from django.db import models
from elixir.model.resource_model.resource import * 

class Credit(models.Model):
    name = models.TextField(null=True, blank=True)
    email = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    orcidId = models.TextField(blank=True, null=True)
    gridId = models.TextField(blank=True, null=True)
    typeEntity = models.TextField(blank=True, null=True)
    typeRole = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    resource = models.ForeignKey(Resource, null=True, blank=True, related_name='credit', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u''