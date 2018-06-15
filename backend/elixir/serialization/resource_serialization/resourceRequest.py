from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class ResourceRequestSerializer(serializers.ModelSerializer):
	username = serializers.CharField(allow_blank=False, max_length=25, min_length=1, source="user.username")
	resourceId = serializers.CharField(allow_blank=False, min_length=1, source="resource.textId")

	class Meta:
		model = ResourceRequest
		fields = ('type', 'completed', 'accepted', 'username', 'requestId', 'resourceId',)

	def create(self, validated_data):
		request = ResourceRequest.objects.create()
		request.user = User.objects.get(username = validated_data.get('user')['username'])
		request.resource = Resource.objects.filter(visibility=1).get(textId__iexact=validated_data.get('resource')['textId'])
		request.type = validated_data.get('type')
		request.requestId = validated_data.get('requestId')
		request.save()
		return request

	def validate_type(self, attrs):
		enum = ENUMValidator([u'editing', u'ownership'])
		attrs = enum(attrs)
		return attrs

	def validate(self, attrs):
		if Resource.objects.filter(visibility=1).filter(textId__iexact=attrs['resource']['textId']).count() == 0:
			raise serializers.ValidationError("Requested resource does not exist for specified 'resourceId'")
		return attrs


class ResourceRequestConcludeSerializer(serializers.ModelSerializer):
	accept = serializers.BooleanField(source="accepted")

	class Meta:
		model = ResourceRequest
		fields = ('accept', 'requestId',)

	def update(self, instance, validated_data):
		instance.completed = True
		instance.accepted = validated_data.get('accepted', instance.accepted)
		instance.completedBy = self.context['user']
		if instance.accepted == True:
			request_handler = ResourceRequestHandler()
			request_handler.proccessRequest(instance)
		instance.save()
		return instance