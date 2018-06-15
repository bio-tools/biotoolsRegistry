from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class ToolTypeSerializer(serializers.ModelSerializer):
	name = serializers.CharField(allow_blank=False, max_length=300, min_length=1, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = ToolType
		fields = ('name',)

	def get_pk_field(self, model_field):
		return None

	def to_representation(self, obj):
		return obj.name

	# need to add validation here since this method overrides all validation
	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# checking if within enum
		enum = ENUMValidator([u'Command-line tool', u'Web application', u'Desktop application', u'Script', u'Suite', u'Workbench', u'Database portal', u'Ontology', u'Workflow', u'Plug-in', u'Library', u'Web API', u'Web service', u'SPARQL endpoint'])
		data = enum(data)
		return {'name':data}