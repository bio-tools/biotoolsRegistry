"""Publication-based suggestions for the editor; never writes a resource."""
import ipaddress
import json
import re
import socket
from threading import BoundedSemaphore
from time import monotonic
from urllib.parse import unquote, urlsplit

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from elixir.resource_ui import SchemaUnavailable, resource_descriptor
from elixirapp.browser_auth import browser_login_required
from elixirapp.github_bridge import MAX_RESPONSE, suggestions
from elixirapp.resource_editor import existing


slots = BoundedSemaphore(2)


def publication(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 512:
        raise ValueError('Enter a DOI, PMID, PMCID, or a supported publication link.')
    value = value.strip()
    if value.lower().startswith('https://'):
        url = urlsplit(value)
        if url.username or url.password or url.port not in (None, 443) or url.query or url.fragment:
            raise ValueError('Use a publication identifier or its canonical link.')
        host = (url.hostname or '').lower()
        path = unquote(url.path).strip('/')
        if host in ('doi.org', 'dx.doi.org', 'www.doi.org'):
            value = path
        elif host == 'pubmed.ncbi.nlm.nih.gov':
            value = path
        elif host in ('pmc.ncbi.nlm.nih.gov', 'www.ncbi.nlm.nih.gov', 'europepmc.org'):
            match = re.fullmatch(r'(?:pmc/)?articles/(PMC[0-9]+)', path, re.I)
            if not match:
                raise ValueError('Use a DOI, PubMed, PMC, or Europe PMC article link.')
            value = match.group(1)
        else:
            raise ValueError('Use a DOI, PubMed, PMC, or Europe PMC article link.')
    value = re.sub(r'^(?:doi|pmid|pmcid):\s*', '', value, flags=re.I)
    if re.fullmatch(r'[0-9]{1,12}', value):
        return {'pmid': value}
    if re.fullmatch(r'PMC[0-9]{1,12}', value, re.I):
        return {'pmcid': value.upper()}
    if re.fullmatch(r'10\.[0-9]{4,9}/[^\s?#]{1,200}', value, re.I):
        return {'doi': value}
    raise ValueError('Enter a valid DOI, PMID, or PMCID.')


def webpage(value):
    if value in (None, ''):
        return None
    if not isinstance(value, str) or len(value) > 2000 or any(char.isspace() for char in value):
        raise ValueError('Use a public HTTPS webpage or document URL.')
    url = urlsplit(value)
    host = (url.hostname or '').lower().rstrip('.')
    if url.scheme != 'https' or not host or '.' not in host or url.username or url.password or url.port not in (None, 443) or url.fragment:
        raise ValueError('Use a public HTTPS webpage or document URL.')
    if host.endswith(('.local', '.localhost', '.localdomain', '.internal')):
        raise ValueError('Use a public HTTPS webpage or document URL.')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        try:
            socket.inet_aton(host)
        except OSError:
            return value
    raise ValueError('Use a public HTTPS webpage or document URL.')


def fetch(payload):
    started = monotonic()
    with requests.post(settings.PUB2TOOLS_URL, json=payload, timeout=(5, 180),
                       stream=True, allow_redirects=False) as response:
        if response.status_code != 200:
            raise ValueError('Pub2Tools request failed.')
        content = bytearray()
        for chunk in response.iter_content(8192):
            content.extend(chunk)
            if len(content) > MAX_RESPONSE or monotonic() - started > 180:
                raise ValueError('Pub2Tools response exceeded its size or time limit.')
    result = json.loads(content)
    if not isinstance(result, dict) or result.get('success') is not True or not isinstance(result.get('tool'), dict):
        raise ValueError('Pub2Tools returned an invalid result.')
    return result['tool']


@browser_login_required
@require_POST
@never_cache
def import_publication(request):
    if not settings.PUB2TOOLS_URL:
        return JsonResponse({'detail': 'Publication import is disabled. You can still edit manually.'}, status=503)
    if request.content_type != 'application/json':
        return JsonResponse({'detail': 'Send a JSON request.'}, status=415)
    if len(request.body) > 4096:
        return JsonResponse({'detail': 'Import request is too large.'}, status=413)
    try:
        body = json.loads(request.body)
        if not isinstance(body, dict) or set(body) - {'publication', 'documentUrl', 'biotoolsID', 'schemaRevision'}:
            raise ValueError('Invalid import request.')
        identifier = body.get('biotoolsID')
        if identifier is not None and (not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9.~_-]{1,100}', identifier)):
            raise ValueError('Invalid tool identifier.')
        pub = publication(body.get('publication'))
        doc = webpage(body.get('documentUrl'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'detail': 'Enter a valid DOI, PMID, PMCID or publication link and an optional public HTTPS document URL.'}, status=400)
    if identifier:
        existing(identifier, request.user)
    try:
        descriptor = resource_descriptor()
    except SchemaUnavailable:
        return JsonResponse({'detail': 'Schema metadata is unavailable.'}, status=503)
    if body.get('schemaRevision') != descriptor['revision']:
        return JsonResponse({'detail': 'The resource schema changed. Export your draft before reloading.'}, status=409)
    if not slots.acquire(blocking=False):
        return JsonResponse({'detail': 'Publication import is busy. Try again shortly.'}, status=429)
    try:
        if not cache.add('pub2tools-import:' + str(request.user.pk), True, timeout=60):
            return JsonResponse({'detail': 'Wait one minute before requesting more suggestions.'}, status=429)
        payload = {'publicationIds': [pub]}
        if doc:
            payload['webpageUrls'] = [doc]
        raw = fetch(payload)
        accepted, rejected = suggestions(raw, descriptor)
        return JsonResponse({'suggestions': accepted, 'rejected': rejected, 'raw': raw,
                             'schemaRevision': descriptor['revision']})
    except requests.Timeout:
        return JsonResponse({'detail': 'Publication import timed out. Your draft is unchanged.'}, status=504)
    except (requests.RequestException, ValueError, RecursionError):
        return JsonResponse({'detail': 'Pub2Tools is unavailable or returned an invalid response. Your draft is unchanged.'}, status=502)
    finally:
        slots.release()
