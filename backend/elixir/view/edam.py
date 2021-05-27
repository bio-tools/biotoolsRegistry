from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from elixir.models import *
from elixir.serializers import *
import elixir.search as search
from elixir.view.resource import es

class FunctionList(APIView):
	"""
	List all functions that have beed added to resources.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)


	def get(self, request, format=None):
		functions = Function.objects.filter(resource__visibility=1)
		serializer = FunctionSerializer(functions, many=True)
		return Response(serializer.data)

class UsedTermsList(APIView):
	"""
	List terms used in the registry.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)


	def get(self, request, ontology, format=None):
		query_struct = search.construct_es_query(request.GET)
		del query_struct['sort']
		query_struct['aggs'] = {}

		fields = []
		values = []

		if ontology == 'name':
			fields = ['name.raw']
		elif ontology == 'biotoolsID':
			fields = ['biotoolsID']
		elif ontology == 'topic':
			fields = ['topic.term.raw']
		elif ontology == 'operation':
			fields = ['function.operation.term.raw']
		elif ontology == 'input':
			fields = ['function.input.data.term.keyword', 'function.input.format.term.keyword']
		elif ontology == 'output':
			fields = ['function.output.data.term.keyword', 'function.output.format.term.keyword']
		elif ontology == 'credit':
			fields = ['credit.name.keyword']
		elif ontology == 'collectionID':
			fields = ['collectionID.raw']
		elif ontology == 'toolType':
			fields = ['toolType.raw']
		elif ontology == 'language':
			fields = ['language.raw']
		elif ontology == 'accessibility':
			fields = ['accessibility.keyword']
		elif ontology == 'cost':
			fields = ['cost.raw']
		elif ontology == 'license':
			fields = ['license.raw']
		elif ontology == 'all':
			fields = ['topic.term.raw', 'function.operation.term.raw', 'name.raw', 'function.input.data.term.keyword', 'function.input.format.term.keyword', 'function.output.data.term.keyword', 'function.output.format.term.keyword', 'toolType.raw', 'language.raw', 'accessibility.keyword', 'cost.raw', 'license.raw', 'credit.name.keyword', 'collectionID.raw','name.raw']
		else:
			return Response({'detail': 'Unsupported field.'}, status=status.HTTP_404_NOT_FOUND)

		for field in fields:
			query_struct['aggs'][field] = {
				'terms': {
					'field': field,
					'size': 50000
				}
			}

		result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body=query_struct)

		for field in fields:
			values += [x['key'] for x in result['aggregations'][field]['buckets']]

		return Response({'data': set(values)})


class OntologyDetail(APIView):
	"""
	Retrieve ontology tree for use with various widgets.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)


	def get_object(self, name):
		try:
			return Ontology.objects.get(name=name)
		except Resource.DoesNotExist:
			raise Http404

	def get(self, request, name, format=None):
		ontology = self.get_object(name)
		# Convert object to JSON
		JSONCompliantStruct = {}
		JSONCompliantStruct['data'] = json.loads(ontology.data)
		return Response(JSONCompliantStruct, status=status.HTTP_200_OK)







