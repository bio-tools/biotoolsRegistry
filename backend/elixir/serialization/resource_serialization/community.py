from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class BioLibSerializer(serializers.ModelSerializer):
    app_name = serializers.CharField(allow_blank=False, required=True, max_length=40, min_length=1)
    author_name = serializers.CharField(allow_blank=False, required=True, max_length=40, min_length=1, validators=[IsStringTypeValidator])
    author_username = serializers.CharField(allow_blank=False, required=True, max_length=40, min_length=1)

    class Meta:
        model = BioLib
        fields = ('app_name', 'author_name', 'author_username',)
    
    def validate_app_name(self, attrs):
        p = re.compile('^[a-zA-Z0-9_-]+$', re.IGNORECASE | re.UNICODE)
        if not p.search(attrs):
            raise serializers.ValidationError('This field can only contain letters, numbers or - _')
        return attrs

    def validate_author_username(self, attrs):
        p = re.compile('^[a-zA-Z0-9_-]+$', re.IGNORECASE | re.UNICODE)
        if not p.search(attrs):
            raise serializers.ValidationError('This field can only contain letters, numbers or - _')
        return attrs


class CommunitySerializer(serializers.ModelSerializer):
    biolib = BioLibSerializer(many=False, required=True, allow_null=False)

    def validate_biolib(self, attrs):
        return attrs

    class Meta:
        model = Community
        fields = ('biolib',)