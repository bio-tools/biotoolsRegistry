from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


class TopicSerialiser(serializers.ModelSerializer):
	uri = serializers.CharField(allow_blank=False, validators=[IsURLValidator], required=False)

	class Meta:
		model = Topic
		fields = ('uri', 'term')

	def validate(self, attrs):
		ontology = OntologyValidator('EDAM_topic')
		ontology(attrs.get('uri', None), attrs.get('term', None))
		attrs['uri'] = ontology.get_URI()
		attrs['term'] = ontology.get_term()
		return attrs


class DataSerializer(serializers.ModelSerializer):
	uri = serializers.CharField(allow_blank=False, validators=[IsURLValidator], required=False)

	class Meta:
		model = Data
		fields = ('uri', 'term')

	def validate(self, attrs):
		ontology = OntologyValidator('EDAM_data')
		ontology(attrs.get('uri', None), attrs.get('term', None))
		attrs['uri'] = ontology.get_URI()
		attrs['term'] = ontology.get_term()
		return attrs


class FormatSerializer(serializers.ModelSerializer):
	uri = serializers.CharField(allow_blank=False, validators=[IsURLValidator], required=False)

	class Meta:
		model = Format
		fields = ('uri', 'term')

	def validate(self, attrs):
		ontology = OntologyValidator('EDAM_format')
		ontology(attrs.get('uri', None), attrs.get('term', None))
		attrs['uri'] = ontology.get_URI()
		attrs['term'] = ontology.get_term()
		return attrs

class InputSerializer(serializers.ModelSerializer):

	# nested attributes
	data = DataSerializer(many=False, required=True)
	format = FormatSerializer(many=True, required=False, allow_empty=False)

	class Meta:
		model = Input
		fields = ('data', 'format')


class OutputSerializer(serializers.ModelSerializer):

	# nested attributes
	data = DataSerializer(many=False, required=True)
	format = FormatSerializer(many=True, required=False, allow_empty=False)

	class Meta:
		model = Output
		fields = ('data', 'format')


class OperationSerializer(serializers.ModelSerializer):
	uri = serializers.CharField(allow_blank=False, validators=[IsURLValidator], required=False)

	class Meta:
		model = Operation
		fields = ('uri', 'term')

	def validate(self, attrs):
		ontology = OntologyValidator('EDAM_operation')
		ontology(attrs.get('uri', None), attrs.get('term', None))
		attrs['uri'] = ontology.get_URI()
		attrs['term'] = ontology.get_term()
		return attrs


class FunctionSerializer(serializers.ModelSerializer):
	note = serializers.CharField(max_length=1000, min_length=10, validators=[IsStringTypeValidator], required=False)
	# check for length restrictions
	cmd = serializers.CharField(max_length=1000, min_length=1, validators=[IsStringTypeValidator], required=False)

	# nested attributes
	operation = OperationSerializer(many=True, required=True, allow_empty=False)
	input = InputSerializer(many=True, required=False, allow_empty=False)
	output = OutputSerializer(many=True, required=False, allow_empty=False)

	class Meta:
		model = Function
		fields = ('operation', 'input', 'output', 'note', 'cmd')
		
class OntologySerializer(serializers.ModelSerializer):

	class Meta:
		model = Ontology
		fields = ('data',)

	def get_pk_field(self, model_field):
		return None

		