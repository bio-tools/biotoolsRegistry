import requests
from elixir.models import IssueType
from . import IssueBaseClass


class URLLinkIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			URLLinkIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='invalid_url',
				attribute='link',
				field_name='url'
			),
			_user=user
		)

	def detect(self, resource):
		output = []

		for el in resource.link.all():
			if el.url:
				request = requests.get(el.url)
				if request.status_code != 200:
					output.append(el.url)

		return output
