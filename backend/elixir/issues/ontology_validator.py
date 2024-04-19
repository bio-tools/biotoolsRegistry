from elixir.models import *
import json

class IssueOntologyValidator(object):
	def find_term_or_uri_in_node(self, node, name_or_uri):
		if len(name_or_uri) > 0:
			e_s = {}
			if 'exact_synonyms' in node:
				e_s = {x.lower():x for x in node['exact_synonyms']}
			n_s = {}
			if 'narrow_synonyms' in node:
				n_s = {x.lower():x for x in node['narrow_synonyms']}
			if node['text'].lower() == name_or_uri.lower() or node['data']['uri'].lower() == name_or_uri.lower():
				return node
			elif name_or_uri.lower() in e_s:
				return {'data': {'uri': node['data']['uri']},'text':e_s[name_or_uri.lower()]}
			elif name_or_uri.lower() in n_s:
				return {'data': {'uri': node['data']['uri']},'text':n_s[name_or_uri.lower()]}
			else:
				if len(node['children']) > 0:
					for child in node['children']:
						n = self.find_term_or_uri_in_node(child, name_or_uri)
						if n is not None:
							return n
				else:
					return None
		return None

	def check_if_term_or_uri_in_ontology(self, check_term):
		# check if term is obsolete
		found = self.find_term_or_uri_in_node(self.EDAM_Obsolete, check_term)
		if found:
			return {'status': 'obsolete', 'data': found}

		# check if term is in ontology
		found = self.find_term_or_uri_in_node(self.EDAM_Ontology, check_term)
		if found is not None:
			return {'status' : 'ok', 'data' : found}

		return {'status' : 'not_found'}

	def get_URI(self):
		return self.uri

	def get_term(self):
		return self.term

	def __init__(self, ontology):
		# from elixir.models import *
		# import json
		self.ontology = ontology
		self.uri = None
		self.term = None
		# load obsolete terms from DB
		EDAM_o_db = Ontology.objects.get(name='EDAM_obsolete')
		self.EDAM_Obsolete = json.loads(EDAM_o_db.data)
		# load ontology from DB
		EDAM_db = Ontology.objects.get(name=self.ontology)
		self.EDAM_Ontology = json.loads(EDAM_db.data)

	def __call__(self, uri, term):
		self.uri = uri
		self.term = term
		# return True

		# if we have non-empty URI
		if uri and len(uri) > 0:
			found = self.check_if_term_or_uri_in_ontology(uri)
			# URI takes precedense over term, so if URI matches the one found in EDAM
			# we replace the term with the one from EDAM (EDAM is assumed to have the correct term)
			if found['status'] == 'ok':
				# make sure the term matches the URI
				self.uri = found['data']['data']['uri']
				self.term = found['data']['text']
			elif found['status'] == 'not_found':
				message = 'Invalid URI: ' + uri + '.'
			# checking if the concept is an obsolete one
			elif found['status'] == 'obsolete':
				message = 'Obsolete URI: ' + found['data']['text'] + '.'
			else:
				message = 'Generic URI error'
		# if we don't have an uri then we need the term
		elif term:
			found = self.check_if_term_or_uri_in_ontology(term)
			if found['status'] == 'ok':
				self.uri = found['data']['data']['uri']
				self.term = found['data']['text']
			elif found['status'] == 'not_found':
				message = 'Invalid term: ' + term + '.'
				
			elif found['status'] == 'obsolete':
				message = 'Obsolete term: ' + found['data']['text'] + '.'
				
			else:
				message = 'Generic term error'
				
		else:
			message = 'Either the URI or term is required.'
			

