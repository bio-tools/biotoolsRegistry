from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


# TODO: add pattern validation [\p{Zs}A-Za-z0-9+\.,\-_:;()]*
class VersionSerializer(serializers.ModelSerializer):
	version = serializers.CharField(allow_blank=False, max_length=100, min_length=1, validators=[IsStringTypeValidator, IsVersionValidator], required=False)

	class Meta:
		model = Version
		fields = ('version',)

	def to_representation(self, obj):
		return obj.version

	# need to add validation here since this method overrides all validation
	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		IsVersionValidator(data)
		# check if length is not exceeded
		length = LengthValidator(100)
		length(data)
		return {'version': data}

	def get_pk_field(self, model_field):
		return None
