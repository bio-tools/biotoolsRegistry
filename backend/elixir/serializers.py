from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from elixir.models import *
from elixir.validators import *
from elixir.exceptions import *
import re, json
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
from allauth.account.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from elixir.request_handling import ResourceRequestHandler
from random import randint

from elixir.serialization.resource_serialization.domain import *
from elixir.serialization.resource_serialization.edam import *
from elixir.serialization.resource_serialization.operatingSystem import *
from elixir.serialization.resource_serialization.toolType import *
from elixir.serialization.resource_serialization.language import *
from elixir.serialization.resource_serialization.accessibility import *
from elixir.serialization.resource_serialization.publication import *
from elixir.serialization.resource_serialization.credit import *
from elixir.serialization.resource_serialization.link import *
from elixir.serialization.resource_serialization.download import *
from elixir.serialization.resource_serialization.documentation import *
from elixir.serialization.resource_serialization.collection import *
from elixir.serialization.resource_serialization.contact import *
from elixir.serialization.resource_serialization.resource import *
from elixir.serialization.resource_serialization.user import *
from elixir.serialization.resource_serialization.resourceRequest import *
from elixir.serialization.resource_serialization.version import *
from elixir.serialization.workflow_serialization.workflow import *
from elixir.serialization.user_serialization.user import *
from elixir.serialization.issues_serialization.issues import *


# # just get the versions and latest
# class VersionLatestSerializer(ResourceSerializer):

# 	class Meta:
# 		model = Resource
# 		fields = ('versionId','version','latest',)


class UserSerializer(serializers.ModelSerializer):
	resources = serializers.SerializerMethodField('get_resource')
	sharedResources = serializers.SerializerMethodField('get_shared_resource')
	# subdomains = serializers.SerializerMethodField()
	requests_count = serializers.SerializerMethodField('get_resource_request_count')
	socialAccounts = serializers.SerializerMethodField('get_social_accounts')

	class Meta:
		model = User
		fields = ('username', 'email', 'resources', 'sharedResources', 'is_superuser', 'requests_count', 'socialAccounts')

	def get_resource(self, user):
		resources = Resource.objects.filter(visibility=1, owner=user)
		serializer = ResourceNameSerializer(instance=resources, many=True)
		return serializer.data

	def get_shared_resource(self, user):
		resources = Resource.objects.filter(visibility=1, editPermission__authors__user=user)
		serializer = ResourceNameSerializer(instance=resources, many=True)
		return serializer.data

	def get_resource_request_count(self, user):
		if user.is_superuser:
			return ResourceRequest.objects.filter(completed=False).count()
		return ResourceRequest.objects.filter(resource__owner=user, completed=False).count()

	def get_social_accounts(self, user):
		social_accounts = SocialAccount.objects.filter(user=user)
		return [
			{
				'id': account.id,
				'provider': account.provider,
				'uid': account.uid,
				'extra_data': {
					'login': account.extra_data.get('login', ''),
					'name': account.extra_data.get('name', ''),
					'email': account.extra_data.get('email', ''),
					'orcid': account.extra_data.get('orcid', ''),
					'given_names': account.extra_data.get('given-names', ''),
					'family_name': account.extra_data.get('family-name', ''),
				}
			}
			for account in social_accounts
		]

	# def get_subdomains(self, user):
	# 	subdomains = Domain.objects.filter(owner=user)
	# 	serializer = SubdomainNameSerializer(instance=subdomains, many=True)
	# 	return serializer.data
		


