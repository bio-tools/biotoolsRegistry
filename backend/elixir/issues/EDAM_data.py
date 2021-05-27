from elixir.models import IssueType
from .ontology_validator import IssueOntologyValidator
from . import IssueBaseClass


class EDAMDataIssue(IssueBaseClass):
	
	def __init__(self, qset, user, term='Data'):
		self.term = term
		self.ov = IssueOntologyValidator('EDAM_data')
		super(
			EDAMDataIssue,
			self
			).__init__(
			_qset=qset,
			_type=IssueType.objects.get(
				type='ontology',
				attribute='data',
				field_value=None
			),
			_user=user
		)

	def detect(self, resource):
		output = []

		obj = self.ov.check_if_term_or_uri_in_ontology(self.term)
		self.issue_type = IssueType.objects.get(
			type='ontology',
			attribute='data',
			field_value=obj['status'] if obj['status'] in ['obsolete', 'not_found'] else None
		)
		
		for function in resource.function.all():
			for inp in function.input.all():
				if inp.data:
					if inp.data.term == obj['data']['text'] or inp.data.uri == obj['data']['data']['uri']:
						output.append('Input - ' + obj['data']['text'])

			for out in function.output.all():
				if out.data:
					if out.data.term == obj['data']['text'] or out.data.uri == obj['data']['data']['uri']:
						output.append('Output - ' + obj['data']['text'])

		return output
