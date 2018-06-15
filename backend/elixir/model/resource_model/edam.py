from django.db import models
from elixir.model.resource_model.resource import * 

# table to keep ontologies and parts of ontologies for the widget
class Ontology(models.Model):
    name = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.name) or u''

class Function(models.Model):
    comment = models.TextField(blank=True, null=True)
    resource = models.ForeignKey(Resource, null=True, blank=True, related_name='function', on_delete=models.CASCADE)

    # metadata
    additionDate= models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.comment) or u''

class Operation(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    function = models.ForeignKey(Function, null=True, blank=True, related_name='operation', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.term) or u''

class Data(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.term) or u''

class Input(models.Model):
    # reverse relationship, because many inputs
    function = models.ForeignKey(Function, null=True, blank=True, related_name='input', on_delete=models.CASCADE)
    # forward relationship, because one data
    data = models.ForeignKey(Data, null=True, blank=False)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.data.term) or u''

class Output(models.Model):
    # reverse relationship, because many outputs
    function = models.ForeignKey(Function, null=True, blank=True, related_name='output', on_delete=models.CASCADE)
    # forward relationship, because one data
    data = models.ForeignKey(Data, null=True, blank=False)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.data.term) or u''

class Format(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    input = models.ForeignKey(Input, null=True, blank=True, related_name='format', on_delete=models.CASCADE)
    output = models.ForeignKey(Output, null=True, blank=True, related_name='format', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.term) or u''