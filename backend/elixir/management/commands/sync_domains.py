from collections import OrderedDict
from django.conf import settings
from django.core.management.base import BaseCommand
from elixir.models import *
from elixir.serializers import *
from elasticsearch import Elasticsearch
import json


def process_domain(domain_object):
	"""Obtain a union of tools from existing domain resources / tools and also regular tools."""

	domain_data = DomainSerializer(domain_object).data

	# get OrderedDict (name and biotoolsID) of resources that are in the domain
	domain_resources_dict = OrderedDict()
	for r in domain_data['resources']:
		domain_resources_dict[r['biotoolsID']] = r
 
	# get OrderedDict (name and biotoolsID) of resources that are annotated with a list of collections (coming from collections tagged in domains)
	resource_list = []
	for c in domain_data['collection']:
		collection_objects = CollectionID.objects.filter(name=c).select_related('resource')
		
		resource_list.extend([
			OrderedDict([('name', c.resource.name), ('biotoolsID', c.resource.biotoolsID)]) 
			for c in collection_objects if c.resource.visibility == 1
		])
	
	# union the resources objects (also hash the same biotoolsID sometimes which is good because it updates tool names in domains as a side-effect )
	for r in resource_list:
		domain_resources_dict[r['biotoolsID']] = r
	
	# update the data
	domain_data['resources'] = list(domain_resources_dict.values())

	# return a new serializer (DomainUpdateSerializer type)
	return DomainUpdateSerializer(data=domain_data, context={"request_type":"PUT"})
	


class Command(BaseCommand):
	"""Synchronize domains based on tool annotations (e.g. collections)"""

	help = 'Synchronize domains based on tool annotations (e.g. collections)'
	
	def handle(self, *args, **options):
		es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)

		domains = Domain.objects.filter(visibility=1, is_private=False)
		for d_obj in domains:
			domain_serializer = process_domain(d_obj)
			
			# maybe we should try except this block and if anything happens
			#	we should revert to the old domain data (i.e. d_obj)
			if domain_serializer.is_valid():
				d_obj.visibility = 0
				d_obj.save()

				domain_serializer.save(owner=d_obj.owner)

				es.index(
					index='domains', 
					doc_type='_doc', 
					id=domain_serializer.validated_data['name'], 
					body=json.loads(json.dumps(domain_serializer.data))
				)

				print('Updated domain:', domain_serializer.validated_data['name'])
