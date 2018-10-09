from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


class CollectionIDSerializer(serializers.ModelSerializer):
	name = serializers.CharField(allow_blank=False, max_length=50, min_length=1, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = CollectionID
		fields = ('name',)

	def to_representation(self, obj):
		return obj.name

	# need to add validation here since this method overrides all validation
	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# check if length is not exceeded
		length = LengthValidator(50)
		length(data)
		IsCollectionIDValidator(data)
		return {'name': data}

	def get_pk_field(self, model_field):
		return None
