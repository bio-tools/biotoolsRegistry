from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


class DocumentationSerializer(serializers.ModelSerializer):
	url = serializers.CharField(allow_blank=False, max_length=300, min_length=1, validators=[IsURLValidator], required=True)
	type = serializers.CharField(allow_blank=True, max_length=300, min_length=1, required=True)
	comment = serializers.CharField(allow_blank=True, max_length=1000, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Documentation
		fields = ('url','type', 'comment')

	def validate_type(self, attrs):
		enum = ENUMValidator([u'API documentation', u'Citation instructions', u'General', u'Manual', u'Terms of use', u'Training material', u'Other'])
		attrs = enum(attrs)
		return attrs

	def get_pk_field(self, model_field):
		return None