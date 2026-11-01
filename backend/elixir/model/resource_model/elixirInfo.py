from django.db import models
from rest_framework import serializers

class ElixirInfo(models.Model):
	status = models.TextField(blank=True, null=True)
	node = models.TextField(blank=True, null=True)

	# metadata
	additionDate = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return ''


# class ElixirInfoSerializer(serializers.ModelSerializer):
# 	status = serializers.CharField(max_length=300, min_length=1, required=False)
# 	node = serializers.CharField(max_length=300, min_length=1, required=True)

# 	class Meta:
# 		model = ElixirInfo
# 		fields = ('status', 'node')

# 	def validate_status(self, attrs):
# 		enum = ENUMValidator([u'ELIXIR Core Service', u'ELIXIR Named Service'])
# 		attrs = enum(attrs)
# 		return attrs

# 	def validate_node(self, attrs):
# 		enum = ENUMValidator([u'UK', u'Switzerland', u'Sweden', u'Spain', u'Slovenia', u'Portugal', u'Norway', u'Netherlands', u'Italy', u'Israel', u'Greece', u'France', u'Finland', u'Estonia', u'EMBL-EBI', u'Denmark', u'Czech Republic', u'Belgium'])
# 		attrs = enum(attrs)
# 		return attrs

# 	def get_pk_field(self, model_field):
# 		return None