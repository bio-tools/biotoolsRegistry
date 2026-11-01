"""Shared read operations. Presentation and write authorization belong to callers."""
from dataclasses import dataclass, field
from time import perf_counter

from django.conf import settings
from django.db.models import prefetch_related_objects

from elixir.models import Resource
from elixir.search import construct_es_query, es
from elixir.advanced_filters import SOURCE_FIELDS, filter_clauses, score_definitions


SEARCH_FACETS = {
    'topic': ['topic.term.raw'], 'operation': ['function.operation.term.raw'],
    'input': ['function.input.data.term.keyword', 'function.input.format.term.keyword'],
    'output': ['function.output.data.term.keyword', 'function.output.format.term.keyword'],
    'toolType': ['toolType.raw'], 'language': ['language.raw'],
    'accessibility': ['accessibility.keyword'], 'cost': ['cost.raw'],
    'license': ['license.raw'], 'credit': ['credit.name.keyword'],
    'collectionID': ['collectionID.raw'], 'name': ['name.raw'],
}
SUMMARY_FIELDS = ['biotoolsID', 'name', 'description', 'toolType', 'topic.term',
                  'function.operation.term', 'additionDate', 'lastUpdate']
FACET_LIMIT = 30


def workspace_aggregations():
    aggregations = {}
    for name, fields in SEARCH_FACETS.items():
        terms = {'size': FACET_LIMIT + 1, 'order': {'_key': 'asc'}}
        if len(fields) == 1:
            terms['field'] = fields[0]
        else:
            # Count each matching resource once when data and format share a term.
            terms['script'] = {
                'source': 'def values = new HashSet(); for (def f : params.fields) '
                          '{ if (doc.containsKey(f)) { values.addAll(doc[f]); }} return values;',
                'params': {'fields': fields},
            }
        aggregations[name] = {'terms': terms}
    return aggregations


class ToolNotFound(LookupError):
    """No current visible resource has this identifier."""


class InvalidQuery(ValueError):
    """Query inputs cannot be interpreted by the existing query builder."""


class SearchPageNotFound(LookupError):
    """Matches exist, but the requested page contains no results."""


def public_domains():
    """Same directory source as /api/d/all, with a public-only projection."""
    fields = ['domain', 'title', 'sub_title', 'description', 'tag', 'collection', 'resources.name', 'resources.biotoolsID']
    result = es.search(index=getattr(settings, 'ELASTIC_SEARCH_DOMAIN_INDEX', 'domains'),
                       body={'size': 10000, 'track_total_hits': True, '_source': fields, 'query': {'match_all': {}}},
                       request_timeout=10)
    hits = result['hits']
    if result.get('timed_out') or result.get('_shards', {}).get('failed') or hits['total']['value'] != len(hits['hits']):
        raise TimeoutError('Incomplete domain directory')
    return sorted([hit['_source'] for hit in hits['hits']], key=lambda entry: entry['domain'].casefold())


@dataclass
class ToolSearchResult:
    items: list
    count: int
    page: int
    per_page: int
    backend_requests: int
    elapsed_ms: float
    facets: dict = field(default_factory=dict)


def get_tool(identifier):
    """Return the visible ORM resource; private edit permission does not hide reads."""
    try:
        return Resource.objects.filter(visibility=1).get(
            biotoolsID__iexact=identifier.removeprefix('biotools:'))
    except Resource.DoesNotExist as exc:
        raise ToolNotFound(identifier) from exc


def get_tool_detail(identifier):
    """Reuse visibility policy and batch the relations rendered by the HTML page."""
    tool = get_tool(identifier)
    prefetch_related_objects(
        [tool], 'owner', 'version', 'topic', 'toolType', 'language', 'operatingSystem',
        'function__operation', 'function__input__data', 'function__input__format',
        'function__output__data', 'function__output__format',
        'publication__type', 'publication__metadata__authors', 'credit__typeRole',
        'documentation__type', 'download', 'link__type', 'relation', 'otherID',
        'collectionID', 'elixirPlatform', 'elixirNode', 'elixirCommunity',
    )
    return tool


def search_tools(query_params, *, page, per_page, workspace=False, advanced=None, comparison_fields=()):
    """Search with q/filter/sort/ord/domain parameters and explicit pagination.

    Accepts a string-valued mapping or QueryDict, not a request. The existing
    builder retains its size cap and malformed-input behavior. Elasticsearch
    errors propagate; callers must not turn backend failures into empty results.
    """
    started = perf_counter()
    parameters = query_params.copy()
    parameters['page'] = page
    parameters['per_page'] = per_page
    try:
        page = int(page)
        body = construct_es_query(parameters)
    except (ValueError, TypeError) as exc:
        raise InvalidQuery(str(exc)) from exc

    requests = 1
    domain = parameters.get('domain')
    if domain:
        domains = es.search(index=getattr(settings, 'ELASTIC_SEARCH_DOMAIN_INDEX', 'domains'), body={
            'size': 10000,
            'query': {'bool': {'must': [
                {'match_phrase': {'domain.raw': {'query': domain}}}
            ]}},
        })
        requests += 1
        if workspace and (domains.get('timed_out') or domains.get('_shards', {}).get('failed', 0)):
            raise TimeoutError('Domain membership search did not return complete results')
        if domains['hits']['total']['value'] > 0:
            resources = domains['hits']['hits'][0]['_source']['resources']
            ids = {resource['biotoolsID'] for resource in resources}
            body['query']['bool']['must'].append(
                {'terms': {'biotoolsID': [identifier.lower() for identifier in ids]}})
        elif workspace:
            body['query']['bool']['must'].append({'match_none': {}})

    options = {}
    if workspace:
        body['_source'] = SUMMARY_FIELDS + SOURCE_FIELDS + [score['field'] for score in score_definitions()]
        body['_source'] += list(comparison_fields)
        body['query']['bool']['filter'] = filter_clauses(advanced or [])
        body['aggs'] = workspace_aggregations()
        body['sort'] = [body['sort'], {'biotoolsID': {'order': 'asc'}}]
        body['timeout'] = '5s'
        options = {'request_timeout': 8, 'allow_partial_search_results': False}
    result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body=body, **options)
    if workspace and (result.get('timed_out') or result.get('_shards', {}).get('failed', 0)):
        raise TimeoutError('Search did not return complete results')
    count = result['hits']['total']['value']
    items = [hit['_source'] for hit in result['hits']['hits']]
    if not items and count > 0:
        raise SearchPageNotFound('Invalid page. That page contains no results.')
    return ToolSearchResult(items, count, page, body['size'], requests,
                            (perf_counter() - started) * 1000, result.get('aggregations', {}))
