import re
from urllib.parse import quote

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.views.decorators.cache import never_cache

from elixir.queries import get_tool_detail, ToolNotFound
from elixir.serializers import ResourceSerializer
from elixir.resource_ui import SchemaUnavailable, public_fields, resource_descriptor
from elixirapp.resource_editor import can_edit


def publication_identifiers(publication):
    doi = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', (publication.doi or '').strip(), flags=re.I)
    pmid = (publication.pmid or '').strip()
    return {
        'doi': doi if re.fullmatch(r'''10\.\d{4,9}/[^\s<>"']+''', doi, flags=re.I) else '',
        'pmid': pmid if re.fullmatch(r'[0-9]+', pmid) else '',
    }


def elixir_badges(mask):
    return [(label, url, logo) for bit, label, url, logo in (
        (1, 'ELIXIR Deposition Database', 'https://elixir-europe.org/platforms/data/elixir-deposition-databases', 'edd.png'),
        (2, 'ELIXIR Core Data Resource', 'https://elixir-europe.org/platforms/data/core-data-resources', 'cdr.png'),
        (4, 'Recommended Interoperability Resource', 'https://elixir-europe.org/platforms/interoperability/rir-selection', 'rir.png'),
    ) if isinstance(mask, int) and 0 < mask < 8 and mask & bit]


@require_safe
@never_cache
def detail(request, identifier):
    try:
        tool = get_tool_detail(identifier)
    except ToolNotFound as exc:
        raise Http404 from exc
    path = '/' + quote(tool.biotoolsID, safe='')
    canonical = getattr(request, 'canonical', False)
    if canonical and request.path != path:
        query = request.META.get('QUERY_STRING', '')
        return HttpResponseRedirect(path + ('?' + query if query else ''))
    badges = elixir_badges(tool.elixir_badge)
    try:
        descriptor = resource_descriptor()
    except SchemaUnavailable:
        return render(request, 'html/schema_unavailable.html', status=503)
    data = ResourceSerializer(tool).data
    fields = descriptor['contract']['fields']
    specialized = {'name', 'description', 'homepage', 'biotoolsID', 'biotoolsCURIE', 'topic', 'function', 'publication',
                   'owner', 'additionDate', 'lastUpdate', 'confidence_flag', 'elixir_badge'}
    if any(not fields[name]['public'] for name in specialized):
        return render(request, 'html/schema_unavailable.html', status=503)
    metadata = public_fields(data, descriptor['contract'], handled=specialized)
    concept_paths = {f'function.{parent}.{leaf}' for parent in ('operation', 'input.data', 'input.format', 'output.data', 'output.format')
                     for leaf in ('uri', 'term')}
    functions = [{'record': record, 'extra': public_fields(value, fields['function']['item'], handled=concept_paths)}
                 for record, value in zip(tool.function.all(), data.get('function') or [])]
    publication_paths = {'publication.' + path for path in ('doi', 'pmid', 'pmcid', 'type', 'version', 'note',
        'metadata.title', 'metadata.authors.name', 'metadata.journal', 'metadata.date', 'metadata.abstract',
        'metadata.citationCount')}
    publications = [{'record': record, 'identifiers': publication_identifiers(record),
                     'extra': public_fields(value, fields['publication']['item'], handled=publication_paths)}
                    for record, value in zip(tool.publication.all(), data.get('publication') or [])]
    return render(request, 'html/tool_detail.html', {
        'tool': tool, 'edit_url': path + '/edit',
        'canonical_url': request.build_absolute_uri(path),
        'api_url': '/api/t' + path, 'badges': badges, 'can_edit': can_edit(request.user, tool),
        'schema_fields': fields, 'schema_revision': descriptor['revision'],
        'functions': functions, 'publications': publications,
        'rrids': [item.value for item in tool.otherID.all() if (item.type or '').lower() == 'rrid']
                 if fields.get('otherID', {}).get('public') else [],
        'has_publication_metrics': any(entry['identifiers']['doi'] or entry['identifiers']['pmid'] for entry in publications),
        'has_publication_doi': any(entry['identifiers']['doi'] for entry in publications),
        'metadata_sections': [node for node in metadata if 'entries' in node],
        'metadata_facts': [node for node in metadata if 'entries' not in node],
    })
