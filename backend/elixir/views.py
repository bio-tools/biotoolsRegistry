import datetime
import json
import random
import re
import time
import uuid
from collections import Counter
from pprint import pprint

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import Http404
from django.utils.decorators import method_decorator
from elasticsearch import Elasticsearch
from rest_framework import generics, status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    parser_classes,
    permission_classes,
    renderer_classes,
)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

import elixir.elixir_logging as elixir_logging
import elixir.search as search
import elixir.stats as stats
from elixir.models import Domain, Function, Resource
from elixir.permissions import (
    CanConcludeResourceRequest,
    HasEditPermissionToEditResourceOrReadOnly,
    IsOwnerOrReadOnly,
    IsStaffOrReadOnly,
)
from elixir.serializers import *
from elixir.view.domain import *
from elixir.view.edam import *
from elixir.view.environment import *
from elixir.view.issues import *
from elixir.view.resource import *
from elixir.view.stats import *
from elixir.view.tools import *
from elixir.view.user import *
from elixir.view.workflow import *
from elixirapp import settings


def issue_function(resource, user):
    # check for issues
    pass
    # EDAMTopicIssue([resource], user=user).report()
    # EDAMOperationIssue([resource], user=user).report()
    # EDAMDataIssue([resource], user=user).report()
    # EDAMFormatIssue([resource], user=user).report()
    # NoLicenseIssue([resource], user=user).report()
    # NoContactIssue([resource], user=user).report()
    # NoTOSIssue([resource], user=user).report()
