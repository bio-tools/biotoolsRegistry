from urllib.parse import quote

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.views.decorators.cache import never_cache

from elixir.queries import get_tool_detail, ToolNotFound
from elixir.serializers import ResourceSerializer
from elixir.resource_ui import SchemaUnavailable, public_fields, resource_descriptor
from elixirapp.resource_editor import can_edit


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
    badges = [(label, url) for mask, label, url in (
        (1, 'ELIXIR Deposition Database', 'https://elixir-europe.org/platforms/data/elixir-deposition-databases'),
        (2, 'ELIXIR Core Data Resource', 'https://elixir-europe.org/platforms/data/core-data-resources'),
        (4, 'Recommended Interoperability Resource', 'https://elixir-europe.org/platforms/interoperability/rir-selection'),
    ) if 0 < tool.elixir_badge < 8 and tool.elixir_badge & mask]
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
        'metadata.title', 'metadata.authors.name', 'metadata.journal', 'metadata.date', 'metadata.abstract')}
    publications = [{'record': record, 'extra': public_fields(value, fields['publication']['item'], handled=publication_paths)}
                    for record, value in zip(tool.publication.all(), data.get('publication') or [])]
    return render(request, 'html/tool_detail.html', {
        'tool': tool, 'edit_url': path + '/edit',
        'canonical_url': request.build_absolute_uri(path),
        'api_url': '/api/t' + path, 'badges': badges, 'can_edit': can_edit(request.user, tool),
        'schema_fields': fields, 'schema_revision': descriptor['revision'],
        'functions': functions, 'publications': publications,
        'metadata_sections': [node for node in metadata if 'entries' in node],
        'metadata_facts': [node for node in metadata if 'entries' not in node],
    })
