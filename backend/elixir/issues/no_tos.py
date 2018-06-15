from elixir.models import IssueType
from . import IssueBaseClass


class NoTOSIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			NoTOSIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='missing',
				attribute='documentation',
				field_name='type',
				field_value='terms_of_use'
			),
			_user=user
		)

	def detect(self, resource):
		output = []
	
		if not resource.documentation:
			return [None]

		missing = True

		for el in resource.documentation.all():
			if el.type:
				if el.type == 'Terms of use':
					missing = False
		if missing:
			output = [None]
		
		return output
