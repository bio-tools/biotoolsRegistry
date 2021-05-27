from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class DownloadSerializer(serializers.ModelSerializer):
	url = serializers.CharField(allow_blank=False, validators=[IsURLFTPValidator], required=True)
	type = serializers.CharField(allow_blank=True, max_length=300, min_length=1, required=True)
	note = serializers.CharField(allow_blank=True, min_length=10, max_length=1000, validators=[IsStringTypeValidator], required=False)
	version = serializers.CharField(allow_blank=True, max_length=100, min_length=1, required=False)
	#cmd = serializers.CharField(max_length=100, min_length=1, validators=[IsStringTypeValidator], required=False)
	class Meta:
		model = Download
		fields = ('url', 'type', 'note', 'version')

	def validate_type(self, attrs):
		enum = ENUMValidator(['API specification', 'Biological data', 'Binaries', 'Command-line specification', 'Container file', 'Tool wrapper (CWL)', 'Icon', 'Screenshot', 'Software package', 'Source code', 'Test data', 'Test script', 'Tool wrapper (Galaxy)', 'Tool wrapper (Taverna)', 'Tool wrapper (Other)', 'VM image', 'Downloads page', 'Other'])
		attrs = enum(attrs)
		return attrs

	# TODO: add to interfaces
	# cmd == "A useful command pertinent to the download, e.g. for getting or installing a tool."
	# version == "Version information (typically a version number) of the software applicable to this download."
	def validate_version(self, attrs):
		# make sure the version matches the regular expression
		#p = re.compile('^[\p{Zs}A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)

		#this is ok, only allow spaces
		p = re.compile('^[ A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)

		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain letters, numbers, spaces or these characters: + . , - _ : ; ( )')
		return attrs

	def get_pk_field(self, model_field):
		return None