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
		elif ontology == 'topic':
			fields = ['topic.term.raw']
		elif ontology == 'operation':
			fields = ['function.operation.term.raw']
		elif ontology == 'input':
			fields = ['function.input.data.term.raw', 'function.input.format.term.raw']
		elif ontology == 'output':
			fields = ['function.output.data.term.raw', 'function.output.format.term.raw']
		elif ontology == 'credit':
			fields = ['credit.name.raw']
		elif ontology == 'collectionID':
			fields = ['collectionID.raw']
		elif ontology == 'all':
			fields = ['name.raw', 'topic.term.raw', 'function.operation.term.raw', 'function.input.data.term.raw', 'function.input.format.term.raw', 'function.output.data.term.raw', 'function.output.format.term.raw', 'credit.name.raw', 'collectionID.raw']
		else:
			return Response({'detail': 'Unsupported field.'}, status=status.HTTP_404_NOT_FOUND)

		for field in fields:
			query_struct['aggs'][field] = {
				'terms': {
					'field': field,
					'size': 10000
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







