import requests
from elixir.models import IssueType
from . import IssueBaseClass


class URLContactIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			URLContactIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='invalid_url',
				attribute='contact',
				field_name='url'
			),
			_user=user
		)

	def detect(self, resource):
		output = []

		for el in resource.contact.all():
			if el.url:
				request = requests.get(el.url)
				if request.status_code != 200:
					output.append(el.url)

		return output
