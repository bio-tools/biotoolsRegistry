from django.db import models
from elixir.model.resource_model.resource import * 

# table to keep search terms along with their type
class SearchTermLog(models.Model):
	name = models.CharField(max_length=32, blank=True, null=True)
	term = models.CharField(max_length=32, blank=True, null=True)

	class Meta:
		unique_together = ['name', 'term']


# table to keep a collectionID of search terms that were a part of single search query
class SearchQueryLog(models.Model):
	date = models.DateTimeField(auto_now_add=True)
	terms = models.ManyToManyField(SearchTermLog, related_name="queries")