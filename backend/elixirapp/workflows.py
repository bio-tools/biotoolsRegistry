import logging
import math

from django.db import DatabaseError
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_safe
from elixir.models import Workflow

logger = logging.getLogger(__name__)


@require_safe
def designer(request):
    response = render(request, 'html/workflow_designer.html')
    response['Referrer-Policy'] = 'no-referrer'
    return response


def annotation_box(annotation, width, height):
    values = [annotation.startX, annotation.startY, annotation.endX, annotation.endY, width, height]
    if not all(math.isfinite(value) for value in values) or width <= 0 or height <= 0:
        return None
    left, right = sorted(max(0, min(width, value)) / width * 100 for value in (annotation.startX, annotation.endX))
    top, bottom = sorted(max(0, min(height, value)) / height * 100 for value in (annotation.startY, annotation.endY))
    if left == right or top == bottom:
        return None
    return f'left:{left:.4f}%;top:{top:.4f}%;width:{right-left:.4f}%;height:{bottom-top:.4f}%'


@require_safe
def page(request):
    query = request.GET.get('q', '').strip()[:200]
    try:
        workflows = Workflow.objects.all().prefetch_related('annotations').order_by('biotoolsID')
        if query:
            workflows = workflows.filter(Q(biotoolsID__icontains=query) | Q(description__icontains=query) |
                Q(annotations__title__icontains=query) | Q(annotations__description__icontains=query) |
                Q(annotations__edam_term__icontains=query)).distinct()
        records = []
        for workflow in workflows:
            annotations = [{'record': item, 'box': annotation_box(item, workflow.image_width, workflow.image_height)}
                           for item in workflow.annotations.all()]
            image_url = workflow.image.url if workflow.image and workflow.image.storage.exists(workflow.image.name) else None
            records.append({'record': workflow, 'image': image_url, 'annotations': annotations})
        return render(request, 'html/workflows.html', {'workflows': records, 'query': query})
    except (DatabaseError, OSError, ValueError):
        logger.exception('Workflow list unavailable')
        return render(request, 'html/workflows.html', {'unavailable': True, 'query': query}, status=503)
