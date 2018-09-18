from django.db import models
from elixir.model.resource_model.resource import * 

class Link(models.Model):
	url = models.TextField()
	type = models.TextField()
	note = models.TextField(blank=True, null=True)
	resource = models.ForeignKey(Resource, null=True, blank=True, related_name='link', on_delete=models.CASCADE)

	# metadata
	additionDate = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return unicode(self.url) or u''