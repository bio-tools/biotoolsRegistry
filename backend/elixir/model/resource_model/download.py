from django.db import models
from elixir.model.resource_model.resource import * 

class Download(models.Model):
	# comment should be called note
	# should cmd be here?

	url = models.TextField()
	type = models.TextField()
	note = models.TextField(blank=True, null=True)
	version = models.TextField(blank=True, null=True)
	cmd = models.TextField(blank=True, null=True, max_length=100)
	resource = models.ForeignKey(Resource, null=True, blank=True, related_name='download', on_delete=models.CASCADE)

	# metadata
	additionDate = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return str(self.url) or ''