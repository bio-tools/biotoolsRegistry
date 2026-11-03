"""Frontend-only search contract; public REST representations remain unchanged."""
import logging
import re
from math import ceil

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_safe
from django.views.decorators.cache import never_cache
from django.db import DatabaseError
from elasticsearch.exceptions import TransportError

from elixir.queries import FACET_LIMIT, InvalidQuery, SearchPageNotFound, search_tools
from elixir.models import Credit, CollectionID, Domain, Resource
from elixir.advanced_filters import filter_values, parse_filters, score_metadata
from elixir.edam_lookup import EdamUnavailable, EdamVocabulary
from elixir.resource_ui import SchemaUnavailable, resource_descriptor, search_metadata, public_fields
from elixir.resource_schema import flatten
from elixir.search_settings import search_struct


logger = logging.getLogger(__name__)
FILTERS = tuple(search_struct) + ('domain',)
SORTS = {'lastUpdate': 'Updated', 'additionDate': 'Added', 'name': 'Name',
         'score': 'Relevance', 'citationCount': 'Citation count', 'citationDate': 'Publication date'}
PAGE_SIZES = (10, 25, 50, 100)
MAX_WINDOW = 10000


def filter_groups(descriptor):
    fields = flatten(descriptor['contract'])
    groups = {}

    def group(path):
        if path not in groups:
            groups[path] = {'id': path, 'label': fields[path]['label'] if path else 'Tool details',
                            'keys': [], 'children': []}
            parent = path.rpartition('.')[0]
            if parent:
                group(parent)['children'].append(groups[path])
        return groups[path]

    for key in search_struct:
        paths = [path.split('.') for path in search_struct.get(key, {}).get('search_field', [])]
        common = []
        for parts in zip(*paths):
            if len(set(parts)) != 1:
                break
            common.append(parts[0])
        # Shared input/output aliases stay at their common schema ancestor.
        while common:
            field = fields.get('.'.join(common), {})
            if field.get('item', field).get('fields'):
                break
            common.pop()
        group('.'.join(common))['keys'].append(key)
    return [node for path, node in groups.items() if '.' not in path] + [
        {'id': 'registry', 'label': 'Registry', 'keys': ['domain'], 'children': []}]


class SearchInputError(ValueError):
    def __init__(self, field, message):
        self.field = field
        super().__init__(message)


def parse_search(parameters):
    allowed = {'q', 'sort', 'ord', 'page', 'per_page', 'advanced', 'view', *FILTERS}
    for key, values in parameters.lists():
        if key not in allowed:
            raise SearchInputError(key, 'Unsupported search parameter.')
        # Match the public API's characterized QueryDict last-value semantics.
    state = {'q': parameters.get('q', '').strip(), 'sort': parameters.get('sort', 'lastUpdate'),
             'ord': parameters.get('ord', 'desc'), 'page': 1, 'per_page': 50,
             'view': parameters.get('view', 'cards')}
    if state['view'] not in ('cards', 'table'):
        raise SearchInputError('view', 'Choose cards or table.')
    for key in ('page', 'per_page'):
        value = parameters.get(key, str(state[key]))
        if not re.fullmatch(r'[0-9]{1,5}', value) or int(value) < 1:
            raise SearchInputError(key, 'Use a positive whole number.')
        state[key] = int(value)
    if state['per_page'] not in PAGE_SIZES:
        raise SearchInputError('per_page', 'Choose 10, 25, 50 or 100 results per page.')
    if state['page'] * state['per_page'] > MAX_WINDOW:
        raise SearchInputError('page', 'Narrow the search to browse beyond 10,000 results.')
    if state['sort'] not in SORTS or state['ord'] not in ('asc', 'desc'):
        raise SearchInputError('sort', 'Choose a supported sort and direction.')
    for key in ('q', *FILTERS):
        value = parameters.get(key, '').strip()
        if len(value) > 256 or re.search(r'[\x00-\x1f\x7f\\]', value):
            raise SearchInputError(key, 'Use at most 256 characters without control characters or backslashes.')
        if value and key != 'domain' and not re.search(r'\w', value):
            raise SearchInputError(key, 'Include a searchable word or identifier.')
        if value:
            state[key] = value
    try:
        state['advanced'] = parse_filters(parameters.get('advanced', '[]'))
    except ValueError as exc:
        raise SearchInputError('advanced', str(exc)) from exc
    return state


def summary(item, canonical=False, descriptor=None):
    def terms(values):
        return list(dict.fromkeys(value['term'] for value in values if value.get('term')))[:5]
    identifier = item['biotoolsID']
    result = {
        'id': identifier, 'name': item['name'], 'description': item.get('description', '')[:400],
        'url': '/' + identifier if canonical else reverse('html:tool-detail', urlconf='elixirapp.html_urls', kwargs={'identifier': identifier}),
        'toolTypes': item.get('toolType', [])[:4], 'topics': terms(item.get('topic', [])),
        'operations': terms([operation for function in item.get('function', [])
                             for operation in function.get('operation', [])]),
        'added': (item.get('additionDate') or '')[:10], 'updated': (item.get('lastUpdate') or '')[:10],
        'filterValues': filter_values(item),
    }
    if descriptor:
        def text(node):
            if 'values' in node:
                return ', '.join(str(value['label']) for value in node['values'])
            return '; '.join(', '.join(child['label'] + ': ' + text(child) for child in entry)
                             for entry in node.get('entries', []))
        nodes = public_fields(item, descriptor['contract'])
        result['comparison'] = {node['name']: text(node) for node in nodes}
        for node in nodes:
            if node['name'] in ('additionDate', 'lastUpdate'):
                result['comparison'][node['name']] = result['added' if node['name'] == 'additionDate' else 'updated']
            if node['name'] == 'function':
                for entry in node.get('entries', []):
                    for child in entry:
                        key = child['path']
                        value = text(child)
                        result['comparison'][key] = '; '.join(filter(None, (result['comparison'].get(key), value)))
    return result


@require_safe
@never_cache
def page(request):
    try:
        descriptor = resource_descriptor()
        metadata = search_metadata(descriptor, search_struct)
        metadata['domain'] = {'label': 'Domain', 'choices': []}
    except SchemaUnavailable:
        return render(request, 'html/schema_unavailable.html', status=503)
    comparison = {name: field['label'] for name, field in descriptor['contract']['fields'].items() if field['public']}
    function = descriptor['contract']['fields'].get('function', {})
    if function.get('public'):
        comparison.update({field['path']: function['label'] + ' › ' + field['label']
                           for field in function.get('item', {}).get('fields', {}).values() if field['public']})
    config = {'endpoint': reverse('canonical-search-data') if getattr(request, 'canonical', False) else reverse('html:search-data'),
              'filters': {name: metadata[name]['label'] for name in FILTERS},
              'filterChoices': {name: metadata[name]['choices'] for name in FILTERS},
              'filterGroups': filter_groups(descriptor),
              'schemaRevision': descriptor['revision'], 'sorts': SORTS,
              'pageSizes': PAGE_SIZES, 'maxWindow': MAX_WINDOW, 'scores': score_metadata(),
              'comparisonFields': comparison,
              'optionsEndpoint': reverse('canonical-search-options') if getattr(request, 'canonical', False) else reverse('html:search-options'),
              'edamEndpoint': reverse('canonical-edam-lookup') if getattr(request, 'canonical', False) else reverse('html:edam-lookup')}
    body, status, elapsed = search_payload(request)
    if request.GET.get('view') == 'table':
        for item in body.get('items', []):
            item['comparisonCells'] = [item.get('comparison', {}).get(name, '') for name in config['comparisonFields'] if name != 'name']
    query = request.GET.copy()
    def page_url(number):
        parameters = query.copy()
        parameters['page'] = number
        return request.path + '?' + parameters.urlencode()
    pagination = body.get('pagination', {})
    fields = [{'key': key, **metadata[key], 'value': request.GET.get(key, '')} for key in FILTERS]
    by_key = {field['key']: field for field in fields}

    def native_group(node):
        children = [native_group(child) for child in node['children']]
        return {**node, 'fields': [by_key[key] for key in node['keys']], 'children': children,
                'active': sum(bool(by_key[key]['value']) for key in node['keys']) + sum(child['active'] for child in children)}

    response = render(request, 'html/search.html', {
        'search_config': config, 'search_result': body, 'search_fields': fields,
        'search_groups': [native_group(node) for node in config['filterGroups']],
        'search_values': request.GET, 'search_path': request.path,
        'unknown_parameters': [(key, value) for key, value in request.GET.items()
                               if key not in {'q', 'sort', 'ord', 'page', 'per_page', 'advanced', 'view', *FILTERS}],
        'previous_url': page_url(pagination['previous']) if pagination.get('previous') else '',
        'next_url': page_url(pagination['next']) if pagination.get('next') else '',
        'first_url': page_url(1),
    }, status=status)
    if elapsed is not None:
        response['Server-Timing'] = f'search;dur={elapsed:.2f}'
    return response


@require_safe
def canonical_page(request):
    if request.path != '/t':
        query = request.META.get('QUERY_STRING', '')
        return HttpResponseRedirect('/t' + ('?' + query if query else ''))
    return page(request)


def search_payload(request):
    try:
        state = parse_search(request.GET)
        descriptor = resource_descriptor() if state['view'] == 'table' else None
        comparison_fields = [name for name, field in descriptor['contract']['fields'].items() if field['public']] if descriptor else []
        ontology = [condition for condition in state['advanced'] if condition['type'] == 'ontology']
        if ontology:
            vocabulary = EdamVocabulary('topic')
            try:
                for condition in ontology:
                    vocabulary.resolve(condition['values'])
            except ValueError as exc:
                raise SearchInputError('advanced', str(exc)) from exc
        result = search_tools(state, page=state['page'], per_page=state['per_page'], workspace=True,
                              advanced=state['advanced'], comparison_fields=comparison_fields)
        pages = max(1, ceil(min(result.count, MAX_WINDOW) / result.per_page))
        if result.page > pages:
            raise SearchPageNotFound()
        facets = {name: {
            'values': [{'value': bucket['key'], 'count': bucket['doc_count']}
                       for bucket in aggregation['buckets'][:FACET_LIMIT]],
            'truncated': len(aggregation['buckets']) > FACET_LIMIT,
        } for name, aggregation in result.facets.items()}
        body = {
            'items': [summary(item, getattr(request, 'canonical', False), descriptor) for item in result.items], 'count': result.count,
            'facets': facets, 'state': state,
            'scores': score_metadata(),
            'candidates': {'scope': 'candidate', 'size': len(result.items), 'limit': max(PAGE_SIZES),
                           'complete': result.page == 1 and len(result.items) == result.count},
            'pagination': {'page': result.page, 'perPage': result.per_page, 'pages': pages,
                           'previous': result.page - 1 if result.page > 1 else None,
                           'next': result.page + 1 if result.page < pages else None,
                           'limited': result.count > MAX_WINDOW},
        }
        return body, 200, result.elapsed_ms
    except SearchInputError as exc:
        return {'error': {'code': 'invalid_search', 'field': exc.field, 'message': str(exc)}}, 400, None
    except InvalidQuery:
        return {'error': {'code': 'invalid_search', 'message': 'The search terms could not be parsed.'}}, 400, None
    except SearchPageNotFound:
        return {'error': {'code': 'invalid_page', 'message': 'This page has no results. Return to page 1.'}}, 400, None
    except (TransportError, TimeoutError, EdamUnavailable, SchemaUnavailable):
        logger.exception('Workspace search unavailable')
        return {'error': {'code': 'search_unavailable', 'message': 'Search is temporarily unavailable. Please retry.'}}, 503, None


@require_safe
@never_cache
def data(request):
    body, status, elapsed = search_payload(request)
    response = JsonResponse(body, status=status)
    if elapsed is not None:
        response['Server-Timing'] = f'search;dur={elapsed:.2f}'
    return response


@require_safe
@never_cache
def options(request):
    field = request.GET.get('field', '')
    query = request.GET.get('q', '').strip()
    if field not in ('domain', 'creditName', 'collectionID', 'name') or len(query) > 80 or re.search(r'[\x00-\x1f\x7f]', query):
        return JsonResponse({'error': 'Invalid lookup.'}, status=400)
    try:
        if field == 'domain':
            values = [{'value': name, 'label': title or name} for name, title in
                      Domain.objects.filter(visibility=1, is_private=False).values_list('name', 'title').distinct().order_by('name')]
            return JsonResponse({'items': values})
        if len(query) < 2:
            return JsonResponse({'items': []})
        model = {'creditName': Credit, 'collectionID': CollectionID, 'name': Resource}[field]
        visibility = {'visibility': 1} if field == 'name' else {'resource__visibility': 1}
        names = model.objects.filter(**visibility, name__icontains=query).exclude(name='').values_list('name', flat=True).distinct().order_by('name')[:21]
        values = list(names)
        return JsonResponse({'items': [{'value': name, 'label': name} for name in values[:20]], 'more': len(values) > 20})
    except (DatabaseError, TransportError, TimeoutError):
        logger.exception('Search options unavailable')
        return JsonResponse({'error': 'Options are temporarily unavailable.'}, status=503)
