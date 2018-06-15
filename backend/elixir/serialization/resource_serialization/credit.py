from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class CreditSerializer(serializers.ModelSerializer):
	name = serializers.CharField(allow_blank=False, max_length=100, min_length=1, validators=[IsStringTypeValidator], required=True)
	url = serializers.CharField(allow_blank=False, max_length=300, min_length=1, validators=[IsURLValidator], required=False)
	email = serializers.CharField(allow_blank=False, max_length=300, validators=[IsStringTypeValidator, IsEmailValidator], required=False)
	orcidId = serializers.CharField(allow_blank=False, max_length=100, validators=[IsStringTypeValidator], required=False)
	gridId = serializers.CharField(allow_blank=False, max_length=100, validators=[IsStringTypeValidator], required=False)
	typeEntity = serializers.CharField(allow_blank=False, max_length=30, required=False)
	typeRole = serializers.CharField(allow_blank=False, max_length=30, required=False)
	comment = serializers.CharField(allow_blank=False, max_length=1000, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Credit
		fields = ('name', 'url', 'email', 'orcidId', 'gridId', 'typeEntity', 'typeRole', 'comment')

	def validate_typeEntity(self, attrs):
		enum = ENUMValidator([u'Person', u'Project', u'Division', u'Institute', u'Consortium', u'Funding agency'])
		attrs = enum(attrs)
		return attrs

	def validate_typeRole(self, attrs):
		enum = ENUMValidator([u'Developer', u'Maintainer', u'Provider', u'Documentor', u'Contributor', u'Support'])
		attrs = enum(attrs)
		return attrs

	def get_pk_field(self, model_field):
		return None