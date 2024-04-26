from elixir.models import IssueType
from .ontology_validator import IssueOntologyValidator
from . import IssueBaseClass


class EDAMOperationIssue(IssueBaseClass):

	def __init__(self, qset, user, term='Operation'):
		self.term = term
		self.ov = IssueOntologyValidator('EDAM_operation')
		super(
			EDAMOperationIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='ontology',
				attribute='operation',
				field_value=None
			),
			_user=user
		)

	def detect(self, resource):
		output = []

		obj = self.ov.check_if_term_or_uri_in_ontology(self.term)
		self.issue_type = IssueType.objects.get(
			type='ontology',
			attribute='operation',
			field_value=obj['status'] if obj['status'] in ['obsolete', 'not_found'] else None
		)
		
		for function in resource.function.all():
			for operation in function.operation.all():
				if operation.term == obj['data']['text'] or operation.uri == obj['data']['data']['uri']:
						output.append('Operation - ' + obj['data']['text'])
		
		return output
