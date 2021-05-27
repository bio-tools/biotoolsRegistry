from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers

# table to keep permissions for a specified resource
class EditPermission(models.Model):
	type = models.TextField(default="private")

	def __unicode__(self):
		return ''

class EditPermissionAuthor(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	editPermissions = models.ManyToManyField(EditPermission, related_name="authors")


class EditPermissionAuthorSerializer(serializers.ModelSerializer):
	user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
	editPermissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

	class Meta:
		model = EditPermissionAuthor
		fields = ('user', 'editPermissions',)

	def validate(self, attrs):
		self.validateUser(attrs['username'])
		return attrs

	def validateUser(self, username):
		if User.objects.filter(username = username).count() == 0:
			raise serializers.ValidationError("Specified user does not exist: " + username + ".")

	# need to add validation here since this method overrides all validation
	def to_internal_value(self, data):
		return {'username': data}

	def to_representation(self, obj):
		return obj.user.username

	def get_pk_field(self, model_field):
		return None

class EditPermissionSerializer(serializers.ModelSerializer):
	type = serializers.CharField(required=True)
	authors = EditPermissionAuthorSerializer(many=True, required=False)

	class Meta:
		model = EditPermission
		fields = ('type', 'authors',)

	def validate(self, attrs):
		self.validatePermissionType(attrs["type"])
		return attrs

	def validatePermissionType(self, type):
		permissionTypes = ["private", "public", "group"]
		if type not in permissionTypes:
			raise serializers.ValidationError("Invalid permission type. Allowed permission types are: " + ', '.join(str(x) for x in permissionTypes) +".")

	def get_pk_field(self, model_field):
		return None
