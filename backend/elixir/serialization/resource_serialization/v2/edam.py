from rest_framework import serializers
from elixir.models import *
from elixir.validators import *
from elixir.serializers import *

class LegacyFunctionSerializer(serializers.ModelSerializer):
	comment = serializers.CharField(max_length=1000, min_length=10, validators=[IsStringTypeValidator], required=False, source='note')

	# nested attributes
	operation = OperationSerializer(many=True, required=True, allow_empty=False)
	input = InputSerializer(many=True, required=False, allow_empty=False)
	output = OutputSerializer(many=True, required=False, allow_empty=False)

	class Meta:
		model = Function
		fields = ('comment', 'operation', 'input', 'output')
