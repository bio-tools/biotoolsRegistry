from django.contrib.auth.models import User
from rest_framework import generics, serializers, status
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from elixir.models import EditPermission, EditPermissionAuthor, Resource
from elixir.permissions import IsOwnerOrReadOnly

#######################################################################################################################
# Views
#######################################################################################################################


class EditPermissionsQueryError(Exception):
    pass


class EditPermissions(APIView):
    """
    Set and edit permissions for a specified resource.
    """

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )

    # Operations
    def extractGETQueryParameters(self, query):
        try:
            return {"id": query["id"]}
        except Exception as e:
            raise ParseError(
                "This request requires the following parameter: 'id' (a resource id)."
            )

    def extractPUTQueryParameters(self, query):
        try:
            return {"id": query["id"], "permission": query["permission"]}
        except Exception as e:
            raise ParseError(
                "This request requires the following parameters: 'id' (a resource id), permission (a type of a permission to be assigned)."
            )

    def getResource(self, id):
        obj = Resource.objects.filter(visibility=1).get(biotoolsID__iexact=id)
        self.check_object_permissions(self.request, obj)
        return obj

    def setEditPermission(self, resource, permissionType):
        editpermission = resource.editPermission
        serializer = EditPermissionSerializer(
            editpermission, data={"type": permissionType}, partial=True
        )
        if serializer.is_valid():
            serializer.save()
        else:
            raise ParseError(serializer.errors["general_errors"][0])

    # Request handling
    def put(self, request):
        # Check and extract the required parameters.
        parameters = self.extractPUTQueryParameters(request.data)
        resource = self.getResource(parameters["id"])
        permission = parameters["permission"]
        # Update permissions in the database.
        self.setEditPermission(resource, permission)
        return Response({"detail": "Edit permissions changed successfully."})

    def get(self, request):
        # Check and extract the required parameters.
        parameters = self.extractGETQueryParameters(request.GET)
        resource = self.getResource(parameters["id"])
        editpermission = resource.editPermission
        return Response({"id": resource.biotoolsId, "type": editpermission.type})
