from django.db import models
from elixir.model.resource_model.resource import * 
from jsonfield import JSONField
from django.utils import timezone

# table to keep historic stats data
class StatsData(models.Model):
    date = models.DateTimeField()
    data = JSONField(null=True, blank=True)
    totalEntries = models.IntegerField(default=0)
    creditAffiliationCount = models.IntegerField()
    edamAnnotationsCount = models.IntegerField()
    formatAnnotationsCount = models.IntegerField()
    functionAnnotationsCount = models.IntegerField()
    topicAnnotationsCount = models.IntegerField()
    dataTypeAnnotationsCount = models.IntegerField()
    nameAnnotationCount = models.IntegerField(default=0)
    uniqueIDAnnotationCount = models.IntegerField(default=0)
    topicAnnotationCount = models.IntegerField(default=0)
    operatingSystemAnnotationCount = models.IntegerField(default=0)
    codeAvailabilityAnnotationCount = models.IntegerField(default=0)
    operationAnnotationCount = models.IntegerField(default=0)
    descriptionAnnotationCount = models.IntegerField(default=0)
    downloadsAnnotationCount = models.IntegerField(default=0)
    dataFormatsAnnotationCount = models.IntegerField(default=0)
    accessibilityAnnotationCount = models.IntegerField(default=0)
    toolTypeAnnotationCount = models.IntegerField(default=0)
    documentationAnnotationCount = models.IntegerField(default=0)
    inputOutputAnnotationCount = models.IntegerField(default=0)
    communityAnnotationCount = models.IntegerField(default=0)
    contactAnnotationCount = models.IntegerField(default=0)
    homepageAnnotationCount = models.IntegerField(default=0)
    publicationAnnotationCount = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now()
        return super(StatsData, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return ''
