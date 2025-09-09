import json, random, datetime, time, re, uuid
import elixir.search as search
import elixir.elixir_logging as elixir_logging
import elixir.stats as stats
from rest_framework import status, generics
from django.utils.decorators import method_decorator
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from elixir.models import Resource, Function, Domain
from django.http import Http404
from elixir.serializers import *
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes, parser_classes
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from elasticsearch import Elasticsearch
from collections import Counter
from django.db.models import Count
from elixirapp import settings
from django.db.models import Q
from pprint import pprint

from elixir.view.resource import *
from elixir.view.domain import *
from elixir.view.stats import *
from elixir.view.workflow import *
from elixir.view.issues import *
from elixir.view.user import *
from elixir.view.environment import *
from elixir.view.tools import *
from elixir.view.edam import *
from elixir.view.matrix import *


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
