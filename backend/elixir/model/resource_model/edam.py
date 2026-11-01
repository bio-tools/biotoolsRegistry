from django.db import models
from elixir.model.resource_model.resource import * 

# table to keep ontologies and parts of ontologies for the widget
class Ontology(models.Model):
    name = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.name) or ''


# need to make this 0..many instead od 1..many
class Function(models.Model):
    # comment should be called note
    # I think cmd should be removed , doublecheck
    note = models.TextField(blank=True, null=True)
    cmd = models.TextField(blank=True, null=True, max_length=100)
    resource = models.ForeignKey(Resource, null=True, blank=True, related_name='function', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return str(self.note) or ''


class Operation(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    function = models.ForeignKey(Function, null=True, blank=True, related_name='operation', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.term) or ''

class Data(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.term) or ''


class Input(models.Model):
    # reverse relationship, because many inputs
    function = models.ForeignKey(Function, null=True, blank=True, related_name='input', on_delete=models.CASCADE)
    # forward relationship, because one data
    data = models.ForeignKey(Data, null=True, blank=False,on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.data.term) or ''


class Output(models.Model):
    # reverse relationship, because many outputs
    function = models.ForeignKey(Function, null=True, blank=True, related_name='output', on_delete=models.CASCADE)
    # forward relationship, because one data
    data = models.ForeignKey(Data, null=True, blank=False, on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.data.term) or ''


class Format(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    input = models.ForeignKey(Input, null=True, blank=True, related_name='format', on_delete=models.CASCADE)
    output = models.ForeignKey(Output, null=True, blank=True, related_name='format', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.term) or ''
        