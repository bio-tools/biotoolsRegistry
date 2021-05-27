from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


class IssueTypeSerializer(serializers.ModelSerializer):

	class Meta:
		model = IssueType
		fields = ('type', 'attribute', 'field_name', 'field_value')

	def get_pk_field(self, model_field):
		return None


class IssueStateSerializer(serializers.ModelSerializer):

	class Meta:
		model = IssueState
		fields = ('name',)

	def to_representation(self, obj):
		return obj.name

	def get_pk_field(self, model_field):
		return None


class IssueSerializer(serializers.ModelSerializer):
	issue_type = IssueTypeSerializer(many=False)
	issue_state = IssueStateSerializer(many=False)

	class Meta:
		model = Issue
		fields = (
			'id',
			'issue_type',
			'issue_state',
			'field_name',
			'field_value',
			'resource_biotoolsID',
			'resolution_date',
			'resolution_actor',
			'additionDate',
			'comment',
			'creation_actor'
			)