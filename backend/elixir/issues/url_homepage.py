import requests
from elixir.models import IssueType
from . import IssueBaseClass


class URLHomepageIssue(IssueBaseClass):

	def __init__(self, qset, user):
		super(
			URLHomepageIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='invalid_url',
				attribute='homepage'
			),
			_user=user
		)

	def detect(self, resource):
		output = []

		request = requests.get(resource.homepage)
		if request.status_code == 200:
			output.append(resource.homepage)
		
		return output
