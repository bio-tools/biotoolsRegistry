from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from elixir.models import *
from elixir.serializers import *
from elixir import stats

class Stats(APIView):
	"""
	Retrieve stats for use with various widgets.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)
	
	def get(self, request, format=None):
		query_dict = request.GET
		query_limit = int(query_dict.get('limit', 10))
		statsInfo = stats.StatsInfo()
		return Response(statsInfo.statsData(query_limit), status=status.HTTP_200_OK)

class TotalEntriesStats(APIView):
	"""
	Retrieve total entries stats for use with various widgets.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)
	
	def get(self, request, format=None):
		query_dict = request.GET
		days_limit = int(query_dict.get('months', 24))
		statsInfo = stats.StatsInfo()
		return Response(statsInfo.totalEntriesForLast(days_limit), status=status.HTTP_200_OK)

class AnnotationCountStats(APIView):
	"""
	Retrieve total annotations count stats for use with various widgets.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)
	
	def get(self, request, format=None):
		query_dict = request.GET
		days_limit = int(query_dict.get('months', 24))
		statsInfo = stats.StatsInfo()
		return Response(statsInfo.totalAnnotationsCountForLast(days_limit), status=status.HTTP_200_OK)

class UserStats(APIView):
	"""
	Retrieve user stats for use with various widgets.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)
	
	def get(self, request, format=None):
		statsInfo = stats.StatsInfo()
		return Response(statsInfo.userGrowthByMonth(), status=status.HTTP_200_OK)