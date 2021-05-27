from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


class DocumentationTypeSerializer(serializers.ModelSerializer):
	type = serializers.CharField(allow_blank=False, required=True)

	class Meta:
		model = DocumentationType
		fields = ('type',)

	def get_pk_field(self, model_field):
		return None

	def to_representation(self, obj):
		return obj.type

	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# checking if within enum
		enum = ENUMValidator(['API documentation', 'Citation instructions', 'Code of conduct', 'Command-line options', 'General', 'User manual', 'Terms of use', 'Training material', 'Governance', 'Contributions policy', 'Installation instructions', 'FAQ', 'Release notes', 'Other', 'Quick start guide'])
		data = enum(data)
		return {'type': data}

class DocumentationSerializer(serializers.ModelSerializer):
	url = serializers.CharField(allow_blank=False, validators=[IsURLFTPValidator], required=True)
	type = DocumentationTypeSerializer(many=True, required=True, allow_empty=False)
	note = serializers.CharField(allow_blank=True, min_length=10, max_length=1000, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Documentation
		fields = ('url', 'type', 'note')

	# def validate_type(self, attrs):
	# 	enum = ENUMValidator([u'API documentation', u'Citation instructions', u'Code of conduct', u'Command-line options', u'General', u'User manual', u'Terms of use', u'Training material', u'Governance', u'Contributions policy', u'Installation instructions', u'FAQ', u'Release notes', u'Other'])
	# 	attrs = enum(attrs)
	# 	return attrs

	def get_pk_field(self, model_field):
		return None