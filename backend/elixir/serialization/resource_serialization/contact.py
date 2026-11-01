from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

# TODO: this needs migrating to credits
# class ContactSerializer(serializers.ModelSerializer):
# 	name = serializers.CharField(allow_blank=False, max_length=300, min_length=1, validators=[IsStringTypeValidator], required=False)
# 	url = serializers.CharField(allow_blank=False, validators=[IsURLValidator], required=False)
# 	email = serializers.CharField(allow_blank=False, max_length=300, validators=[IsStringTypeValidator, IsEmailValidator], required=False)
# 	tel = serializers.CharField(allow_blank=False, max_length=30, validators=[IsStringTypeValidator], required=False)
# 	# contactRole = ContactRoleSerializer(many=True, required=False)

# 	class Meta:
# 		model = Contact
# 		fields = ('name', 'url', 'email', 'tel')

# 	def validate_url(self, attrs):
# 		attrs = IsURLValidator(attrs)
# 		return attrs

# 	def validate(self, attrs):
# 		# make sure that either the email or URL is included
# 		if not ( ('email' in attrs and len(attrs['email'])) or ('url' in attrs and len(attrs['url'])) ):
# 			raise serializers.ValidationError('Either the URL or email is required.')
# 		# case insensitive overwrite
# 		return attrs

# 	def get_pk_field(self, model_field):
# 		return None
