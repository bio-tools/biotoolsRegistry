import hashlib
import json
import logging
import secrets
import uuid

from django.core import signing
from django.db import DatabaseError, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from elixir.edam_lookup import EdamUnavailable
from elixir.models import Function, Resource, WorkflowDesign
from elixir.resource_ui import SchemaUnavailable
from elixir.workflow_drafts import MAX_BYTES, validate_graph
from elixir.workflow_matching import function_details

logger = logging.getLogger(__name__)


def error(code, message, status):
    return JsonResponse({'error': {'code': code, 'message': message}}, status=status)


def parse(request):
    if request.content_type != 'application/json' or len(request.body) > MAX_BYTES:
        raise ValueError('Use JSON within the draft size limit.')
    try:
        value = json.loads(request.body)
    except (ValueError, UnicodeDecodeError, RecursionError) as exc:
        raise ValueError('Invalid JSON.') from exc
    if not isinstance(value, dict):
        raise ValueError('Use a JSON object.')
    return value


def payload(request):
    body = parse(request)
    title = body.get('title')
    if not isinstance(title, str) or not title.strip() or len(title) > 120:
        raise ValueError('Enter a title of at most 120 characters.')
    return title.strip(), validate_graph(body.get('graph'))


def summary(design):
    return {'id': str(design.pk), 'title': design.title, 'revision': str(design.revision),
            'shared': bool(design.share_digest), 'updated': design.updated.isoformat()}


def unresolved_steps(graph, *, lock=False):
    if lock:
        resources, functions = set(), set()
        for step in graph['steps']:
            try:
                ref = signing.loads(step['function']['token'], salt='biotools.workflow-function.v1')
                if type(ref['resource']) is int and type(ref['function']) is int:
                    resources.add(ref['resource'])
                    functions.add(ref['function'])
            except (signing.BadSignature, KeyError, TypeError):
                continue
        list(Resource.objects.select_for_update().filter(pk__in=resources).order_by('pk').values_list('pk', flat=True))
        list(Function.objects.select_for_update().filter(pk__in=functions).order_by('pk').values_list('pk', flat=True))
    unresolved, resolved = set(), {}
    for step in graph['steps']:
        token = step['function']['token']
        if token not in resolved:
            try:
                resolved[token] = function_details(token)
            except ValueError:
                resolved[token] = None
        current = resolved[token]
        if not current or current['resource']['id'] != step['resource']['id'] or current['function']['id'] != step['function']['id']:
            unresolved.add(step['id'])
    return unresolved


def redacted_graph(graph, unresolved):
    steps = []
    for step in graph['steps']:
        if step['id'] not in unresolved:
            steps.append(step)
            continue
        function = step['function']
        steps.append({'id': step['id'], 'note': step['note'],
            'resource': {'id': '', 'name': 'Hidden or unavailable tool', 'revision': {'token': step['resource']['revision']['token']}},
            'function': {'id': function['id'], 'token': function['token'], 'operations': [],
                         'input': [{'id': io['id'], 'data': None, 'formats': []} for io in function['input']],
                         'output': [{'id': io['id'], 'data': None, 'formats': []} for io in function['output']]},
            'schemaRevision': '', 'vocabularyRevisions': {},
            'selection': {'direction': step['selection']['direction'], 'ioId': step['selection']['ioId'],
                          'fingerprint': '', 'evidence': {}}})
    connections = []
    for edge in graph['connections']:
        if edge['from']['step'] in unresolved or edge['to']['step'] in unresolved:
            connections.append({'id': edge['id'], 'from': edge['from'], 'to': edge['to'], 'evidence': 'unknown',
                                'reason': edge['reason'] or 'Annotation unavailable; review required.'})
        else:
            connections.append(edge)
    return {'version': graph['version'], 'steps': steps, 'connections': connections}


def require_owner(request):
    if not request.user.is_authenticated:
        return error('authentication_required', 'Sign in to manage drafts.', 401)
    expected = request.headers.get('X-Biotools-User')
    if expected and expected != str(request.user.pk):
        return error('account_changed', 'The account changed. Download your work before reloading.', 409)
    return None


@never_cache
@require_http_methods(['GET', 'POST'])
def collection(request):
    denied = require_owner(request)
    if denied:
        return denied
    try:
        if request.method == 'GET':
            raw_offset = request.GET.get('offset', '0')
            if set(request.GET) - {'offset'} or len(request.GET.getlist('offset')) > 1 or not raw_offset.isascii() or not raw_offset.isdecimal() or int(raw_offset) > 100000:
                raise ValueError('Invalid draft list offset.')
            offset = int(raw_offset)
            designs = list(WorkflowDesign.objects.filter(owner=request.user).order_by('-updated', 'id')[offset:offset + 101])
            return JsonResponse({'items': [summary(design) for design in designs[:100]], 'more': len(designs) > 100})
        body = parse(request)
        title, graph = payload(request)
        try:
            identifier = uuid.UUID(body['id']) if 'id' in body else uuid.uuid4()
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError('Invalid draft identifier.') from exc
        design, created = WorkflowDesign.objects.get_or_create(pk=identifier, defaults={
            'owner': request.user, 'title': title, 'graph': graph})
        if not created and (design.owner_id != request.user.pk or design.title != title or design.graph != graph):
            return error('duplicate_draft', 'This draft identifier is already in use. Keep your local copy and reload.', 409)
        return JsonResponse(summary(design), status=201 if created else 200)
    except (ValueError, RecursionError) as exc:
        return error('invalid_draft', str(exc), 400)
    except DatabaseError:
        logger.exception('Workflow draft collection unavailable')
        return error('draft_unavailable', 'Drafts are temporarily unavailable. Your current work is unchanged.', 503)


@never_cache
@require_http_methods(['GET', 'PUT', 'DELETE'])
def detail(request, identifier):
    denied = require_owner(request)
    if denied:
        return denied
    try:
        design = WorkflowDesign.objects.filter(pk=identifier, owner=request.user).first()
        if design is None:
            return error('not_found', 'Draft not found.', 404)
        if request.method == 'GET':
            with transaction.atomic():
                design = WorkflowDesign.objects.select_for_update().filter(pk=identifier, owner=request.user).first()
                if design is None:
                    return error('not_found', 'Draft not found.', 404)
                unresolved = unresolved_steps(design.graph, lock=True)
                return JsonResponse({**summary(design), 'graph': redacted_graph(design.graph, unresolved) if unresolved else design.graph,
                                     'unresolved': sorted(unresolved)})
        expected = request.headers.get('If-Match', '')
        try:
            expected = uuid.UUID(expected)
        except (ValueError, AttributeError):
            raise ValueError('Supply the current draft revision.')
        if request.method == 'DELETE':
            deleted, _ = WorkflowDesign.objects.filter(pk=design.pk, owner=request.user, revision=expected).delete()
            if not deleted:
                return error('stale_revision', 'The draft changed. Keep your local copy and reload.', 409)
            return JsonResponse({'deleted': True})
        title, graph = payload(request)
        new_revision = uuid.uuid4()
        updated = WorkflowDesign.objects.filter(pk=design.pk, owner=request.user, revision=expected).update(
            title=title, graph=graph, revision=new_revision, share_digest=None, updated=timezone.now())
        if not updated:
            return error('stale_revision', 'The draft changed. Keep your local copy and reload.', 409)
        design.refresh_from_db()
        return JsonResponse(summary(design))
    except (ValueError, RecursionError) as exc:
        return error('invalid_draft', str(exc), 400)
    except (DatabaseError, EdamUnavailable, SchemaUnavailable):
        logger.exception('Workflow draft unavailable')
        return error('draft_unavailable', 'Drafts are temporarily unavailable. Your current work is unchanged.', 503)


@never_cache
@require_POST
def share(request, identifier):
    denied = require_owner(request)
    if denied:
        return denied
    try:
        body = parse(request)
        if body.get('action') not in ('create', 'revoke'):
            raise ValueError('Choose create or revoke.')
        try:
            expected = uuid.UUID(request.headers.get('If-Match', ''))
        except ValueError:
            raise ValueError('Supply the current draft revision.')
        design = WorkflowDesign.objects.filter(pk=identifier, owner=request.user).first()
        if design is None:
            return error('not_found', 'Draft not found.', 404)
        if body['action'] == 'create' and unresolved_steps(design.graph):
            return error('unresolved_draft', 'A referenced function is hidden or unavailable. Review the draft before sharing.', 409)
        token = secrets.token_urlsafe(32) if body['action'] == 'create' else None
        digest = hashlib.sha256(token.encode()).hexdigest() if token else None
        revision = uuid.uuid4()
        updated = WorkflowDesign.objects.filter(pk=design.pk, owner=request.user, revision=expected).update(
            share_digest=digest, revision=revision, updated=timezone.now())
        if not updated:
            return error('stale_revision', 'The draft changed. Keep your local copy and reload.', 409)
        return JsonResponse({'revision': str(revision), 'token': token})
    except (ValueError, RecursionError) as exc:
        return error('invalid_draft', str(exc), 400)
    except (DatabaseError, EdamUnavailable, SchemaUnavailable):
        logger.exception('Workflow sharing unavailable')
        return error('draft_unavailable', 'Sharing is temporarily unavailable. Your current work is unchanged.', 503)


@csrf_exempt  # Read-only token lookup; the secret stays in the request body rather than URLs or logs.
@never_cache
@require_POST
def shared(request):
    try:
        token = parse(request).get('token')
        if not isinstance(token, str) or not 32 <= len(token) <= 100 or not token.isascii():
            return error('not_found', 'Shared design not found.', 404)
        digest = hashlib.sha256(token.encode()).hexdigest()
        with transaction.atomic():
            design = WorkflowDesign.objects.select_for_update().filter(share_digest=digest).first()
            if design is None or unresolved_steps(design.graph, lock=True):
                return error('not_found', 'Shared design not found.', 404)
            response = JsonResponse({'title': design.title, 'graph': design.graph, 'readOnly': True})
        response['Referrer-Policy'] = 'no-referrer'
        return response
    except (ValueError, RecursionError):
        return error('not_found', 'Shared design not found.', 404)
    except (DatabaseError, EdamUnavailable, SchemaUnavailable):
        logger.exception('Shared workflow unavailable')
        return error('draft_unavailable', 'Shared designs are temporarily unavailable.', 503)
