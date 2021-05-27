from django.db import models
from elixir.model.resource_model.resource import * 

class Credit(models.Model):
    # make sure you have a credit name either as a TextField or as a CreditName see class below this one
    # comment should be note
    # some fields need to be removed check notes

    name = models.TextField(null=True, blank=True)
    email = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    orcidid = models.TextField(blank=True, null=True)
    gridid = models.TextField(blank=True, null=True)
    rorid = models.TextField(blank=True, null=True)
    fundrefid = models.TextField(blank=True, null=True)
    typeEntity = models.TextField(blank=True, null=True)
    
    #typeRole = models.TextField(blank=True, null=True)

    note = models.TextField(blank=True, null=True)
    #elixirPlatform = models.TextField(blank=True, null=True)
    #elixirNode = models.TextField(blank=True, null=True)
    #tel = models.TextField(blank=True, null=True)
    resource = models.ForeignKey(Resource, null=True, blank=True, related_name='credit', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return ''


# A credit can have 0 or many type roles
class CreditTypeRole(models.Model):
    typeRole = models.TextField(blank=True, null=True)
    credit = models.ForeignKey(Credit, null=True, blank=True, related_name='typeRole', on_delete=models.CASCADE) 

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.name) or ''

# class CreditName(models.Model):
#   name = models.TextField(blank=True, null=True)
#   credit = models.ForeignKey(Credit, null=True, blank=True, related_name='name', on_delete=models.CASCADE)

#   # metadata
#   additionDate = models.DateTimeField(auto_now_add=True)

#   def __unicode__(self):
#       return unicode(self.name) or u''
