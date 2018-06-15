from django.db import models


class IssueType(models.Model):
    type = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    attribute = models.TextField(blank=True, null=True)
    field_name = models.TextField(blank=True, null=True)
    field_value = models.TextField(blank=True, null=True)


class IssueState(models.Model):
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class Issue(models.Model):
    issue_type = models.ForeignKey(IssueType, null=False, blank=False, on_delete=models.CASCADE)
    issue_state = models.ForeignKey(IssueState, null=False, blank=False, on_delete=models.CASCADE)
    field_name = models.TextField(blank=True, null=True)
    field_value = models.TextField(blank=True, null=True)

    resource_textId = models.TextField(blank=True, null=True)
    resource_versionId = models.TextField(blank=True, null=True)
    
    resolution_date = models.DateTimeField(null=True, blank=True)
    resolution_actor = models.CharField(max_length=32, blank=True, null=True)

    creation_actor = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    @classmethod
    def report(self, textId):
        return self.objects.filter(resource_textId=textId)

    def __unicode__(self):
        return self.resource_textId + ' \t-\t ' + unicode(self.issue_type.type) + '\t' + unicode(self.issue_type.attribute) + '\t' + unicode(self.issue_type.field_name) + '\t' + unicode(self.issue_type.field_value) + '\t' + unicode(self.issue_state.name)
