from elixir.models import IssueType
from . import IssueBaseClass
from .ontology_validator import IssueOntologyValidator

class EDAMTopicIssue(IssueBaseClass):

	def __init__(self, qset, user, term='Topic'):
		self.term = term
		self.ov = IssueOntologyValidator('EDAM_topic')
		super(
			EDAMTopicIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='ontology',
				attribute='topic',
				field_value=None
			),
			_user=user
		)

	def detect(self, resource):
		output = []
		
		obj = self.ov.check_if_term_or_uri_in_ontology(self.term)
		self.issue_type = IssueType.objects.get(
			type='ontology',
			attribute='topic',
			field_value=obj['status'] if obj['status'] in ['obsolete', 'not_found'] else None
		)

		for topic in resource.topic.all():
			if topic.term == obj['data']['text'] or topic.uri == obj['data']['data']['uri']:
					output.append(obj['data']['text'])

		return output
