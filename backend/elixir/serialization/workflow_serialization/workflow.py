from rest_framework import serializers
from elixir.models import *
from elixir.validators import *
from elixir.image_field import Base64ImageField

class WorkflowAnnotationSerializer(serializers.ModelSerializer):

	class Meta:
		model = WorkflowAnnotation
		fields = ('startX', 'startY', 'endX', 'endY', 'title', 'url', 'description', 'edam_term', 'edam_uri')


class WorkflowSerializer(serializers.ModelSerializer):
	id = serializers.CharField(source="biotoolsID")
	annotations = WorkflowAnnotationSerializer(many=True)
	width = serializers.FloatField(source="image_width")
	height = serializers.FloatField(source="image_height")
	image = Base64ImageField(
		max_length=None, use_url=True,
	)

	class Meta:
		model = Workflow
		fields = ('id', 'annotations', 'width', 'height', 'image', 'description', 'sourceURL')

	def create(self, validated_data):
		annotations_data = validated_data.pop('annotations')
		workflow = Workflow.objects.create(**validated_data)
		for annotation_data in annotations_data:
			WorkflowAnnotation.objects.create(workflow=workflow, **annotation_data)
		return workflow

	def validate_id(self, attrs):
		if Workflow.objects.filter(biotoolsID=attrs).count() != 0:
			raise serializers.ValidationError("Workflow with a given id already exists.")
		return attrs