from elixir.models import IssueType
from . import IssueBaseClass


class NoLicenseIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			NoLicenseIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='missing',
				attribute='license'
			),
			_user=user
		)

	def detect(self, resource):
		output = []
	
		if not resource.license:
			output.append(None)
		
		return output
