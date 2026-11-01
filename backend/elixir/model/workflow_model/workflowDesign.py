import uuid

from django.conf import settings
from django.db import models


class WorkflowDesign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workflow_designs')
    title = models.CharField(max_length=120)
    graph = models.JSONField()
    revision = models.UUIDField(default=uuid.uuid4, editable=False)
    share_digest = models.CharField(max_length=64, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
