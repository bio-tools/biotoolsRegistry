from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from elixir.serializers import *


class ToolList(APIView):
	"""
	Get a compact list of tools.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		query = request.GET
		# Filtering
		filter_query = {}
		if query.get('name'):
			filter_query["name__icontains"] = query.get('name')
		elif query.get('biotoolsID'):
			filter_query["biotoolsID__icontains"] = query.get('biotoolsID')
		elif query.get('collectionId'):
			filter_query["collectionID__name__icontains"] = query.get('collectionId')
		elif query.get('credit'):
			filter_query["credit__name__icontains"] = query.get('credit')
		elif query.get('contact'):
			filter_query["contact__name__icontains"] = query.get('contact')
		# Data access
		if len(filter_query) == 0:
			resources = Resource.objects.filter(visibility=1).order_by('-lastUpdate').all()
		else:
			resources = Resource.objects.filter(visibility=1).filter(**filter_query).order_by('-lastUpdate').all()
		serializer = ToolListResourceSerializer(instance=resources, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
