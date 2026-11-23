from rest_framework import serializers
from allauth.socialaccount.models import SocialAccount
from django.core.validators import URLValidator
from elixir.models import *
from elixir.validators import *
from elixir.request_handling import ResourceRequestHandler


class ResourceRequestSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=2000)
    supporting_url = serializers.URLField(required=False, allow_blank=True, max_length=500,
                                          validators=[URLValidator(schemes=['http', 'https'])])
    username = serializers.CharField(
        allow_blank=False, max_length=25, min_length=1, source="user.username"
    )
    email = serializers.EmailField(source="user.email")
    orcid = serializers.SerializerMethodField()
    resourceId = serializers.CharField(
        allow_blank=False, min_length=1, source="resource.biotoolsID"
    )
    resourceName = serializers.CharField(source='resource.name', read_only=True)

    class Meta:
        model = ResourceRequest
        fields = (
            "type",
            "completed",
            "accepted",
            "username",
            "email",
            "orcid",
            "requestId",
            "resourceId",
            "resourceName",
            "relationship",
            "reason",
            "supporting_url",
            "created_at",
            "withdrawn",
        )
        read_only_fields = ('created_at', 'withdrawn')

    def get_orcid(self, obj):
        """Get ORCID from the user's social accounts"""
        try:
            orcid_account = SocialAccount.objects.get(user=obj.user, provider='orcid')
            return orcid_account.uid
        except SocialAccount.DoesNotExist:
            return ''

    def create(self, validated_data):
        return ResourceRequest.objects.create(
            user=User.objects.get(username=validated_data['user']['username']),
            resource=Resource.objects.get(visibility=1, biotoolsID__iexact=validated_data['resource']['biotoolsID']),
            type=validated_data['type'], requestId=validated_data['requestId'],
            relationship=validated_data.get('relationship', ''), reason=validated_data.get('reason', ''),
            supporting_url=validated_data.get('supporting_url', ''))

    def validate_type(self, attrs):
        enum = ENUMValidator(["editing", "ownership"])
        attrs = enum(attrs)
        return attrs

    def validate(self, attrs):
        if (
            Resource.objects.filter(visibility=1)
            .filter(biotoolsID__iexact=attrs["resource"]["biotoolsID"])
            .count()
            == 0
        ):
            raise serializers.ValidationError(
                "Requested resource does not exist for specified 'resourceId'"
            )
        return attrs


class ResourceRequestConcludeSerializer(serializers.ModelSerializer):
    accept = serializers.BooleanField(source="accepted")

    class Meta:
        model = ResourceRequest
        fields = (
            "accept",
            "requestId",
        )

    def update(self, instance, validated_data):
        instance.completed = True
        instance.accepted = validated_data.get("accepted", instance.accepted)
        instance.completedBy = self.context["user"]
        if instance.accepted is True:
            request_handler = ResourceRequestHandler()
            request_handler.proccessRequest(instance)
        instance.save()
        return instance
