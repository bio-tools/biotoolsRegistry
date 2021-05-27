from elixir.models import EditPermission, EditPermissionAuthor, Resource
from elixir.permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status, generics, serializers
from rest_framework.exceptions import ParseError
from django.contrib.auth.models import User

#######################################################################################################################
# Views
#######################################################################################################################

class EditPermissionsQueryError(Exception):
	pass

class EditPermissions(APIView):
	"""
	Set and edit permissions for a specified resource.
	"""
	permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)


	# Operations
	def extractGETQueryParameters(self, query):
		try:
			return {"id": query["id"]}
		except Exception as e:
			raise ParseError("This request requires the following pa rameter: 'id' (a resource id).")

	def extractPUTQueryParameters(self, query):
		try:
			return {"id": query["id"], "permission": query["permission"]}
		except Exception as e:
			raise ParseError("This request requires the following pa rameters: 'id' (a resource id), permission (a type of a permission to be assigned).")

	def getResource(self, id):
		obj = Resource.objects.filter(visibility=1).get(biotoolsID__iexact=id)
		self.check_object_permissions(self.request, obj)
		return obj

	def setEditPermission(self, resource, permissionType):
		editpermission = resource.editPermission
		serializer = EditPermissionSerializer(editpermission, data={"type": permissionType}, partial=True)
		if serializer.is_valid():
			serializer.save()
		else:
			raise ParseError(serializer.errors['general_errors'][0])


	# Request handling
	def put(self, request):
		# Check and extract the required parameters.
		parameters = self.extractPUTQueryParameters(request.data)
		resource = self.getResource(parameters["id"])
		permission = parameters["permission"]
		# Update permissions in the database.
		self.setEditPermission(resource, permission)
		return Response({"detail": "Edit permissions changed sucessfully."})

	def get(self, request):
		# Check and extract the required parameters.
		parameters = self.extractGETQueryParameters(request.GET)
		resource = self.getResource(parameters["id"])
		editpermission = resource.editPermission
		return Response({'id': resource.biotoolsId, 'type': editpermission.type})
