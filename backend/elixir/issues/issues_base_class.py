import datetime
from elixir.models import IssueType, IssueState, Issue, Resource


class IssueBaseClass(object):
	qset = None
	field_name = None
	issue_type = None
	fail_issue_state = None
	fixed_issue_state = None
	reopened_isseu_state = None
	term = None
	ov = None
	user = None

	def __init__(self, _qset, _type, _user='system'):
		if not _qset:
			_qset = Resource.objects.filter(visibility=1)
		self.qset = _qset
		self.issue_type = _type
		self.fail_issue_state = IssueState.objects.get(name='fail')
		self.fixed_issue_state = IssueState.objects.get(name='fixed')
		self.reopened_issue_state = IssueState.objects.get(name='reopened')
		self.user = _user

	# always perform PER TOOL and return True/false
	def detect(self, resource):
		raise Exception("Not implemented exception")

	# execute a check on the queryset and add issues to the DB
	def report(self):
		for tool in self.qset:
			# get the detected issues for the tool
			detected_issues = self.detect(tool)
			# get the existing issues of this type
			existing_issues = Issue.objects.filter(
				issue_type=self.issue_type,
				resource_biotoolsID=tool.biotoolsID,
				resource_versionId=tool.versionId
			)
			# now reopen the closed ones or close if there aren't any new ones
			#####
			# if we have something to report
			if not detected_issues:
				for issue in existing_issues:
					issue.issue_state = self.fixed_issue_state
					issue.resolution_date = datetime.datetime.now()
					issue.resolution_actor = self.user
					issue.save()
			else:
				for detected_issue in detected_issues:
					if existing_issues:
						for issue in existing_issues:
							if issue.issue_state == self.fixed_issue_state:
								issue.issue_state = self.reopened_issue_state
								issue.additionDate = datetime.datetime.now()
								issue.creation_actor = self.user
								issue.save()
					else:
						Issue(
							issue_type=self.issue_type,
							issue_state=self.fail_issue_state,
							field_value=detected_issue,
							resource_biotoolsID=tool.biotoolsID,
							resource_versionId=tool.versionId,
							creation_actor=self.user
						).save()
