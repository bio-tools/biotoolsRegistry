"""Optional, session-protected repository suggestions; never writes a resource."""
import json
import re
from threading import BoundedSemaphore
from time import monotonic
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from rest_framework.exceptions import ValidationError

from elixir.resource_ui import SchemaUnavailable, resource_descriptor
from elixir.serializers import ResourceUpdateSerializer
from elixirapp.browser_auth import browser_login_required
from elixirapp.resource_editor import existing


MAX_RESPONSE = 512 * 1024
# Per worker: at most two provider calls, and one attempt per user per minute.
slots = BoundedSemaphore(2)


def repository(value):
    if not isinstance(value, str) or len(value) > 300 or any(char.isspace() for char in value):
        raise ValueError('Supply a public GitHub repository URL.')
    url = urlsplit(value)
    if url.scheme != 'https' or url.netloc.lower() != 'github.com' or url.query or url.fragment:
        raise ValueError('Use https://github.com/owner/repository without query parameters or fragments.')
    parts = url.path.strip('/').split('/')
    if len(parts) != 2:
        raise ValueError('Use the repository root URL, not a file or branch URL.')
    owner, repo = parts
    repo = repo[:-4] if repo.endswith('.git') else repo
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', owner) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', repo) or repo in {'.', '..'}:
        raise ValueError('Invalid GitHub owner or repository name.')
    return owner, repo


def check_shape(value, field, path):
    if value is None and field.get('nullable'):
        return
    kind = field['kind']
    valid = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str), 'number': type(value) in (int, float),
             'boolean': isinstance(value, bool)}
    if not valid.get(kind):
        raise ValueError(path + ': incompatible value type.')
    if kind == 'object':
        for name, item in value.items():
            child = field['fields'].get(name)
            if not child or not child.get('writable'):
                raise ValueError(path + '.' + name + ': unknown or protected field.')
            check_shape(item, child, path + '.' + name)
    elif kind == 'array':
        if len(value) > 100:
            raise ValueError(path + ': too many suggested items.')
        for item in value:
            check_shape(item, field['item'], path)
    choices = field.get('choices')
    if choices:
        values = value if kind == 'array' else [value]
        if any(item not in [choice['value'] for choice in choices] for item in values):
            raise ValueError(path + ': value is not in the active vocabulary.')


def without_empty(value):
    if isinstance(value, dict):
        return {key: cleaned for key, item in value.items() if (cleaned := without_empty(item)) not in (None, '', [], {})}
    if isinstance(value, list):
        return [cleaned for item in value if (cleaned := without_empty(item)) not in (None, '', [], {})]
    return value


def error_message(error):
    def messages(value):
        if isinstance(value, dict):
            return [message for item in value.values() for message in messages(item)]
        if isinstance(value, (list, tuple)):
            return [message for item in value for message in messages(item)]
        return [str(value)]
    result = []
    for message in messages(error.detail if isinstance(error, ValidationError) else error):
        if message.startswith('Invalid URI: http://edamontology.org/'):
            message = 'EDAM term is not in the current registry ontology: ' + message[len('Invalid URI: '):]
        result.append(message)
    return '; '.join(dict.fromkeys(result))


def suggestions(raw, descriptor):
    serializer = ResourceUpdateSerializer()
    accepted, rejected = {}, []

    def validate(name, value, field):
        check_shape(value, field, name)
        if name == 'otherID' and any(item.get('value', '').lower().startswith('biotools:') for item in value):
            raise ValueError('Registry identifiers are protected.')
        parsed = serializer.fields[name].run_validation(value)
        validator = getattr(serializer, 'validate_' + name, None)
        if validator:
            validator(parsed)

    errors = (ValueError, TypeError, KeyError, AttributeError, ValidationError)
    for name, raw_value in raw.items():
        field = descriptor['contract']['fields'].get(name)
        if not field or not field.get('writable'):
            continue
        if name == 'publication' and isinstance(raw_value, list):
            # Provider enrichment is display-only; the registry owns publication metadata.
            raw_value = [{key: item for key, item in publication.items() if key not in {'metadata', 'title'}}
                         if isinstance(publication, dict) else publication for publication in raw_value]
        value = without_empty(raw_value)
        if value in (None, '', [], {}):
            continue
        try:
            validate(name, value, field)
            accepted[name] = value
        except errors as exc:
            if field['kind'] != 'array' or not isinstance(value, list) or len(value) > 100:
                rejected.append({'path': name, 'reason': error_message(exc)})
                continue
            valid = []
            for item in value:
                try:
                    validate(name, [item], field)
                    valid.append(item)
                except errors as item_error:
                    rejected.append({'path': name, 'reason': error_message(item_error)})
            if valid:
                try:
                    validate(name, valid, field)
                    accepted[name] = valid
                except errors as combined_error:
                    rejected.append({'path': name, 'reason': error_message(combined_error)})
    return accepted, rejected


def fetch(payload):
    started = monotonic()
    with requests.post(settings.GITHUB_BRIDGE_URL, json=payload, timeout=(5, 45),
                       stream=True, allow_redirects=False) as response:
        if response.status_code not in (200, 201):
            raise ValueError('Bridge request failed. Try again later.')
        content = bytearray()
        for chunk in response.iter_content(8192):
            content.extend(chunk)
            if len(content) > MAX_RESPONSE or monotonic() - started > 45:
                raise ValueError('Bridge response exceeded its size or time limit.')
    raw = json.loads(content)
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise ValueError('Bridge returned an invalid metadata object.')
    return raw


@browser_login_required
@require_POST
@never_cache
def import_repository(request):
    if not settings.GITHUB_BRIDGE_URL:
        return JsonResponse({'detail': 'GitHub import is disabled. You can still edit manually.'}, status=503)
    if request.content_type != 'application/json':
        return JsonResponse({'detail': 'Send a JSON request.'}, status=415)
    if len(request.body) > 2048:
        return JsonResponse({'detail': 'Import request is too large.'}, status=413)
    try:
        body = json.loads(request.body)
        if not isinstance(body, dict) or set(body) - {'url', 'biotoolsID', 'schemaRevision'}:
            raise ValueError('Supply a repository URL, optional tool ID and schema revision.')
        owner, repo = repository(body.get('url'))
        identifier = body.get('biotoolsID')
        if identifier is not None and (not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9.~_-]{1,100}', identifier)):
            raise ValueError('Invalid tool identifier.')
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'detail': 'Supply https://github.com/owner/repository and a valid optional tool ID.'}, status=400)
    resource = existing(identifier, request.user) if identifier else None
    try:
        descriptor = resource_descriptor()
    except SchemaUnavailable:
        return JsonResponse({'detail': 'Schema metadata is unavailable.'}, status=503)
    if body.get('schemaRevision') != descriptor['revision']:
        return JsonResponse({'detail': 'The resource schema changed. Export your draft before reloading.'}, status=409)
    if not slots.acquire(blocking=False):
        return JsonResponse({'detail': 'GitHub import is busy. Try again shortly.'}, status=429)
    try:
        if not cache.add('github-import:' + str(request.user.pk), True, timeout=60):
            return JsonResponse({'detail': 'Wait one minute before requesting more suggestions.'}, status=429)
        payload = {'owner': owner, 'repo': repo}
        if resource:
            # The pinned image uses snake_case, unlike upstream's Angular caller.
            payload['biotools_id'] = resource.biotoolsID
        raw = fetch(payload)
        accepted, rejected = suggestions(raw, descriptor)
        return JsonResponse({'suggestions': accepted, 'rejected': rejected, 'raw': raw,
                             'schemaRevision': descriptor['revision']})
    except requests.Timeout:
        return JsonResponse({'detail': 'GitHub import timed out. Your draft is unchanged.'}, status=504)
    except (requests.RequestException, ValueError, RecursionError):
        return JsonResponse({'detail': 'GitHub import returned an unavailable or invalid response. Your draft is unchanged.'}, status=502)
    finally:
        slots.release()
