from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class PublicationAuthorSerializer(serializers.ModelSerializer):
	class Meta:
		model = PublicationAuthor
		fields = ('name',)

class PublicationMetadataSerializer(serializers.ModelSerializer):
	authors = PublicationAuthorSerializer(many=True)

	class Meta:
		model = PublicationMetadata
		fields = ('title', 'abstract', 'date', 'citationCount', 'authors', 'journal')

class PublicationSerializer(serializers.ModelSerializer):
	pmcid = serializers.CharField(allow_blank=False, validators=[IsPMCIDValidator], required=False)
	pmid = serializers.CharField(allow_blank=False, validators=[IsPMIDValidator], required=False)
	doi = serializers.CharField(allow_blank=False, validators=[IsDOIValidator], required=False)
	type = serializers.CharField(allow_blank=True, max_length=300, min_length=1, required=False)
	version = serializers.CharField(allow_blank=True, max_length=300, min_length=1, required=False)
	metadata = PublicationMetadataSerializer(read_only=True, required=False, many=False)

	class Meta:
		model = Publication
		fields = ('pmcid', 'pmid', 'doi', 'type', 'version', 'metadata')

	def validate_type(self, attrs):
		enum = ENUMValidator([u'Primary', u'Benchmark', u'Review', u'Other'])
		attrs = enum(attrs)
		return attrs

	def get_pk_field(self, model_field):
		return None