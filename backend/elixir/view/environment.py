from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from elixir.models import *
from elixir.serializers import *
from elixirapp.environment import is_production

class Environment(APIView):
    """
    Returns the deployment info of the server.
    """

    def get(self, request, format=None):
        return Response("Production" if is_production() else "Development")
