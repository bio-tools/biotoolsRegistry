import requests
from elixir.models import IssueType
from . import IssueBaseClass


class URLDocumentationIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			URLDocumentationIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='invalid_url',
				attribute='documentation',
				field_name='url'
			),
			_user=user
		)

	def detect(self, resource):
		output = []

		for el in resource.credit.all():
			if el.url:
				request = requests.get(el.url)
				if request.status_code != 200:
					output.append(el.url)

		return output
