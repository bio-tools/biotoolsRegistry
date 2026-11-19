"""Private, owner-only resource drafts, separate from public registry records."""
import json
import re
import uuid

from django.db import DatabaseError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from elixir.models import ResourceDraft
from elixirapp.browser_auth import browser_login_required
from elixirapp.resource_editor import existing


def error(message, status):
    return JsonResponse({'detail': message}, status=status)


def identity(request):
    return request.headers.get('X-Biotools-User') == str(request.user.pk)


def summary(draft):
    return {'id': str(draft.pk), 'target': draft.target, 'recordRevision': draft.record_revision,
            'revision': str(draft.revision), 'name': str(draft.resource.get('name') or 'Untitled')[:120],
            'updated': draft.updated.isoformat()}


def payload(request):
    if request.content_type != 'application/json' or len(request.body) > 1024 * 1024:
        raise ValueError('Use a JSON draft no larger than 1 MB.')
    try:
        body = json.loads(request.body)
    except (ValueError, UnicodeDecodeError, RecursionError) as exc:
        raise ValueError('Invalid draft JSON.') from exc
    if not isinstance(body, dict) or set(body) - {'id', 'target', 'recordRevision', 'resource'}:
        raise ValueError('Invalid draft fields.')
    target, record_revision, resource = body.get('target'), body.get('recordRevision'), body.get('resource')
    if not isinstance(target, str) or not re.fullmatch(r'[A-Za-z0-9.~_-]{0,100}', target):
        raise ValueError('Invalid draft target.')
    if not isinstance(record_revision, str) or (target and not re.fullmatch(r'[a-f0-9]{64}', record_revision)) or (not target and record_revision):
        raise ValueError('Invalid record revision.')
    if not isinstance(resource, dict):
        raise ValueError('A draft must contain a JSON record.')
    if target:
        existing(target, request.user)
    return body, target, record_revision, resource


@browser_login_required
@never_cache
@require_http_methods(['GET', 'POST'])
def collection(request):
    if not identity(request):
        return error('The account changed. Keep your work and reload.', 409)
    try:
        if request.method == 'GET':
            target = request.GET.get('target', '')
            offset = request.GET.get('offset', '0')
            if (set(request.GET) - {'target', 'offset'} or len(request.GET.getlist('target')) > 1 or
                    len(request.GET.getlist('offset')) > 1 or not re.fullmatch(r'[A-Za-z0-9.~_-]{0,100}', target) or
                    not offset.isascii() or not offset.isdecimal() or int(offset) > 100000):
                raise ValueError('Invalid draft target.')
            offset = int(offset)
            drafts = list(ResourceDraft.objects.filter(owner=request.user, target=target).order_by('-updated', 'id')[offset:offset + 101])
            return JsonResponse({'items': [summary(draft) for draft in drafts[:100]], 'more': len(drafts) > 100})
        body, target, record_revision, resource = payload(request)
        try:
            identifier = uuid.UUID(body['id']) if 'id' in body else uuid.uuid4()
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError('Invalid draft identifier.') from exc
        draft, created = ResourceDraft.objects.get_or_create(pk=identifier, defaults={'owner': request.user,
            'target': target, 'record_revision': record_revision, 'resource': resource})
        if not created and (draft.owner_id != request.user.pk or draft.target != target or
                            draft.record_revision != record_revision or draft.resource != resource):
            return error('Draft identifier already in use. Keep your work and reload.', 409)
        return JsonResponse(summary(draft), status=201 if created else 200)
    except ValueError as exc:
        return error(str(exc), 400)
    except DatabaseError:
        return error('Drafts are temporarily unavailable. Your work is unchanged.', 503)


@browser_login_required
@never_cache
@require_http_methods(['GET', 'PUT', 'DELETE'])
def detail(request, identifier):
    if not identity(request):
        return error('The account changed. Keep your work and reload.', 409)
    try:
        draft = ResourceDraft.objects.filter(pk=identifier, owner=request.user).first()
        if not draft:
            return error('Draft not found.', 404)
        if request.method == 'GET':
            if draft.target:
                existing(draft.target, request.user)
            return JsonResponse({**summary(draft), 'resource': draft.resource})
        try:
            expected = uuid.UUID(request.headers.get('If-Match', ''))
        except ValueError as exc:
            raise ValueError('Supply the current draft revision.') from exc
        if request.method == 'DELETE':
            deleted, _ = ResourceDraft.objects.filter(pk=identifier, owner=request.user, revision=expected).delete()
            return JsonResponse({'deleted': True}) if deleted else error('The draft changed. Keep your work and reload.', 409)
        _, target, record_revision, resource = payload(request)
        if target != draft.target or record_revision != draft.record_revision:
            raise ValueError('A draft cannot change its target or record revision.')
        revision = uuid.uuid4()
        updated = ResourceDraft.objects.filter(pk=identifier, owner=request.user, revision=expected).update(
            resource=resource, revision=revision, updated=timezone.now())
        if not updated:
            return error('The draft changed. Keep your work and reload.', 409)
        draft.refresh_from_db()
        return JsonResponse(summary(draft))
    except ValueError as exc:
        return error(str(exc), 400)
    except DatabaseError:
        return error('Drafts are temporarily unavailable. Your work is unchanged.', 503)
