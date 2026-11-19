import uuid

from django.conf import settings
from django.db import models


class ResourceDraft(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resource_drafts')
    target = models.CharField(max_length=100, blank=True, default='')
    record_revision = models.CharField(max_length=64, blank=True, default='')
    resource = models.JSONField()
    revision = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
