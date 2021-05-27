from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from elixir.models import *
from elixir.serializers import *

class UserList(APIView):
	"""
	List usernames in the registry.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		query_dict = request.GET
		search_term = ''
		search_limit = 10
		if query_dict:
			if 'term' in query_dict:
				search_term = query_dict['term']
			if 'limit' in query_dict:
				search_limit = query_dict['limit']
		users = User.objects.filter(username__icontains=search_term)[:search_limit]
		serializer = UserNameSerializer(users, many=True)
		return Response(serializer.data)