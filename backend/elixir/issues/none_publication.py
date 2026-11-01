from elixir.models import IssueType
from . import IssueBaseClass


class NonePublicationIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			NonePublicationIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='none',
				attribute='publication',
				field_name='id'
			),
			_user=user
		)

	def detect(self, resource):
		output = []

		for publication in resource.publication.all():
			if (
				publication.pmid == 'None' or
				publication.pmcid == 'None' or
				publication.doi == 'None'
				):
				output.append(publication)
		
		return output
