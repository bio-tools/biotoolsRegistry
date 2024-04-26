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

class PublicationTypeSerializer(serializers.ModelSerializer):
	type = serializers.CharField(allow_blank=False, required=True)

	class Meta:
		model = PublicationType
		fields = ('type',)

	def get_pk_field(self, model_field):
		return None

	def to_representation(self, obj):
		return obj.type

	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# checking if within enum
		enum = enum = ENUMValidator(['Primary', 'Method', 'Usage', 'Benchmarking study', 'Review', 'Other'])
		data = enum(data)
		return {'type': data}

class PublicationSerializer(serializers.ModelSerializer):
	pmcid = serializers.CharField(allow_blank=False, validators=[IsPMCIDValidator], required=False)
	pmid = serializers.CharField(allow_blank=False, validators=[IsPMIDValidator], required=False)
	doi = serializers.CharField(allow_blank=False, validators=[IsDOIValidator], required=False)
	# type = serializers.CharField(allow_blank=True, max_length=300, min_length=1, required=False)
	type = PublicationTypeSerializer(many=True, required=False, allow_empty=False)
	version = serializers.CharField(allow_blank=False, max_length=100, min_length=1, required=False)
	note = serializers.CharField(allow_blank=True, min_length=10, max_length=1000, validators=[IsStringTypeValidator], required=False)
	metadata = PublicationMetadataSerializer(read_only=True, required=False, many=False)

# TODO: add these to interfaces
# summary->version == "Version information (typically a version number) of the software applicable to this bio.tools entry."
# summary->otherID->version == "Version information (typically a version number) of the software applicable to this identifier."
# download->version == "Version information (typically a version number) of the software applicable to this download."
# publication->version == "Version information (typically a version number) of the software applicable to this publication."

	class Meta:
		model = Publication
		fields = ('doi', 'pmid', 'pmcid',  'type', 'version', 'note', 'metadata')

	# def validate_type(self, attrs):
	# 	enum = ENUMValidator([u'Primary', u'Method', u'Usage', u'Benchmarking study', u'Review', u'Other'])
	# 	attrs = enum(attrs)
	# 	return attrs

	def validate_version(self, attrs):
		# make sure the version matches the regular expression
		# this is wrong in python, it doesn't work for spaces, 
		#we shouldn't use other whitespace than spaces anway
		#p = re.compile('^[\p{Zs}A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)

		#this is ok, only allow spaces
		p = re.compile('^[ A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)
		
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain letters, numbers, spaces or these characters: + . , - _ : ; ( )')
		return attrs
	
	def validate(self, data):
		if not data.get("doi") and not data.get("pmid") and not data.get("pmcid"):
			raise serializers.ValidationError('Publication requires at least one of DOI, PMID, PMCID')

		return data

	def get_pk_field(self, model_field):
		return None