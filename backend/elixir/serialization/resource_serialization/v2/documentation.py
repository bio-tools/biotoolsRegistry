from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

# TODO: add this
# - "Governance" ("Information about the software governance model.")
# - "Contributions policy ("Information about policy for making contributions to the software project.)
# - "Installation instructions" ("Instructions how to install the software.")
# - "Tutorial" ("A tutorial about using the software.")

class LegacyDocumentationSerializer(serializers.ModelSerializer):
	url = serializers.CharField(allow_blank=False, validators=[IsURLFTPValidator], required=True)
	type = serializers.CharField(allow_blank=True, required=True)
	comment = serializers.CharField(allow_blank=True, min_length=10, max_length=1000, validators=[IsStringTypeValidator], required=False, source="note")

	class Meta:
		model = Documentation
		fields = ('url', 'type', 'comment')

	def validate_type(self, attrs):
		enum = ENUMValidator([u'API documentation', u'Citation instructions', u'General', u'Manual', u'Terms of use', u'Training material', u'Governance', u'Contributions policy', u'Installation instructions', u'Tutorial', u'Other'])
		attrs = enum(attrs)
		return attrs

	def get_pk_field(self, model_field):
		return None