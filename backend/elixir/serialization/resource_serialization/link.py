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
class LinkSerializer(serializers.ModelSerializer):
	url = serializers.CharField(allow_blank=False, validators=[IsURLFTPValidator], required=True)
	type = serializers.CharField(allow_blank=True, required=True)
	note = serializers.CharField(allow_blank=True, min_length=10, max_length=1000, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Link
		fields = ('url', 'type', 'note')

	def validate_type(self, attrs):
		enum = ENUMValidator([u'Helpdesk', u'Issue tracker', u'Mailing list', u'Mirror', u'Registry', u'Repository', u'Social media', u'Scientific benchmark', u'Service', u'Technical monitoring', u'Galaxy service', u'Discussion forum', u'Other'])
		attrs = enum(attrs)
		return attrs

	def get_pk_field(self, model_field):
		return None