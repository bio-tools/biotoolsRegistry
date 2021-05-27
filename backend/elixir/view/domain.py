from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsDomainOwnerOrReadOnly, IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from elixir.models import *
from elixir.serializers import *
from elixir.view.resource import es
from django.http import Http404
from rest_framework.validators import UniqueValidator
from elasticsearch import NotFoundError as ESNotFoundError

# Perhaps there should be some domains that can't be deleted... or only deleted by superusers
# Maybe add this in a settings file
NOT_DELETABLE_DOMAINS = ['all']


def is_superuser(user):
	return User.objects.get(username=user).is_superuser == 1

class DomainView(APIView):
	"""
	Create or list domains.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, IsDomainOwnerOrReadOnly, )


	# get a list of all domains (domain name/id and the number of resources in the domain)
	# this is based on the type of user (anonymous, logged in, superuser)
	def get(self, request, format=None):
		if request.user and not request.user.is_anonymous and not(is_superuser(request.user)):
			subdomains = Domain.objects.filter(owner=request.user, visibility=1)
			serializer = SubdomainNameSerializer(instance=subdomains, many=True)
			return Response(serializer.data, status=status.HTTP_200_OK)
		elif request.user and not request.user.is_anonymous and is_superuser(request.user):
			subdomains = Domain.objects.filter(visibility=1)
			serializer = SubdomainNameSerializer(instance=subdomains, many=True)
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			subdomains = Domain.objects.filter(visibility=1)
			serializer = SubdomainNameSerializer(instance=subdomains, many=True)
			return Response(serializer.data, status=status.HTTP_200_OK)


	def post(self, request, format=None):

		serializer = DomainSerializer(data=request.data, context={'request':request,"request_type":"POST"})

		# Need to check somewhere that those resources do indeed exist
		# Also we get DomainResource names from the original resource , rather than letting the user add names willy-nilly

		if serializer.is_valid():
			serializer.save(owner=request.user)
			
			es.index(
				index='domains', 
				doc_type='_doc', 
				id=serializer.validated_data['name'], 
				body=serializer.data
			)
			return Response(serializer.data, status=status.HTTP_201_CREATED)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DomainResourceView(APIView):
	"""
	Add/remove or list tools for a domain.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, IsDomainOwnerOrReadOnly, )


	def get_object(self, name):
		try:
			obj = Domain.objects.get(name=name, visibility=1)
			self.check_object_permissions(self.request, obj)
			return obj
		except Domain.DoesNotExist:
			raise Http404

	def get(self, request, domain, format=None):
		# need to do something with this, count doesn't make sense here, should be a different URL
		
		if domain.lower() == 'all':
			elastic_domain_query_struct = {
				"size": 10000,
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
			else:
				return Response(status=status.HTTP_404_NOT_FOUND)

		else:
			# try:
			# 	result = es.get(index='domains',doc_type='_doc', id=domain.lower())
			# 	return Response(
			# 		{
			# 			'count': 1,
			# 			'data': result['_source']
			# 		}
					
			# 	)
			# except ESNotFoundError:
			# 	return Response(status=status.HTTP_404_NOT_FOUND)
			d = self.get_object(domain)
			result = DomainSerializer(d)
			return Response(
			 		{
			 			'count': 1,
			 			'data': result.data
			 		}
			)

	def put(self, request, domain=None, format=None):	
		# Updating a domain creates a new domain object and the old one gets a visibility of 0

		serializer = DomainUpdateSerializer(data=request.data, context={'request':request,"request_type":"PUT"})

		if serializer.is_valid():

			old_domain = self.get_object(serializer.validated_data['name'])
			old_domain.visibility = 0
			old_domain.save()

			# serializer.save(owner=old_domain.owner, additionDate=old_domain.additionDate)
			
			serializer.save(owner=old_domain.owner)
			
			es.index(
				index='domains', 
				doc_type='_doc', 
				id=serializer.validated_data['name'], 
				body=serializer.data
			)

			return Response(serializer.data, status=status.HTTP_200_OK)
		
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	def delete(self, request, domain, format=None):
		if not(request.user.is_superuser) and domain.strip().lower() in NOT_DELETABLE_DOMAINS:
			return Response({"detail": "You do not have permission to delete this domain."}, status=status.HTTP_403_FORBIDDEN)

		d = self.get_object(domain)
		d.visibility = 0
		d.save()

		try:
			es.delete(index='domains', doc_type='_doc', id=domain.lower())
		except ESNotFoundError:
			# if it gets here it means then it set the visibility = 1 and if it can't find the document in the index
			# it's kind of an issue but not really
			# return 204 just to have a bit of a difference
			return Response(status=status.HTTP_204_NO_CONTENT)

		return Response(status=status.HTTP_200_OK)