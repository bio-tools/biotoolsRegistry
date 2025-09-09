from elasticsearch import Elasticsearch
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from elixir import search
from elixir.serializers import *

es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)

# From https://github.com/bio-tools/biotoolsSum/blob/master/public/config.js
DATA = [
	{
		"name": 'DNA',
		"cells": [
			{
				"route": 'dna-1d-services',
				"image": 'dna-1d-services.png',
				"message": 'Services for studies on DNA sequences',
				"q": 'dna sequence',
			}, {
				"route": 'dna-2d-services',
				"image": 'dna-2d-services.png',
				"message": 'Services for studies on secondary DNA structures',
				"q": 'dna secondary structure',
			}, {
				"route": 'dna-3d-services',
				"image": 'dna-3d-services.png',
				"message": 'Services for studies on DNA structures',
				"q": 'dna structure',
			}, {
				"route": 'dna-xd-services',
				"image": 'dna-xd-services.png',
				"message": 'Services for studies on DNA-omics',
				"q": 'genomics',
			},
		],
	},
	{
		"name": 'RNA',
		"cells": [
			{
				"route": 'rna-1d-services',
				"image": 'rna-1d-services.png',
				"message": 'Services for studies on RNA sequences',
				"q": 'rna sequence',
			}, {
				"route": 'rna-2d-services',
				"image": 'rna-2d-services.png',
				"message": 'Services for studies on secondary RNA structures',
				"q": 'rna secondary structure',
			}, {
				"route": 'rna-3d-services',
				"image": 'rna-3d-services.png',
				"message": 'Services for studies on RNA structures',
				"q": 'rna structure',
			}, {
				"route": 'rna-xd-services',
				"image": 'rna-xd-services.png',
				"message": 'Services for studies on RNA-omics',
				"q": 'rna omics',
			},
		],
	},
	{
		"name": 'Protein',
		"cells": [
			{
				"route": 'protein-1d-services',
				"image": 'protein-1d-services.png',
				"message": 'Services for studies on protein sequences',
				"q": 'protein sequence',
			}, {
				"route": 'protein-2d-services',
				"image": 'protein-2d-services.png',
				"message": 'Services for studies on secondary protein structures',
				"q": 'protein secondary structure',
			}, {
				"route": 'protein-3d-services',
				"image": 'protein-3d-services.png',
				"message": 'Services for studies on protein structures',
				"q": 'protein structure',
			}, {
				"route": 'protein-xd-services',
				"image": 'protein-xd-services.png',
				"message": 'Services for studies on proteomics',
				"q": 'protein omics',
			},
		],
	},
	{
		"name": 'Drugs and other small molecules',
		"cells": [
			{
				"route": 'drug-1d-services',
				"image": 'drug-1d-services.png',
				"message": 'Services for studies on primary structures for small molecules',
				"q": 'small molecule primary sequence',
			}, {
				"route": 'drug-2d-services',
				"image": 'drug-2d-services.png',
				"message": 'Services for studies on secondary structures for small molecules',
				"q": 'small molecule secondary structure',
			}, {
				"route": 'drug-3d-services',
				"image": 'drug-3d-services.png',
				"message": 'Services for studies on structures for small molecules',
				"q": 'small molecule structure',
			}, {
				"route": 'drug-xd-services',
				"image": 'drug-xd-services.png',
				"message": 'Services for studies on small "moleculeomics"',
				"q": 'small molecule omics',
			},
		],
	},
]


class ToolMatrix(APIView):
	"""
	Get a matrix of tool classes
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		query = request.GET
		# Note to self: the API is proxied behind /api/

		# Create a copy
		response = DATA

		# Get count of tools for a query
		def get_count(q: str) -> int:
			query_struct = search.construct_es_query({"q": q})
			result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body=query_struct)
			count = result['hits']['total']['value']
			return count

		for row in response:
			for cell in row['cells']:
				cell['count'] = get_count(cell['q'])

		# Flatten the data to a format angularjs can use
		flat = []
		for row in response:
			flat.append({"name": row['name'], "head": True})
			for cell in row['cells']:
				x = cell
				x["head"] = False
				flat.append(x)

		# Return as JSON
		return Response(flat)
