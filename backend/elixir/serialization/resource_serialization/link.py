from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class LinkSerializer(serializers.ModelSerializer):
	url = serializers.CharField(allow_blank=False, max_length=300, min_length=1, validators=[IsURLFTPValidator], required=True)
	type = serializers.CharField(allow_blank=True, max_length=300, min_length=1, required=True)
	comment = serializers.CharField(allow_blank=True, max_length=1000, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Link
		fields = ('url','type', 'comment')

	def validate_type(self, attrs):
		enum = ENUMValidator([u'Browser', u'Helpdesk', u'Issue tracker', u'Mailing list', u'Mirror', u'Registry', u'Repository', u'Social media'])
		attrs = enum(attrs)
		return attrs

	def get_pk_field(self, model_field):
		return None