from rest_framework import serializers
from elixir.models import *
from elixir.validators import *
from elixir.resource_options import METADATA_CHOICES

class ToolTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        allow_blank=False, validators=[IsStringTypeValidator], required=False
    )

    class Meta:
        model = ToolType
        fields = ("name",)

    def get_pk_field(self, model_field):
        return None

    def to_representation(self, obj):
        return obj.name

    # need to add validation here since this method overrides all validation
    def to_internal_value(self, data):
        # checking if blank
        IsNotBlankValidator(data)
        # checking if within enum
        enum = ENUMValidator(METADATA_CHOICES['toolType'])
        data = enum(data)
        return {"name": data}
