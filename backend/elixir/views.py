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

from allauth.socialaccount.providers.orcid.views import OrcidOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, SocialConnectView


class CustomOAuth2Client(OAuth2Client):
    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        _scope,  # This is fix for incompatibility between django-allauth==65.3.1 and dj-rest-auth==7.0.1
        scope_delimiter=" ",
        headers=None,
        basic_auth=False,
    ):
        super().__init__(
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            scope_delimiter,
            headers,
            basic_auth,
        )

# ORCID 

class OrcidLogin(SocialLoginView):
	adapter_class = OrcidOAuth2Adapter
	callback_url = "http://127.0.0.1/orcid/callback/"
	client_class = CustomOAuth2Client

class OrcidConnect(SocialConnectView):
	adapter_class = OrcidOAuth2Adapter
	callback_url = 'http://127.0.0.1/orcid/callback/'
	client_class = CustomOAuth2Client

# Github

class GitHubLogin(SocialLoginView):
	adapter_class = GitHubOAuth2Adapter
	callback_url = "http://127.0.0.1/github/callback/"
	client_class = CustomOAuth2Client

class GitHubConnect(SocialConnectView):
	adapter_class = GitHubOAuth2Adapter
	callback_url = 'http://127.0.0.1/github/callback/'
	client_class = CustomOAuth2Client


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
