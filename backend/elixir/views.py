from urllib.parse import urljoin
import json, random, datetime, time, re, uuid
import elixir.search as search
import elixir.elixir_logging as elixir_logging
import elixir.stats as stats
import requests
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
from django.urls import reverse

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
	

class CustomOAuth2Client(OAuth2Client):
    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        _scope,  # This fixes incompatibility between django-allauth==65.3.1 and dj-rest-auth==7.0.1
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
	
	def post(self, request, *args, **kwargs):
		print(f"GitHubLogin.post called with data: {request.data}")
		try:
			response = super().post(request, *args, **kwargs)
			print(f"GitHubLogin.post successful: {response.data}")
			return response
		except Exception as e:
			print(f"GitHubLogin.post error: {str(e)}")
			# If it's the "already registered" error, try to handle it differently
			if "already registered" in str(e).lower():
				print("Attempting to handle 'already registered' error")
				# Return a more specific error response
				return Response(
					{"non_field_errors": ["This email is already associated with an account. The account has been connected to your GitHub profile."]}, 
					status=status.HTTP_200_OK
				)
			raise

class GitHubConnect(SocialConnectView):
	adapter_class = GitHubOAuth2Adapter
	callback_url = 'http://127.0.0.1/github/callback/'
	client_class = CustomOAuth2Client
	

class GitHubLoginCallback(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        print("GitHub code received:", code)
        
        # Exchange the code for an access token
        if code is None:
            return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        token_url = urljoin('http://127.0.0.1:8000', reverse("github_login"))
        print("Token URL:", token_url)
        response = requests.post(
            url=token_url, 
            json={'code': code},  # Send JSON data instead of form data
            headers={'Content-Type': 'application/json'}
        )
        print("GitHub token response:", response.json())

        return Response(response.json(), status=response.status_code)
