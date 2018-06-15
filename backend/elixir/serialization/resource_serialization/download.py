from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class DownloadSerializer(serializers.ModelSerializer):
	url = serializers.CharField(allow_blank=False, max_length=300, min_length=1, validators=[IsURLFTPValidator], required=True)
	type = serializers.CharField(allow_blank=True, max_length=300, min_length=1, required=True)
	comment = serializers.CharField(allow_blank=True, max_length=1000, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Download
		fields = ('url','type', 'comment')

	def validate_type(self, attrs):
		enum = ENUMValidator([u'API specification', u'Biological data', u'Binaries', u'Binary package', u'Command-line specification', u'Container file', u'CWL file', u'Icon', u'Ontology', u'Screenshot', u'Source code', u'Source package', u'Test data', u'Test script', u'Tool wrapper (galaxy)', u'Tool wrapper (taverna)', u'Tool wrapper (other)', u'VM image'])
		attrs = enum(attrs)
		return attrs

	def get_pk_field(self, model_field):
		return None