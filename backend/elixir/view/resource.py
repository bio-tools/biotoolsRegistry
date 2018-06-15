from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from rest_framework.settings import api_settings
import elixir.search as search
import elixir.logging as logging
from django.conf import settings
from rest_framework.response import Response
from elasticsearch import Elasticsearch
from elixir.models import *
from elixir.serializers import *
from django.http import Http404

es = Elasticsearch([{'host':'localhost','port':9200}])

class ResourceList(APIView):
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

		result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body=query_struct)
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
				domain_resources = set(map(lambda x: (x['textId']), domain_result['resources']))
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

	def post(self, request, format=None):
		serializer = ResourceSerializer(data=request.data)

		if serializer.is_valid():

			serializer.save(owner=request.user)
			issue_function(Resource.objects.get(textId=serializer.data['id'], visibility=1), request.user)

			es.index(index=settings.ELASTIC_SEARCH_INDEX, doc_type='tool', body=serializer.data)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DisownResourceView(APIView):
	"""
	Disown the request
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

	def get_object(self, textId):
		try:
			obj = Resource.objects.filter(visibility=1).get(textId__iexact=textId)
			self.check_object_permissions(self.request, obj)
			return obj
		except Resource.DoesNotExist:
			raise Http404

	def get_disowned_user(self):
		return User.objects.get(username__iexact="admin")
 
	def post(self, request, textId, format=None):
		resource = self.get_object(textId)
		resource.owner = self.get_disowned_user()
		resource.save()
		return Response({"detail": "You have successfully disowned your entry."}, status=status.HTTP_200_OK)


class ResourceRequestView(APIView):
	"""
	Create or obtain resource requests.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)

	def put(self, request, format=None):
		serializerData = request.data
		serializerData['username'] = request.user.username
		serializerData['requestId'] = uuid.uuid4()
		serializer = ResourceRequestSerializer(data=serializerData)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request, format=None):
		my_requests = ResourceRequest.objects.filter(user=request.user)
		if request.user.is_superuser == True:
			received_requests = ResourceRequest.objects.all()
		else:
			received_requests = ResourceRequest.objects.filter(Q(resource__owner=request.user) | Q(completedBy=request.user))
		received_requests_serializer = ResourceRequestSerializer(instance=received_requests, many=True)
		my_requests_serializer = ResourceRequestSerializer(instance=my_requests, many=True)
		return Response({'requests': {'received': received_requests_serializer.data, 'sent': my_requests_serializer.data}}, status=status.HTTP_200_OK)


class ProcessResourceRequest(APIView):
	"""
	Retrieve, update or delete a resource instance.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, CanConcludeResourceRequest)

	def post(self, request, format=None):
		if not 'requestId' in request.data: 
			return Response({"detail": "Request could not be completed. Missing parameter: 'requestId'."}, status=status.HTTP_400_BAD_REQUEST)
		if not 'accept' in request.data: 
			return Response({"detail": "Request could not be completed. Missing parameter: 'accept'."}, status=status.HTTP_400_BAD_REQUEST)
		try:
			resourceRequest = ResourceRequest.objects.get(requestId=request.data['requestId'])
		except:
   			return Response({"detail": "No active requests with a specified 'requestId' could be found."}, status=status.HTTP_404_NOT_FOUND)
   		self.check_object_permissions(self.request, resourceRequest)
   		if resourceRequest.completed == True: 
			return Response({"detail": "Request has already been concluded."}, status=status.HTTP_400_BAD_REQUEST)
   		serializer = ResourceRequestConcludeSerializer(resourceRequest, data=request.data, context={'user': request.user})
   		if serializer.is_valid():
			serializer.save()
		responseSerializer = ResourceRequestSerializer(resourceRequest)
		return Response(responseSerializer.data, status=status.HTTP_200_OK)


class ResourceDetail(APIView):
	"""
	Retrieve a specific resource
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, HasEditPermissionToEditResourceOrReadOnly)

	def get_object(self, textId):
		try:
			obj = Resource.objects.filter(visibility=1).get(textId__iexact=textId)
			self.check_object_permissions(self.request, obj)
			return obj
		except Resource.DoesNotExist:
			raise Http404

	def check_for_edit_permissions(self, request, resource):
		if request.user == resource.owner or request.user.is_superuser:
			return True
		return False

	def check_editing_permissions(self, request, resource):
		if 'editPermission' in request.data:
			if 'type' in request.data['editPermission'] and resource.editPermission.type != request.data['editPermission']['type']:
				return True
			authors = set(resource.editPermission.authors.all().values_list('user__username', flat=True))
			if not 'authors' in request.data['editPermission']:	
				return False
			authorsRequest = set(request.data['editPermission']['authors'])
			if authors != authorsRequest:
				return True
		return False

	def get(self, request, textId, format=None):
		resource = self.get_object(textId)
		serializer = ResourceSerializer(resource)
		return Response(serializer.data)

	# the update is actually creating a brand new resource, copying a few key information, and setting the visibility of the original to 0
	def put(self, request, textId, format=None):
		resource = self.get_object(textId)
		canEditPermissions = self.check_for_edit_permissions(request, resource)
		isEditingPermissions = self.check_editing_permissions(request, resource)
		if canEditPermissions == False and isEditingPermissions == True:
			return Response({"detail": "Only the owner can edit permissions for a specified resource."}, status=status.HTTP_401_UNAUTHORIZED)
		# Copy permissions from the esisting resource in case not specified.
		if isEditingPermissions == False:
			permissionSerializer = EditPermissionSerializer(resource.editPermission)
			request.data['editPermission'] = permissionSerializer.data
		serializer = ResourceUpdateSerializer(data=request.data)

		if serializer.is_valid():
			# setting the visibility of the current resource to 0
			resource.visibility = 0
			resource.save()
			# copying the textual id and additionDate to the newly created resource
			serializer.save(textId=resource.textId, additionDate=resource.additionDate, owner=resource.owner)
			issue_function(Resource.objects.get(textId=serializer.data['id'], visibility=1), str(resource.owner))
			
			# update the existing resource in elastic
			result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body={
				"query": {
					"bool" : {
						"must": [
							{
								"match": {
									"id": resource.textId.lower()
								}
							}
						]
					}
				}
			})
			count = result['hits']['total']
			if count == 1:
				es.index(index=settings.ELASTIC_SEARCH_INDEX, doc_type='tool', body=serializer.data, id=result['hits']['hits'][0]['_id'])

			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, textId, format=None):
		resource = self.get_object(textId)
		# setting the visibility of the current resource to 0
		resource.visibility = 0
		resource.save()

		result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body={
			"query": {
				"bool" : {
					"must": [
						{
							"match": {
								"id": resource.textId.lower()
							}
						}
					]
				}
			}
		})
		count = result['hits']['total']
		if count == 1:
			es.delete(index=settings.ELASTIC_SEARCH_INDEX, doc_type='tool', id=result['hits']['hits'][0]['_id'])

		return Response(status=status.HTTP_204_NO_CONTENT)

# class ResourceDetailVersionList(APIView):
# 	"""
# 	Retrieve a list of versions for a resource
# 	"""
# 	# permission_classes = (IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly)

# 	def get_list(self, textId):
# 		try:
# 			obj = Resource.objects.filter(visibility=1, textId__iexact=textId)
# 			self.check_object_permissions(self.request, obj)
# 			return obj
# 		except Resource.DoesNotExist:
# 			raise Http404

# 	def get(self, request, textId, version=None, format=None):
# 		resource = self.get_list(textId)
# 		serializer = VersionLatestSerializer(instance=resource, many=True)
# 		return Response(serializer.data)

class ResourceCreateValidator(APIView):
	"""
	Validate creating a resource.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)


	def post(self, request, format=None):
		serializer = ResourceSerializer(data=request.data)
		if serializer.is_valid():
			return Response(serializer.validated_data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResourceUpdateValidator(APIView):
	"""
	Validate updating a resource.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, HasEditPermissionToEditResourceOrReadOnly,)


	def get_object(self, textId):
		try:
			obj = Resource.objects.filter(visibility=1).get(textId__iexact=textId)
			self.check_object_permissions(self.request, obj)
			return obj
		except Resource.DoesNotExist:
			raise Http404

	def put(self, request, textId, format=None):
		resource = self.get_object(textId)
		serializer = ResourceUpdateSerializer(data=request.data)
		if serializer.is_valid():
			return Response(serializer.validated_data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		