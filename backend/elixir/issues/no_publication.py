from elixir.models import IssueType
from . import IssueBaseClass


class NoPublicationIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			NoPublicationIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='missing',
				attribute='publication',
				field_name='id'
			),
			_user=user
		)

	def detect(self, resource):
		output = []
		
		if not resource.publication.all():
			output.append(None)
		for publication in resource.publication.all():
			if (
				publication.pmid is None and
				publication.pmcid is None and
				publication.doi is None
				):
				output.append(publication)
			empty_score = 0
			
			if publication.pmid:
				if len(publication.pmid) == 0:
					empty_score += 1
			if publication.pmcid:
				if len(publication.pmcid) == 0:
					empty_score += 1
			if publication.doi:
				if len(publication.doi) == 0:
					empty_score += 1

			if empty_score == 3:
				output.append(publication)
		
		return output
