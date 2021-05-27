from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import User

class Domain(models.Model):
    YES_NO_CHOICES = (
        (0, 'NO'),
        (1, 'YES'),
    )

    # name is not unique anymore because of visibility field
    name = models.CharField(blank=False, null=False, max_length=50, unique=False)

    title = models.TextField(blank=True, null=True)
    sub_title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    
    owner = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    visibility = models.IntegerField(choices=YES_NO_CHOICES, default=1) 

    def __unicode__(self):
        return str(self.name) or ''


class DomainResource(models.Model):
    
    domain = models.ForeignKey(Domain, related_name='resource', null=False, blank=False, on_delete=models.CASCADE)
    name = models.TextField(blank=False, null=False)
    version = models.TextField(blank=True, null=True)
    biotoolsID = models.TextField(blank=False, null=False)
    versionId = models.TextField(blank=False, null=False)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        # return unicode(self.domain) + ' ' + unicode(self.biotoolsID)
        return str(self.biotoolsID)

class DomainTag(models.Model):
    domain = models.ForeignKey(Domain, null=True, blank=True, related_name='tag', on_delete=models.CASCADE)
    name = models.TextField(blank=False, null=True, max_length=50)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.name) or ''

class DomainCollection(models.Model):
    domain = models.ForeignKey(Domain, null=True, blank=True, related_name='collection', on_delete=models.CASCADE)
    name = models.TextField(blank=False, null=False, max_length=50)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return str(self.name) or ''