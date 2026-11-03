import re
from urllib.parse import quote, urlencode, urlsplit

from django import template
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.html import conditional_escape, format_html
from django.urls import reverse


register = template.Library()
validate_url = URLValidator(schemes=['http', 'https', 'ftp', 'ftps'])


@register.simple_tag
def field_icon(kind):
    return kind if kind in {'string', 'number', 'boolean', 'array', 'object'} else 'object'


@register.simple_tag
def external_link(url, label=None, title=None):
    """Stored metadata is untrusted, including URLs that predate API validation."""
    label = label or url or ''
    try:
        validate_url(url or '')
    except ValidationError:
        return conditional_escape(label)
    if title:
        return format_html('<a href="{}" rel="noopener noreferrer" title="{}">{}</a>', url, title, label)
    return format_html('<a href="{}" rel="noopener noreferrer">{}</a>', url, label)


@register.simple_tag
def search_url(field, value):
    return '/t?' + urlencode({field: '"' + str(value) + '"'})


@register.simple_tag
def workflow_annotation_link(url, edam_uri=None):
    if url:
        try:
            parsed = urlsplit(url)
            match = re.fullmatch(r'/(?:tool/)?(?:biotools:)?([A-Za-z0-9.~_-]{1,100})(?:/version/[^/]+)?/?', parsed.path)
            if parsed.scheme in ('http', 'https') and parsed.hostname in ('bio.tools', 'www.bio.tools') and match:
                return format_html('<a href="/{}" title="Open this tool’s bio.tools entry">bio.tools entry</a>', match.group(1))
            if parsed.hostname == 'edamontology.org':
                return external_link(url, 'EDAM concept', 'Open this term in the EDAM ontology')
        except ValueError:
            pass
        return external_link(url, 'Open annotation')
    return external_link(edam_uri, 'EDAM concept', 'Open this term in the EDAM ontology') if edam_uri else ''


@register.inclusion_tag('html/detail/term.html')
def edam_term(term, field):
    uri = term.uri if term else ''
    match = re.fullmatch(r'https?://edamontology.org/((?:topic|operation|data|format)_\d+)', uri or '')
    identifier = match.group(1) if match else ''
    return {'label': (term.term if term else '') or identifier or uri,
            'uri': uri, 'identifier': identifier,
            'search': search_url(field, identifier) if identifier else ''}


@register.simple_tag
def identifier_link(value, kind):
    if not value:
        return ''
    bases = {'doi': 'https://doi.org/', 'pmid': 'https://pubmed.ncbi.nlm.nih.gov/',
             'pmcid': 'https://europepmc.org/article/PMC/', 'rrid': 'https://scicrunch.org/resolver/',
             'cpe': 'https://cpe-link.org/', 'gridid': 'https://www.grid.ac/institutes/',
             'rorid': 'https://ror.org/', 'fundrefid': 'https://doi.org/'}
    kind = (kind or '').lower()
    if kind not in bases:
        return conditional_escape(value)
    identifier = str(value)
    if kind == 'doi':
        for prefix in ('https://doi.org/', 'http://doi.org/', 'doi:'):
            identifier = identifier.removeprefix(prefix)
    elif kind == 'pmcid':
        identifier = identifier.removeprefix('PMC')
    elif kind == 'rorid':
        identifier = identifier.removeprefix('https://ror.org/')
    return external_link(bases[kind] + quote(identifier, safe='/'), value)


@register.simple_tag
def community_url(name):
    slugs = {'3D-BioInfo': '3d-bioinfo', 'Federated Human Data': 'human-data',
             'Human Copy Number Variation': 'hcnv'}
    return 'https://elixir-europe.org/communities/' + quote(slugs.get(name, (name or '').lower().replace(' ', '-')))


@register.simple_tag(takes_context=True)
def tool_url(context, identifier):
    if not re.fullmatch(r'[A-Za-z0-9.~_-]{1,100}', identifier or ''):
        return ''
    if getattr(context.get('request'), 'canonical', False):
        return '/' + identifier
    return reverse('html:tool-detail', kwargs={'identifier': identifier}, urlconf='elixirapp.html_urls')


@register.simple_tag
def license_link(license, label=None):
    if license in ('Freeware', 'Proprietary', 'Other', 'Not licensed'):
        return conditional_escape(label or license)
    return external_link('https://spdx.org/licenses/' + quote(license, safe=''), label or license)


@register.filter
def obfuscated_email(value):
    return value.replace('@', ' at ')
