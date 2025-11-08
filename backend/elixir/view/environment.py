from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from elixir.models import *
from elixir.permissions import (
    CanConcludeResourceRequest,
    HasEditPermissionToEditResourceOrReadOnly,
    IsOwnerOrReadOnly,
    IsStaffOrReadOnly,
)
from elixir.serializers import *


class Environment(APIView):
    """
    Returns the deployment info of the server.
    """

    def get(self, request, format=None):
        if settings.DEPLOYMENT == "dev":
            return Response("Development")
        return Response("Production")
