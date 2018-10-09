from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from elixir.models import *
from elixir.serializers import *
from elixir.view.resource import es

class DomainView(APIView):
	"""
	Create or list domains.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

	def get(self, request, format=None):
		if request.user and not request.user.is_anonymous():
			subdomains = Domain.objects.filter(owner=request.user)
			serializer = SubdomainNameSerializer(instance=subdomains, many=True)
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			subdomains = Domain.objects.all()
			serializer = SubdomainNameSerializer(instance=subdomains, many=True)
			return Response(serializer.data, status=status.HTTP_200_OK)


	def post(self, request, format=None):
		payload = request.data
		if not payload:
			return Response({"details": "Missing domain."}, status=status.HTTP_400_BAD_REQUEST)

		struct = {}
		for x in ['title', 'sub_title', 'description', 'domain']:
			y = unicode(payload.get(x, None))
			if len(y) == 0:
				y = None
			struct[x] = y if y != 'None' else None

		if not struct['domain']:
			return Response({"details": "Missing domain."}, status=status.HTTP_400_BAD_REQUEST)

		if struct['domain'] in ['all']:
			return Response({"details": "Domain not allowed."}, status=status.HTTP_400_BAD_REQUEST)

		x = re.match('^[a-zA-Z0-9.~_-]{2,20}$', struct['domain'])
		if not x:
			return Response({"details": "Invalid domain format. Expecting url-safe string between 2 and 20 characters in length."}, status=status.HTTP_400_BAD_REQUEST)

		try:
			d = Domain.objects.get(name__iexact=struct['domain'])
			return Response({"details": "The domain " + struct['domain'] + " is taken."}, status=status.HTTP_400_BAD_REQUEST)
		except Domain.DoesNotExist:
			Domain(name=struct['domain'], title=struct['title'], sub_title=struct['sub_title'], description=struct['description'], owner=request.user).save()
			es.index(index='domains', doc_type='subdomains', body={'domain':struct['domain'], 'title': struct['title'], 'sub_title': struct['sub_title'], 'description': struct['description'], 'resources': []})
		
		return Response(status=status.HTTP_201_CREATED)


	def delete(self, request, format=None):
		payload = request.data
		if not payload:
			return Response({"details": "Missing domain."}, status=status.HTTP_400_BAD_REQUEST)

		domain = unicode(payload.get('domain', None))
		if not domain:
			return Response({"details": "Missing domain."}, status=status.HTTP_400_BAD_REQUEST)

		if domain in ['all']:
			return Response({"details": "Domain not allowed."}, status=status.HTTP_400_BAD_REQUEST)
		try:
			d = Domain.objects.get(name__iexact=domain)
			if d.owner != request.user:
				return Response({"details": "You are not the owner of this domain."}, status=status.HTTP_401_UNAUTHORIZED)
			d.domainresource_set.all().delete()
			d.delete()
			result = es.search(index='domains', body={'size': 10,'query': {'bool': {'must': [{'match': {'domain': {'query': domain}}}]}}})
			es.delete(index='domains', doc_type='subdomains', id=result['hits']['hits'][0]['_id'])

		except Domain.DoesNotExist:
			return Response({"details": "Domain does not exist."}, status=status.HTTP_400_BAD_REQUEST)
			
		return Response(status=status.HTTP_200_OK)


class DomainResourceView(APIView):
	"""
	Add/remove or list tools for a domain.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

	def get(self, request, domain='all', format=None):
		query_dict = request.GET
		size = query_dict.get('size', 10000)

		if domain != 'all':
			result = es.search(index='domains', body={'size': size,'query': {'bool': {'must': [{'match': {'domain': {'query': domain}}}]}}})
			count = result['hits']['total']
			if count > 0:
				result = [el['_source'] for el in result['hits']['hits']][0]
				return Response({'count': count,
						 'data': result}, status=200)
			else:
				return Response(status=status.HTTP_404_NOT_FOUND)
		else:
			elastic_domain_query_struct = {
				"query" : {
					"match_all" : {}
				}
			}
			result = es.search(index='domains', body=elastic_domain_query_struct)
			count = result['hits']['total']
			if count > 0:
				result = [el['_source'] for el in result['hits']['hits']]
				return Response({'count': count,
						 'data': result}, status=200)
			
		return Response(status=status.HTTP_404_NOT_FOUND)
		

	def put(self, request, domain=None, format=None):
		# cleanup and verification
		if not domain:
			return Response({"details": "Missing domain."}, status=status.HTTP_400_BAD_REQUEST)
		if domain == 'all':
			return Response({"details": "This domain not allowed."}, status=status.HTTP_400_BAD_REQUEST)

		payload = request.data

		if not payload:
			return Response({"details": "Expected payload."}, status=status.HTTP_400_BAD_REQUEST)

		if not isinstance(payload, dict):
			return Response({"details": "Invalid payload format."}, status=status.HTTP_400_BAD_REQUEST)

		if 'resources' not in payload:
			return Response({"details": "Expected payload: resources."}, status=status.HTTP_400_BAD_REQUEST)

		payload_resources = payload.get('resources', None)

		struct = {}
		for x in ['title', 'sub_title', 'description']:
			y = unicode(payload.get(x, None))
			if len(y) == 0:
				y = None
			struct[x] = y if y != 'None' else None
			
		# check the payload
		if not isinstance(payload_resources, list):
			return Response({"details": "Invalid payload format."}, status=status.HTTP_400_BAD_REQUEST)


		for el in payload_resources:
			if not isinstance(el, dict):
				return Response({"details": "Invalid payload format."}, status=status.HTTP_400_BAD_REQUEST)
			biotoolsID = el.get('biotoolsID', None)
			if not biotoolsID:
				return Response({"details": "Missing id for one of the resources."}, status=status.HTTP_400_BAD_REQUEST)
			try:
				r = Resource.objects.get(biotoolsID__iexact=biotoolsID, visibility=1)
			except Resource.DoesNotExist:
				return Response({"details": "Could not locate resource with id " + str(biotoolsID) + " ."}, status=status.HTTP_400_BAD_REQUEST)


		d = None
		try:
			d = Domain.objects.get(name__iexact=domain)
			if d.owner != request.user:
				return Response({"details": "You are not the owner of this domain."}, status=status.HTTP_401_UNAUTHORIZED)

			##### update & save domain attribute here
			d.title = struct['title']
			d.sub_title = struct['sub_title']
			d.description = struct['description']
			d.save()
			##### end


			d.domainresource_set.all().delete()
			result = es.search(index='domains', body={'size': 10,'query': {'bool': {'must': [{'match': {'domain': {'query': domain}}}]}}})
			count = result['hits']['total']
			
			if count > 0:
				for el in payload_resources:
					r = None
					biotoolsID = el.get('biotoolsID', None)
					try:
						r = Resource.objects.get(biotoolsID__iexact=el['biotoolsID'], visibility=1)
						DomainResource(biotoolsID=r.biotoolsID, name=r.name, domain=d).save()
					except Resource.DoesNotExist:
						return Response({"details": "Could not find resource with id " + el['biotoolsID'] + "."}, status=status.HTTP_400_BAD_REQUEST)
				es.index(index='domains', doc_type='subdomains', body={'domain': d.name, 'title': d.title, 'sub_title': d.sub_title, 'description': d.description, 'resources': map(lambda x: {'name': x.name, 'biotoolsID': x.biotoolsID}, d.domainresource_set.all())}, id=result['hits']['hits'][0]['_id'])
		except Domain.DoesNotExist:
			raise Http404

		return Response(status=status.HTTP_200_OK)


	def delete(self, request, domain=None, format=None):	
		if not domain:
			payload = request.data
			if not payload:
				return Response({"details": "Missing payload."}, status=status.HTTP_400_BAD_REQUEST)

			domain = payload.get('domain', None)
			if not domain:
				return Response({"details": "Missing domain."}, status=status.HTTP_400_BAD_REQUEST)

		if domain in ['all']:
			return Response({"details": "Domain not allowed."}, status=status.HTTP_400_BAD_REQUEST)
		try:
			d = Domain.objects.get(name__iexact=domain)
			if d.owner != request.user:
				return Response({"details": "You are not the owner of this domain."}, status=status.HTTP_401_UNAUTHORIZED)
			d.domainresource_set.all().delete()
			d.delete()
			result = es.search(index='domains', body={'size': 10,'query': {'bool': {'must': [{'match': {'domain': {'query': domain}}}]}}})
			es.delete(index='domains', doc_type='subdomains', id=result['hits']['hits'][0]['_id'])
		except Domain.DoesNotExist:
			return Response({"details": "Domain does not exist."}, status=status.HTTP_400_BAD_REQUEST)
			
		return Response(status=status.HTTP_200_OK)