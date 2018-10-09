from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from rest_framework.response import Response
from elixir.models import *
from elixir.serializers import *
from rest_framework.settings import api_settings
import elixir.logging as logging
import elixir.search as search
from elixir.view.resource import es

class LegacyResourceDetail(APIView):
	"""
	Retrieve a specific resource
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, HasEditPermissionToEditResourceOrReadOnly)

	def get_object(self, biotoolsID):
		try:
			obj = Resource.objects.filter(visibility=1).get(biotoolsID__iexact=biotoolsID)
			self.check_object_permissions(self.request, obj)
			return obj
		except Resource.DoesNotExist:
			raise Http404

	def get(self, request, biotoolsID, format=None):
		resource = self.get_object(biotoolsID)
		serializer = LegacyResourceSerializer(resource)
		return Response(serializer.data)

class LegacyResourceList(APIView):
	"""
	List all resources, or create a new resource.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)


	def get(self, request, format=None):
		query_dict = request.GET
		size = api_settings.PAGE_SIZE
		page = int(query_dict.get('page', '1'))

		searchLogger = logging.SearchLogger(query_dict)
		searchLogger.commit()

		domain = query_dict.get('domain', None)
		domain_resources = []
		query_struct = search.construct_es_query(query_dict)

		result = es.search(index=settings.ELASTIC_SEARCH_INDEX_V2, body=query_struct)
		count = result['hits']['total']
		results = [el['_source'] for el in result['hits']['hits']]

		# check if page is valid
		if (not results and count > 0):
			return Response({"detail": "Invalid page. That page contains no results."}, status=status.HTTP_404_NOT_FOUND)

		if domain:
			domain_result = es.search(index='domains', body={'size': 10000,'query': {'bool': {'must': [{'match': {'domain': {'query': domain}}}]}}})
			domain_count = domain_result['hits']['total']
			if domain_count > 0:
				domain_result = [el['_source'] for el in domain_result['hits']['hits']][0]
				domain_resources = set(map(lambda x: (x['id']), domain_result['resources']))
				# get touples of returned tools
				returned_resource = set(map(lambda x: (x['id']), results))

				if len(list(set(query_dict.keys()) - set([u'sort', u'domain', u'ord', u'page']))) == 0:
					diff = list(domain_resources)
				else:
					diff = list(returned_resource & domain_resources)

				if len(diff) > 0:
					count = len(diff)
					if len(diff) > 1000:
						results = []
						for i in range(0,len(diff) / 1000):
							rest = len(diff) if len(diff) <= i*1000+1000 else i*1000+1000
							query_struct['query'] = {'bool': {'should': map(lambda x: {'bool': {'must': [{'match': {'id': {'query': x[0]}}}]}}, diff[i*1000:rest])}}
							result = es.search(index='elixir', body=query_struct)
							sub_results = [el['_source'] for el in result['hits']['hits']]
							results += sub_results
					else:
						query_struct['query'] = {'bool': {'should': map(lambda x: {'bool': {'must': [{'match': {'id': {'query': x}}}]}}, diff)}}
						result = es.search(index='elixir', body=query_struct)
						count = result['hits']['total']
						results = [el['_source'] for el in result['hits']['hits']]
				else:
					return Response({'count': 0,
						 'next': None if (page*size >= count) else "?page=" + str(page + 1),
						 'previous': None if page == 1 else "?page=" + str(page - 1),
						 'list': []}, status=200)
			else:
				return Response({'count': 0,
					'next': None if (page*size >= count) else "?page=" + str(page + 1),
				 	'previous': None if page == 1 else "?page=" + str(page - 1),
				 	'list': []}, status=200)

		return Response({'count': count,
						 'next': None if (page*size >= count) else "?page=" + str(page + 1),
						 'previous': None if page == 1 else "?page=" + str(page - 1),
						 'list': results}, status=200)

	