import logging

from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe, require_POST

from elixir.edam_lookup import EdamUnavailable
from elixir.resource_ui import SchemaUnavailable
from elixir.workflow_matching import StaleCursor, compare_annotations, function_details, matching_candidates

logger = logging.getLogger(__name__)


@require_safe
@never_cache
def candidates(request):
    try:
        return JsonResponse(matching_candidates(request.GET))
    except StaleCursor as exc:
        return JsonResponse({'error': {'code': 'stale_cursor', 'message': str(exc)}}, status=409)
    except (DatabaseError, EdamUnavailable, SchemaUnavailable):
        logger.exception('Workflow matching unavailable')
        return JsonResponse({'error': {'code': 'matching_unavailable', 'message': 'Matching is temporarily unavailable. Please retry.'}}, status=503)
    except ValueError as exc:
        return JsonResponse({'error': {'code': 'invalid_match', 'message': str(exc)}}, status=400)


@require_safe
@never_cache
def function(request):
    try:
        if set(request.GET) != {'ref'} or len(request.GET.getlist('ref')) != 1:
            raise ValueError('Supply one function reference.')
        result = function_details(request.GET['ref'])
        if result is None:
            return JsonResponse({'error': {'code': 'function_unavailable', 'message': 'The function is no longer available.'}}, status=404)
        return JsonResponse(result)
    except (DatabaseError, EdamUnavailable, SchemaUnavailable):
        logger.exception('Workflow function unavailable')
        return JsonResponse({'error': {'code': 'matching_unavailable', 'message': 'Matching is temporarily unavailable. Please retry.'}}, status=503)
    except ValueError as exc:
        return JsonResponse({'error': {'code': 'invalid_reference', 'message': str(exc)}}, status=400)


@require_POST
@never_cache
def compare(request):
    from elixirapp.workflow_drafts import parse
    try:
        return JsonResponse(compare_annotations(parse(request)))
    except (DatabaseError, EdamUnavailable, SchemaUnavailable):
        logger.exception('Workflow comparison unavailable')
        return JsonResponse({'error': {'code': 'matching_unavailable', 'message': 'Matching is temporarily unavailable. Please retry.'}}, status=503)
    except ValueError as exc:
        return JsonResponse({'error': {'code': 'invalid_match', 'message': str(exc)}}, status=400)
