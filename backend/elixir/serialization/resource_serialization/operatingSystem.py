from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class OperatingSystemSerializer(serializers.ModelSerializer):
	name = serializers.CharField(allow_blank=False, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = OperatingSystem
		fields = ('name',)

	def get_pk_field(self, model_field):
		return None

	def to_representation(self, obj):
		return obj.name

	# need to add validation here since this method overrides all validation
	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# check if length is not exceeded
		enum = ENUMValidator(['Mac', 'Linux', 'Windows'])
		data = enum(data)
		return {'name': data}