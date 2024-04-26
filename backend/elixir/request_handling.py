from elixir.models import *

class ResourceRequestHandler:
	def proccessRequest(self, resourceRequest):
		if resourceRequest.type == 'editing':
			self.proccessEditingRightsRequest(resourceRequest)
		elif resourceRequest.type == 'ownership':
			self.proccessOwnershipRequest(resourceRequest)

	def proccessOwnershipRequest(self, resourceRequest):
		resourceRequest.resource.owner = resourceRequest.user 
		resourceRequest.resource.save()

	def proccessEditingRightsRequest(self, resourceRequest):
		user = resourceRequest.user
		authors = EditPermissionAuthor.objects.filter(user=user)
		author = None
		if authors.count() > 0:
			author = authors[0]
		else:
			author = EditPermissionAuthor.objects.create(user=user)
		author.save()
		author.editPermissions.add(resourceRequest.resource.editPermission)
		resourceRequest.resource.editPermission.type = 'group'
		resourceRequest.resource.editPermission.authors.add(author)
		resourceRequest.resource.save()
		resourceRequest.resource.editPermission.save()