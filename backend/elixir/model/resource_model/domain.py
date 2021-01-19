from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import User

class Domain(models.Model):
    name = models.CharField(blank=False, null=False, max_length=50, unique=True)

    title = models.TextField(blank=True, null=True)
    sub_title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    # is_private = models.BooleanField(default=False)


    owner = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    def __unicode__(self):
        return unicode(self.name) or u''


class DomainResource(models.Model):
    domain = models.ForeignKey(Domain, null=False, blank=False, on_delete=models.CASCADE)
    name = models.TextField(blank=False, null=False)
    version = models.TextField(blank=True, null=True)
    biotoolsID = models.TextField(blank=False, null=False)
    versionId = models.TextField(blank=False, null=False)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.domain) + ' ' + unicode(self.biotoolsID)

# class DomainTag(models.Model):
#     domain = models.ForeignKey(Domain, null=True, blank=True, related_name='domaintag', on_delete=models.CASCADE)
#     name = models.TextField(blank=False, null=False, max_length=50)

# class DomainCollection(models.Model):
#     domain = models.ForeignKey(Domain, null=True, blank=True, related_name='domaincollection', on_delete=models.CASCADE)
#     name = models.TextField(blank=False, null=False, max_length=50)