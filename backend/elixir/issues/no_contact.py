from elixir.models import IssueType
from . import IssueBaseClass


class NoContactIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			NoContactIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='missing',
				attribute='contact'
			),
			_user=user
		)

	def detect(self, resource):
		output = []

		if not resource.contact:
			return [None]

		for el in resource.contact.all():
			if not el.url and not el.email:
				output.append('contact id: ' + str(el.id))
		
		return output
