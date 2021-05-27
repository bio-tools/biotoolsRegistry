from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

# TODO: make link and download and documentation respect this:
# "link": [
# 	{
# 		"isAvailable": false,
# 		"type": "Scientific benchmark"
# 	},
# 	{
# 	  	"url": "https://example.com",
# 	 	"type": "Helpdesk"
# 	}
# ]

class LinkTypeSerializer(serializers.ModelSerializer):
	type = serializers.CharField(allow_blank=False, required=True)

	class Meta:
		model = LinkType
		fields = ('type',)

	def get_pk_field(self, model_field):
		return None

	def to_representation(self, obj):
		return obj.type

	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# checking if within enum
		enum = ENUMValidator(['Helpdesk', 'Issue tracker', 'Mailing list', 'Mirror', 'Repository', 'Social media', 'Service', 'Software catalogue', 'Technical monitoring', 'Galaxy service', 'Discussion forum', 'Other'])
		data = enum(data)
		return {'type': data}

class LinkSerializer(serializers.ModelSerializer):
	url = serializers.CharField(allow_blank=False, validators=[IsURLFTPValidator], required=True)
	type = LinkTypeSerializer(many=True, required=True, allow_empty=False)
	note = serializers.CharField(allow_blank=True, min_length=10, max_length=1000, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Link
		fields = ('url', 'type', 'note')

	# def validate_type(self, attrs):
	# 	enum = ENUMValidator([u'Helpdesk', u'Issue tracker', u'Mailing list', u'Mirror', u'Registry', u'Repository', u'Social media', u'Service', u'Software catalogue', u'Technical monitoring', u'Galaxy service', u'Discussion forum', u'Other'])
	# 	attrs = enum(attrs)
	# 	return attrs

	def get_pk_field(self, model_field):
		return None

