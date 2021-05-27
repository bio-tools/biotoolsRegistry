from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from elixir.models import *
from elixir.serializers import *

class WorkflowDetailView(APIView):
	"""
	Create a new workflow
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)

	def get(self, request, id, format=None):
		workflow = Workflow.objects.get(biotoolsID=id)
		serializer = WorkflowSerializer(workflow)
		return Response(serializer.data, status=status.HTTP_200_OK)


class WorkflowView(APIView):
	"""
	Create a new workflow
	"""
	permission_classes = (IsAuthenticatedOrReadOnly,)

	def post(self, request, format=None):
		serializer = WorkflowSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save();
		return Response(serializer.data, status=status.HTTP_200_OK)

	def get(self, request, format=None):
		workflows = Workflow.objects.all()
		serializer = WorkflowSerializer(workflows, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
