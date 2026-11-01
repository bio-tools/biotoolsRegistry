from django.db import models
from elixir.model.resource_model.resource import * 

class Documentation(models.Model):
	url = models.TextField()
	type_old = models.TextField()
	note = models.TextField(blank=True, null=True)
	resource = models.ForeignKey(Resource, null=True, blank=True, related_name='documentation', on_delete=models.CASCADE)

	# metadata
	additionDate = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return str(self.url) or ''

class DocumentationType(models.Model):
    type = models.TextField(blank=True, null=True)
    documentation = models.ForeignKey(Documentation, null=True, blank=True, related_name='type', on_delete=models.CASCADE) 

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.name) or ''