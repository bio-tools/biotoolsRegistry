from django.db import models
from elixir.model.resource_model.elixirInfo import * 
from elixir.model.resource_model.editPermission import *
from django.contrib.auth.models import User

class Resource(models.Model):
    YES_NO_CHOICES = (
        (0, 'NO'),
        (1, 'YES'),
    )

    WAS_ID_VALIDATED_CHOICES = (
        (0, 'NO'),
        (1, 'YES'),
    )

    HOMEPAGE_STATUS_CHOICES = (
        (0, 'UP'),
        (1, 'DOWN'),
        (2, 'DEAD')
    )

    textId = models.CharField(max_length=50)
    name = models.TextField()
    version = models.TextField(blank=True, null=True)
    versionId = models.CharField(max_length=50, null=True, default='none')

    homepage = models.TextField()
    description = models.TextField()

    canonicalID = models.TextField(blank=True, null=True)

    issue_score = models.FloatField(blank=True, null=True)

    version_hash = models.TextField(blank=True, null=True)
    visibility = models.IntegerField(choices=YES_NO_CHOICES, default=1)
    latest = models.IntegerField(choices=YES_NO_CHOICES, default=1)
    was_id_validated = models.IntegerField(choices=WAS_ID_VALIDATED_CHOICES, default=0)
    homepage_status = models.IntegerField(choices=HOMEPAGE_STATUS_CHOICES, default=0)

    # things that used to be in separate tables
    cost = models.TextField(blank=True, null=True)
    maturity = models.TextField(blank=True, null=True)
    license = models.TextField(blank=True, null=True)

    elixirInfo = models.ForeignKey(ElixirInfo, null=True, blank=True, on_delete=models.CASCADE)
    editPermission = models.ForeignKey(EditPermission, null=False, blank=True, on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(blank=True, null=True)
    lastUpdate = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='resource', blank=False, null=False)

    # additional information that we don't have in the xsd model
    availability = models.TextField(blank=True, null=True)
    downtime = models.TextField(blank=True, null=True)

    # Information related to the conda channel and conda package
    conda_channel = models.CharField(max_length=50, null=True)
    conda_package = models.CharField(max_length=75, null=True)
    
    def __unicode__(self):
        return unicode(self.name) or u''

# table to keep user requests
class ResourceRequest(models.Model):
    requestId = models.CharField(max_length=50)
    resource = models.ForeignKey(Resource, null=True, blank=True, related_name='requests', on_delete=models.CASCADE)
    type = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, related_name='requests', blank=True, null=True, on_delete=models.CASCADE)
    completedBy = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
