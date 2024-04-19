from rest_framework import serializers
from elixir.models import *
from rest_auth.serializers import PasswordResetSerializer#, UserDetailsSerializer
from rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
import re

# custom serializer just for enabling HTML emails
class CustomPasswordResetSerializer(PasswordResetSerializer):
	def get_email_options(self):
		return {
			'html_email_template_name': 'registration/password_reset_email.html'
		}


# custom user validation
class UserRegisterSerializer(RegisterSerializer):
	def validate_username(self, attrs):
		# make sure the username matches the regular expression
		p = re.compile('^[A-Za-z0-9-_.]*$', re.IGNORECASE)
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain uppercase and lowercase letters, decimal digits, or these characters - _ .')
		# clean username using function built into allauth
		attrs = get_adapter().clean_username(attrs)
		return attrs


# username list
class UserNameSerializer(serializers.ModelSerializer):
	username = serializers.CharField()

	class Meta:
		model = User
		fields = ('username',)