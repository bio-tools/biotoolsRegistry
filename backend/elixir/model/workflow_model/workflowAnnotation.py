from django.db import models
from elixir.model.workflow_model.workflow import *

class WorkflowAnnotation(models.Model):
    startX = models.FloatField()
    startY = models.FloatField()
    endX = models.FloatField()
    endY = models.FloatField()
    title = models.TextField(blank=True, null=False)
    description = models.TextField(blank=True, null=False)
    edam_term = models.TextField(blank=True, null=True)
    edam_uri = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    workflow = models.ForeignKey(Workflow, null=True, blank=True, related_name='annotations', on_delete=models.CASCADE)

