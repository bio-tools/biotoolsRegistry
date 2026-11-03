"""Session-only resource editor facade over the existing resource write handlers."""
from copy import deepcopy
from collections import defaultdict, deque
from hashlib import sha256
import json
import logging
from types import SimpleNamespace

from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import never_cache
from rest_framework.exceptions import APIException

from elixir.models import Resource
from elixir.permissions import HasEditPermissionToEditResourceOrReadOnly
from elixir.queries import get_tool, ToolNotFound
from elixir.serializers import ResourceSerializer, ResourceUpdateSerializer
from elixir.serialization.resource_serialization.publication import publication_identity
from elixir.resource_options import METADATA_CHOICES
from elixir.resource_ui import SchemaUnavailable, resource_descriptor
from elixir.view.resource import ResourceDetail, ResourceList, check_update_confidence_flag
from elixirapp.browser_auth import browser_login_required


logger = logging.getLogger(__name__)
BASIC_FIELDS = {'name', 'description', 'homepage', 'toolType'}


def editor_fields(descriptor):
    return {name for name, field in descriptor['contract']['fields'].items() if field['writable']}


def protected_nested_values(value, contract):
    """Compare non-writable annotations across reorder without inventing row identities."""
    protected = defaultdict(list)

    def visit(value, field, path=''):
        if isinstance(value, list) and field.get('item'):
            for item in value:
                visit(item, field['item'], path)
        elif isinstance(value, dict) and field.get('fields'):
            for name, child in value.items():
                metadata = field['fields'].get(name)
                child_path = '.'.join(filter(None, (path, name)))
                # Permission and publication identity checks own these bounded cases.
                if not metadata or child_path in {'editPermission', 'publication.metadata'}:
                    continue
                if metadata.get('writable'):
                    visit(child, metadata, child_path)
                elif path:
                    protected[child_path].append(json.dumps(child, sort_keys=True))
    visit(value, contract)
    return {path: sorted(values) for path, values in protected.items()}


def can_edit(user, resource):
    return user.is_authenticated and HasEditPermissionToEditResourceOrReadOnly().has_object_permission(
        SimpleNamespace(user=user, method='PUT'), None, resource)


def can_manage_permissions(user, resource):
    return resource is None or ResourceDetail().check_for_edit_permissions(SimpleNamespace(user=user), resource)


def existing(identifier, user, *, lock=False):
    try:
        resource = get_tool(identifier)
        if lock:
            resource = Resource.objects.select_for_update().get(pk=resource.pk, visibility=1)
    except (ToolNotFound, Resource.DoesNotExist) as exc:
        raise Http404 from exc
    if not can_edit(user, resource):
        raise PermissionDenied
    return resource


def revision(resource, data):
    return sha256(json.dumps([resource.pk, data], sort_keys=True).encode()).hexdigest()


def normalized(value, field):
    """Mirror the contract's optional null/empty omission; never drop unknown fields."""
    if field.read_only:
        return value
    if isinstance(value, list):
        return [normalized(item, field.child) for item in value]
    if isinstance(value, dict):
        return {key: normalized(child, field.fields[key]) for key, child in value.items()
                if not (not field.fields[key].required and not field.fields[key].read_only and (
                    (child is None and not field.fields[key].allow_null)
                    or (child == [] and not getattr(field.fields[key], 'allow_empty', True))))}
    return value


def preservation_blocked(data, original):
    def protected_ids(value):
        items = value.get('otherID')
        if not isinstance(items, list):
            return []
        return sorted(json.dumps(item, sort_keys=True) for item in items if isinstance(item, dict)
                      and isinstance(item.get('value'), str) and item['value'].strip().lower().startswith('biotools:'))

    if protected_ids(data) != protected_ids(original):
        return True
    previous = defaultdict(deque)
    for item in original.get('publication') or []:
        previous[publication_identity(item)].append(item.get('metadata'))
    publications = data.get('publication')
    for item in publications if isinstance(publications, list) else []:
        if not isinstance(item, dict):
            continue  # Leave malformed values to the authoritative serializer.
        matches = previous[publication_identity(item)]
        metadata = matches.popleft() if matches else None
        if item.get('metadata') is not None and item['metadata'] != metadata:
            return True
    return False


def unrelated(data, editable_fields=BASIC_FIELDS):
    result = deepcopy(data)
    for key in editable_fields | {'lastUpdate'}:
        result.pop(key, None)
    # These relations are sets in the authoritative serializer; retain multiplicity checks.
    for key in ('toolType', 'operatingSystem', 'language', 'collectionID'):
        if isinstance(result.get(key), list):
            result[key].sort()
    for function in result.get('function', []):
        function['operation'].sort(key=lambda value: json.dumps(value, sort_keys=True))
        for item in function.get('input', []) + function.get('output', []):
            item.get('format', []).sort(key=lambda value: json.dumps(value, sort_keys=True))
    return result


class PreservationConflict(APIException):
    status_code = 409
    default_detail = 'This replacement would change other metadata. Nothing was saved; your draft is retained.'


class BasicUpdate(ResourceDetail):
    def process_request_for_otherID(self, request, rID):
        # The facade checks protected IDs before mutation; keep submitted error indices.
        return request

    def check_replacement(self, data):
        if unrelated(self.original, self.changed_fields) != unrelated(data, self.changed_fields):
            raise PreservationConflict()


def unknown_nested_fields(value, field):
    """DRF ignores unknown keys; the editor must not claim those values were saved."""
    if isinstance(value, list) and hasattr(field, 'child'):
        errors = [unknown_nested_fields(item, field.child) for item in value]
        return errors if any(errors) else {}
    if isinstance(value, dict) and hasattr(field, 'fields'):
        errors = {}
        for key, child in value.items():
            error = unknown_nested_fields(child, field.fields[key]) if key in field.fields else ['Unsupported field.']
            if error:
                errors[key] = error
        return errors
    return {}


def configuration(user, resource=None, *, canonical=False):
    data = ResourceSerializer(resource).data if resource else {
        'name': '', 'biotoolsID': '', 'description': '', 'homepage': '', 'toolType': [],
        'editPermission': {'type': 'private', 'authors': []},
    }
    kwargs = {'identifier': resource.biotoolsID} if resource else {}
    try:
        descriptor = resource_descriptor()
        choices = dict(METADATA_CHOICES)
    except SchemaUnavailable:
        logger.exception('Resource editor schema is unavailable')
        descriptor, choices = None, {}
    return {'resource': data, 'revision': revision(resource, data) if resource else None,
            'endpoint': reverse('html:editor-save' if resource else 'html:editor-create', kwargs=kwargs),
            'validateEndpoint': reverse('html:editor-save' if resource else 'html:editor-create', kwargs=kwargs).replace('/save/', '/validate/'),
            'previewEndpoint': reverse('html:editor-save' if resource else 'html:editor-create', kwargs=kwargs).replace('/save/', '/record-preview/'),
            'editUrl': reverse('html:editor-edit', kwargs=kwargs) if resource else None,
            'detailUrl': reverse('html:tool-detail', kwargs=kwargs) if resource else None,
            'schema': descriptor, 'schemaRevision': descriptor['revision'] if descriptor else None,
            'toolTypes': choices.get('toolType', []), 'edamEndpoint': reverse('canonical-edam-lookup' if canonical else 'html:edam-lookup'),
            'metadataOptions': choices,
            'bridgeEndpoint': '/github-to-biotools' if settings.GITHUB_BRIDGE_URL else None,
            'canManagePermissions': can_manage_permissions(user, resource)}


@browser_login_required
@require_GET
@never_cache
def page(request, identifier=None):
    resource = existing(identifier, request.user) if identifier else None
    return render(request, 'html/resource_editor.html', {'editor_config': configuration(request.user, resource, canonical=getattr(request, 'canonical', False)),
                  'resource': resource, 'editing': resource is not None})


@browser_login_required
@require_POST
@never_cache
def save(request, identifier=None, validate_only=False):
    if request.content_type != 'application/json':
        return JsonResponse({'detail': 'Send a JSON resource.'}, status=415)
    try:
        body = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'detail': 'Invalid JSON.'}, status=400)
    if not isinstance(body, dict) or set(body) != {'resource', 'revision', 'schemaRevision'} or not isinstance(body['resource'], dict):
        return JsonResponse({'detail': 'Supply resource, revision and schemaRevision.'}, status=400)
    try:
        descriptor = resource_descriptor()
    except SchemaUnavailable:
        logger.exception('Resource editor save blocked by unavailable schema')
        return JsonResponse({'detail': 'Schema metadata is unavailable. Nothing was saved; export your draft before reloading.'}, status=503)
    if body['schemaRevision'] != descriptor['revision']:
        return JsonResponse({'detail': 'The resource schema changed. Nothing was saved; export your draft before reloading and revalidating.'}, status=409)
    payload = body['resource']
    nested_errors = unknown_nested_fields(payload, ResourceSerializer())
    if nested_errors:
        return JsonResponse(nested_errors, status=400)
    try:
        with transaction.atomic():
            resource = existing(identifier, request.user, lock=True) if identifier else None
            original = ResourceSerializer(resource).data if resource else None
            editable_fields = editor_fields(descriptor) | ({'editPermission'} if can_manage_permissions(request.user, resource) else set())
            if resource:
                if body['revision'] != revision(resource, original):
                    return JsonResponse({'detail': 'This record changed since it was loaded. Export your draft before reloading.'}, status=409)
                expected = normalized(original, ResourceUpdateSerializer())
                if 'editPermission' not in editable_fields and payload.get('editPermission') != expected.get('editPermission'):
                    raise PermissionDenied
                if {key: value for key, value in payload.items() if key not in editable_fields} != {
                        key: value for key, value in expected.items() if key not in editable_fields}:
                    return JsonResponse({'detail': 'Identifiers, ownership and server metadata cannot be changed in this editor.'}, status=400)
            elif body['revision'] is not None or set(payload) - editable_fields - {'biotoolsID'}:
                return JsonResponse({'detail': 'Only supported schema fields may be supplied for a new record.'}, status=400)

            if preservation_blocked(payload, expected if resource else {}):
                return JsonResponse({'detail': 'Publication enrichment and protected identifiers cannot be changed. Nothing was saved.'}, status=409)
            if protected_nested_values(payload, descriptor['contract']) != protected_nested_values(expected if resource else {}, descriptor['contract']):
                return JsonResponse({'detail': 'Non-writable nested metadata cannot be changed. Nothing was saved; your draft is retained.'}, status=409)

            # The outer Django view owns authentication and CSRF. The existing handlers
            # consume user/data/method and still perform their own object permission checks.
            mutation = SimpleNamespace(user=request.user, data=deepcopy(payload), method='PUT' if resource else 'POST',
                                       authenticators=(), successful_authenticator=None)
            if validate_only:
                serializer = (ResourceUpdateSerializer if resource else ResourceSerializer)(data=deepcopy(payload),
                    context={'request': mutation, 'request_type': mutation.method, 'previous_resource': resource})
                if not serializer.is_valid():
                    return JsonResponse(serializer.errors, status=400)
                if not request.user.is_superuser and (
                    (resource and not check_update_confidence_flag(resource.confidence_flag, payload.get('confidence_flag')))
                    or (not resource and payload.get('confidence_flag') not in (None, '', 'tool'))):
                    return JsonResponse({'confidence_flag': ['This confidence change is not permitted.']}, status=403)
                return JsonResponse({'valid': True, 'detail': 'Validation passed. Nothing was saved.'})
            view = BasicUpdate() if resource else ResourceList()
            view.request = mutation
            view.original = original
            view.changed_fields = {key for key in editable_fields if payload.get(key) != expected.get(key)} if resource else editable_fields
            view.check_permissions(mutation)
            response = view.put(mutation, resource.biotoolsID) if resource else view.post(mutation)
            if response.status_code >= 400:
                transaction.set_rollback(True)
                return JsonResponse(response.data, status=response.status_code)
            unchanged = response.data.get('no_changes', False)
            saved = resource if unchanged else get_tool(response.data['biotoolsID'])
            return JsonResponse({**configuration(request.user, saved, canonical=getattr(request, 'canonical', False)), 'no_changes': unchanged}, status=response.status_code)
    except APIException as exc:
        return JsonResponse(exc.detail if isinstance(exc.detail, dict) else {'detail': exc.detail}, status=exc.status_code)
    except PermissionDenied:
        return JsonResponse({'detail': 'You do not have permission to edit this record.'}, status=403)
    except Http404:
        raise
    except Exception:
        logger.exception('Resource editor save failed')
        return JsonResponse({'detail': 'Save could not be confirmed. Your draft is retained; check the record before retrying.'}, status=503)
