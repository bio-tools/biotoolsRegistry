from django.core.management.base import BaseCommand, CommandError
from elixir.models import *
import json, os

def lookup_count(ontology, term):
	if ontology == 'topic':
		return Resource.objects.filter(visibility=1, topic__term=term).count()
	elif ontology == 'operation':
		return Resource.objects.filter(visibility=1, function__operation__term=term).count()

	# TODO: needs more thought on adding the input+output counts 
	# elif ontology == 'data':
	# 	return Resource.objects.filter(visibility=1, function__input__data__term=term).count()
	# elif ontology == 'format':
	# 	return Resource.objects.filter(visibility=1, function__input__format__term=term).count()

def add_counts(ontology, node, depth=0):

	count = lookup_count(ontology, node['text'])

	print("    " * depth + node['text'] + " (" + str(count) + ")")
	for child in node['children']:
		add_counts(ontology, child, depth+1)

class Command(BaseCommand):
	help = 'Generate stats for EDAM'

	def handle(self, *args, **options):

		topic_root = json.loads(Ontology.objects.get(name="EDAM_Topic").data)
		add_counts('topic', topic_root)

		# operation_root = json.loads(Ontology.objects.get(name="EDAM_Operation").data)
		# add_counts('operation', operation_root)

		self.stdout.write('All done.')
