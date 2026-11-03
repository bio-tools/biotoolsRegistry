"""Render an unsaved editor draft with the public tool-detail template."""
import json
from types import SimpleNamespace

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from elixir.resource_ui import SchemaUnavailable, public_fields, resource_descriptor
from elixirapp.browser_auth import browser_login_required
from elixirapp.resource_editor import existing
from elixirapp.tool_detail import elixir_badges, publication_identifiers


class PreviewList(list):
    def all(self):
        return self


class PreviewObject(SimpleNamespace):
    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        return None


def shape_matches(value, field):
    if value is None:
        return True
    kind = field['kind']
    if kind == 'object':
        return isinstance(value, dict) and all(
            name not in field.get('fields', {}) or shape_matches(item, field['fields'][name])
            for name, item in value.items()
        )
    if kind == 'array':
        return isinstance(value, list) and all(shape_matches(item, field['item']) for item in value)
    return {'string': isinstance(value, str), 'boolean': isinstance(value, bool),
            'number': type(value) in (int, float)}.get(kind, False)


def public_values(value, field):
    if isinstance(value, dict) and field['kind'] == 'object':
        return {name: public_values(item, child) for name, item in value.items()
                if (child := field.get('fields', {}).get(name)) and child.get('public')}
    if isinstance(value, list) and field['kind'] == 'array':
        return [public_values(item, field['item']) for item in value]
    return value


def view_value(value, name=''):
    if isinstance(value, dict):
        return PreviewObject(**{key: view_value(item, key) for key, item in value.items()})
    if isinstance(value, list):
        return PreviewList(view_value(item, name) if isinstance(item, (dict, list))
                           else PreviewObject(name=item, type=item, version=item) for item in value)
    if name in {'additionDate', 'lastUpdate', 'date'} and isinstance(value, str):
        try:
            return parse_datetime(value) or parse_date(value)
        except ValueError:
            return None
    return value


@browser_login_required
@require_POST
@never_cache
def preview(request, identifier=None):
    if request.content_type != 'application/json':
        return JsonResponse({'detail': 'Send a JSON resource.'}, status=415)
    if len(request.body) > 1024 * 1024:
        return JsonResponse({'detail': 'Draft is too large to preview.'}, status=413)
    try:
        body = json.loads(request.body)
        if not isinstance(body, dict) or set(body) != {'resource', 'schemaRevision'} or not isinstance(body['resource'], dict):
            raise ValueError
    except (ValueError, UnicodeDecodeError, RecursionError):
        return JsonResponse({'detail': 'Send a valid draft and schema revision.'}, status=400)
    if identifier:
        existing(identifier, request.user)
    try:
        descriptor = resource_descriptor()
    except SchemaUnavailable:
        return JsonResponse({'detail': 'Schema metadata is unavailable.'}, status=503)
    if body['schemaRevision'] != descriptor['revision']:
        return JsonResponse({'detail': 'The resource schema changed. Export your draft before reloading.'}, status=409)
    data, fields = body['resource'], descriptor['contract']['fields']
    if not shape_matches(data, descriptor['contract']):
        return JsonResponse({'detail': 'The draft contains incompatible field values.'}, status=400)
    data = public_values(data, descriptor['contract'])

    tool = view_value(data)
    tool.biotoolsID = data.get('biotoolsID') or 'draft'
    tool.owner = PreviewObject(username=data.get('owner') or request.user.username)
    specialized = {'name', 'description', 'homepage', 'biotoolsID', 'biotoolsCURIE', 'topic', 'function', 'publication',
                   'owner', 'additionDate', 'lastUpdate', 'confidence_flag', 'elixir_badge'}
    if any(not fields.get(name, {}).get('public') for name in specialized):
        return JsonResponse({'detail': 'Public record schema is unavailable.'}, status=503)
    metadata = public_fields(data, descriptor['contract'], handled=specialized)
    concept_paths = {f'function.{parent}.{leaf}' for parent in ('operation', 'input.data', 'input.format', 'output.data', 'output.format')
                     for leaf in ('uri', 'term')}
    functions = [{'record': view_value(item), 'extra': public_fields(item, fields['function']['item'], handled=concept_paths)}
                 for item in data.get('function') or [] if isinstance(item, dict)]
    publication_paths = {'publication.' + path for path in ('doi', 'pmid', 'pmcid', 'type', 'version', 'note',
        'metadata.title', 'metadata.authors.name', 'metadata.journal', 'metadata.date', 'metadata.abstract', 'metadata.citationCount')}
    publications = []
    for item in data.get('publication') or []:
        if isinstance(item, dict):
            record = view_value(item)
            publications.append({'record': record, 'identifiers': publication_identifiers(record),
                                 'extra': public_fields(item, fields['publication']['item'], handled=publication_paths)})
    return render(request, 'html/tool_detail.html', {
        'tool': tool, 'schema_fields': fields, 'schema_revision': descriptor['revision'], 'preview_mode': True,
        'canonical_url': '', 'api_url': '', 'can_edit': False, 'badges': elixir_badges(data.get('elixir_badge')),
        'functions': functions, 'publications': publications, 'has_publication_metrics': False, 'has_publication_doi': False,
        'rrids': [item['value'] for item in data.get('otherID') or [] if isinstance(item, dict)
                  and (item.get('type') or '').lower() == 'rrid' and item.get('value')]
                 if fields.get('otherID', {}).get('public') else [],
        'metadata_sections': [node for node in metadata if 'entries' in node],
        'metadata_facts': [node for node in metadata if 'entries' not in node],
    })
