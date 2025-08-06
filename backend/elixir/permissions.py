from rest_framework import permissions
from django.http import Http404

class IsDomainOwnerOrReadOnly(permissions.BasePermission):
	"""
	Custom permission to only allow owners of a domain to edit it.
	"""
	def has_permission(self, request, view, obj=None):
		# Write permissions are only allowed to the owner of the domain
		return obj is None or obj.from_user == request.user

	def has_object_permission(self, request, view, obj):
		# Read permissions are allowed to any requests,
		# so we'll always allow GET, HEAD or OPTIONS requests.
		if request.method in permissions.SAFE_METHODS:
			return True

		if request.user.is_superuser:
			return True
		
		# Write permissions are only allowed to the owner of the domain.
		return obj.owner == request.user



class IsDomainOwnerOrEditorOrReadOnly(permissions.BasePermission):
	"""
    Custom permission to only allow owners, editors, or superusers to edit an object.
    Read-only access is allowed to all authenticated users.
    """
	def has_object_permission(self, request, view, obj):
		# Read permissions are allowed to any requests,
		# so we'll always allow GET, HEAD or OPTIONS requests.
		if request.method in permissions.SAFE_METHODS:
			return True

		# Write permissions for superuser, owner, or editor
		return (
			request.user.is_superuser or
			obj.owner == request.user or
			request.user in obj.editors.all()
		)

class IsOwnerOrReadOnly(permissions.BasePermission):
	"""
	Custom permission to only allow owners of an object to edit it.
	"""

	def has_permission(self, request, view, obj=None):
		# Write permissions are only allowed to the owner of the tool
		return obj is None or obj.from_user == request.user

	def has_object_permission(self, request, view, obj):
		# Read permissions are allowed to any request,
		# so we'll always allow GET, HEAD or OPTIONS requests.
		if request.method in permissions.SAFE_METHODS:
			return True

		if request.user.is_superuser:
			return True

		# check if resource is public
		if obj.editPermission.type == 'public':
			return True

		# Write permissions are only allowed to the owner of the tool.
		return obj.owner == request.user


class HasEditPermissionToEditResourceOrReadOnly(permissions.BasePermission):
	"""
	Custom permission to only allow owners or people with edit permissions of an object to edit it.
	"""

	def has_permission(self, request, view, obj=None):
		# Write permissions are only allowed to the owner of the tool
		return obj is None or obj.from_user == request.user

	def has_object_permission(self, request, view, obj):
		# Read permissions are allowed to any request,
		# so we'll always allow GET, HEAD or OPTIONS requests.
		if request.method in permissions.SAFE_METHODS:
			return True

		if request.user.is_superuser:
			return True

		permissionType = obj.editPermission.type
		authors = obj.editPermission.authors
		if permissionType is not None:
			if permissionType == "public":
				return True
			if permissionType == "group" and authors is not None:
				for author in authors.all():
					if author.user == request.user:
						return True

		# Write permissions are only allowed to the owner of the tool.
		return obj.owner == request.user


class IsStaffOrReadOnly(permissions.BasePermission):

	def has_permission(self, request, view, obj=None):
		if request.method in permissions.SAFE_METHODS:
			return True

		if request.user.is_superuser:
			return True
		
		return request.user.is_staff

	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True
		if request.user.is_superuser:
			return True
		
		return request.user.is_staff


class CanConcludeResourceRequest:

	def has_permission(self, request, view, obj=None):
		# Write permissions are only allowed to the owner of the tool
		return obj is None or obj.from_user == request.user

	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser:
			return True
		return obj.resource.owner == request.user

