from rest_framework import serializers
from dj_rest_auth.serializers import PasswordResetSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount

from elixir.models import *
from elixir.serialization.resource_serialization.resource import ResourceNameSerializer

import re

# custom serializer just for enabling HTML emails
class CustomPasswordResetSerializer(PasswordResetSerializer):
	def get_email_options(self):
		return {
			'html_email_template_name': 'registration/password_reset_key_message.html'
		}


# custom user validation
class UserRegisterSerializer(RegisterSerializer):
	def validate_username(self, attrs):
		# make sure the username matches the regular expression
		p = re.compile(r'^[A-Za-z0-9-_.]*$', re.IGNORECASE)
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain uppercase and lowercase letters, decimal digits, or these characters - _ .')
		# clean username using function built into allauth
		attrs = get_adapter().clean_username(attrs)
		return attrs
	
	def validate(self, attrs):
		# Ensure email is provided for regular registration
		if 'email' not in attrs or not attrs['email']:
			raise serializers.ValidationError({'email': 'Email is required for registration.'})
		return super().validate(attrs)


# username list
class UserNameSerializer(serializers.ModelSerializer):
	username = serializers.CharField()

	class Meta:
		model = User
		fields = ('username',)
	

# user details serializer
class CustomUserDetailsSerializer(serializers.ModelSerializer):
	resources = serializers.SerializerMethodField('get_resource')
	sharedResources = serializers.SerializerMethodField('get_shared_resource')
	# subdomains = serializers.SerializerMethodField()
	requests_count = serializers.SerializerMethodField('get_resource_request_count')
	socialAccounts = serializers.SerializerMethodField('get_social_accounts')
	email_verified = serializers.SerializerMethodField('get_email_verified')

	class Meta:
		model = User
		fields = ('username', 'email', 'resources', 'sharedResources', 'is_superuser', 'requests_count', 'socialAccounts', 'email_verified')

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

	def get_email_verified(self, user):
		"""
		Check if the user's primary email address is verified
		"""
		try:
			email_address = EmailAddress.objects.get(user=user, primary=True)
			return email_address.verified
		except EmailAddress.DoesNotExist:
			# If no EmailAddress exists, consider it unverified
			return False

	def update(self, instance, validated_data):
		"""
		Handle email address synchronization
		"""
		old_email = instance.email
		new_email = validated_data.get('email', old_email)

		if old_email == new_email:
			raise serializers.ValidationError({'email': 'Email address is the same as the current one.'})

		# Check for duplicates before any updates
		existing_email = EmailAddress.objects.filter(email=new_email).exclude(user=instance).first()
		if existing_email:
			raise serializers.ValidationError({'email': f"Email {new_email} is already in use"})
			

		instance = super().update(instance, validated_data)
		self._update_email_address(instance, old_email, new_email)
		
		return instance
	
	def _update_email_address(self, user, old_email, new_email):
		"""
		Update or create EmailAddress entries when user email changes
		"""
		try:
			# Try to find existing primary email address
			try:
				old_email_obj = EmailAddress.objects.get(user=user, primary=True)
				# Update existing primary email address
				old_email_obj.email = new_email
				old_email_obj.verified = False  # New email needs verification
				old_email_obj.save()
			except EmailAddress.DoesNotExist:
				# Create new primary email address if none exists
				EmailAddress.objects.create(
					user=user,
					email=new_email,
					primary=True,
					verified=False
				)
			
			# Remove any non-primary email addresses with the old email
			EmailAddress.objects.filter(user=user, email=old_email, primary=False).delete()
			
		except Exception as e:
			# re-raise to prevent user update if email sync fails
			raise
