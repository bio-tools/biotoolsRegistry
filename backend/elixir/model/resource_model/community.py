from django.db import models


class BioLib(models.Model):
    app_name = models.TextField(blank=False, null=True)
    author_name = models.TextField(blank=False, null=True)
    author_username = models.TextField(blank=False, null=True)

    def __unicode__(self):
        return unicode(self.name) or u''

class Community(models.Model):
    biolib = models.ForeignKey(BioLib, blank=False, null=True)

    def __unicode__(self):
        return unicode(self.name) or u''


