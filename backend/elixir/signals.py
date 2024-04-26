from django.db.models.signals import post_save, pre_save
from elixir.models import Publication, Resource
from elixir.publication_metadata import update_publication
import datetime, django.utils.timezone
from django.utils import timezone

# fetch publication metadata after creation
def set_publicationMetadata(sender, instance, **kwargs):
	update_publication(instance)

post_save.connect(set_publicationMetadata, sender=Publication)


# since we can't use the built-in time (since we need to copy it to new resource instances when updating resources), we have to update additionDate manually
def set_additionDate(sender, instance, **kwargs):
	if instance.additionDate is None:
		instance.additionDate = datetime.datetime.now()


pre_save.connect(set_additionDate, sender=Resource)