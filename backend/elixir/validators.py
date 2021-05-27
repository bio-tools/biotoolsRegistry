from rest_framework import serializers
from elixir.serializers import Ontology
import re, json
from rest_framework.validators import UniqueTogetherValidator

# this validator is a copy of UniqueTogetherValidator with one difference: it refuses when version is None
# BE ADVISED: https://github.com/tomchristie/django-rest-framework/issues/2452
class CustomUniqueTogetherValidator(UniqueTogetherValidator):
	def __call__(self, attrs):
		queryset = self.queryset
		queryset = self.filter_queryset(attrs, queryset)
		queryset = self.exclude_current_instance(attrs, queryset)

		if queryset.exists():
			field_names = ', '.join(self.fields)
			raise serializers.ValidationError(self.message.format(field_names=field_names))



def IsStringTypeValidator(value):
	#TODO make this validate a token, no newline, leading or trailing spaces, tabs, duplicated spaces
	# print "in string validator", unicode(type(value)), unicode(value)
	if not (isinstance(value, str) or isinstance(value, str)):
		message = 'Wrong type found, expected unicode/string, got '
		if isinstance(value, list):
			message += 'array/list.'
		elif isinstance(value, dict):
			message += 'dictionary/hash.'
		elif isinstance(value, int):
			message += 'integer/number.'
		else:
			message += str(type(value)) + '.'
		raise serializers.ValidationError(message)


def IsNotBlankValidator(value):
	if not value:
		message = 'This field may not be blank.'
		raise serializers.ValidationError(message)


def IsURLValidator(value):
	IsStringTypeValidator(value)
	message = 'This is not a valid URL: ' + str(value) + '.'
	if not (isinstance(value, str) or isinstance(value, str)):
		raise serializers.ValidationError(message)

	if len(value) == 0:
		message = 'This field may not be blank.'
		raise serializers.ValidationError(message)

	p = re.compile('^https?:\/\/[^\s\/$.?#].[^\s]*$', re.IGNORECASE|re.UNICODE)
	if not p.search(value):
		raise serializers.ValidationError(message)
	return value


def IsURLFTPValidator(value):
	IsStringTypeValidator(value)
	message = 'This is not a valid URL: ' + str(value) + '.'
	if not (isinstance(value, str) or isinstance(value, str)):
		raise serializers.ValidationError(message)

	if len(value) == 0:
		message = 'This field may not be blank.'
		raise serializers.ValidationError(message)
	
	p = re.compile('^(https?|s?ftp):\/\/[^\s\/$.?#].[^\s]*$', re.IGNORECASE|re.UNICODE)
	if not p.search(value):
		raise serializers.ValidationError(message)
	return value

#TODO: refactor the content to fit this
def IsPMCIDValidator(value):
	matchPMCID = re.compile('^PMC[1-9][0-9]{0,8}$', re.IGNORECASE)
	matchNone = re.compile('^None$', re.IGNORECASE)

	if not matchPMCID.search(value) and not matchNone.search(value):
		message = 'This is not a valid PMCID: ' + value + '.'
		raise serializers.ValidationError(message)

def IsPMIDValidator(value):
	matchPMID = re.compile('^[1-9][0-9]{0,8}$', re.IGNORECASE)
	matchNone = re.compile('^None$', re.IGNORECASE)

	if not matchPMID.search(value) and not matchNone.search(value):
		message = 'This is not a valid PMID: ' + value + '.'
		raise serializers.ValidationError(message)

def IsDOIValidator(value):
	# 
	#matchDOI = re.compile('^[0-9]{2}\.[0-9]{4,5}/.*$', re.IGNORECASE)

	# doi regexp (a bit modified) from 
	# https://www.crossref.org/blog/dois-and-matching-regular-expressions/ 

	# added matching for characters: '[', ']', '<' and '>'
	# old regex was '^10\.[0-9]{4,9}\/[-\._;\(\)\/:a-zA-Z0-9]+$'
	matchDOI = re.compile('^10\.[0-9]{4,9}\/[-\.\[\]<>_;\(\)\/:a-zA-Z0-9]+$', re.IGNORECASE)
	matchNone = re.compile('^None$', re.IGNORECASE)

	if not matchDOI.search(value) and not matchNone.search(value):
		message = 'This is not a valid DOI: ' + value + '.'
		raise serializers.ValidationError(message)

# def IsPublicationIDValidator(value):
# 	if isinstance(value,dict):
# 		if 'publicationsOtherID' in value.keys():
# 			value = value['publicationsOtherID']
# 	IsStringTypeValidator(value)

# 	matchPMCID = re.compile('^(PMC)[1-9][0-9]{0,8}$', re.IGNORECASE)
# 	matchPMID = re.compile('^[1-9][0-9]{0,8}$', re.IGNORECASE)
# 	matchDOI = re.compile('^(doi:)?[0-9]{2}\.[0-9]{4,5}/.*$', re.IGNORECASE)
# 	matchNone = re.compile('^None$', re.IGNORECASE)

# 	if not matchPMCID.search(value) and not matchPMID.search(value) and not matchDOI.search(value) and not matchNone.search(value):
# 		message = 'This is not a valid publication ID: ' + value + '.'
# 		raise serializers.ValidationError(message)


def IsEmailValidator(value):
	IsStringTypeValidator(value)
	p = re.compile('^[A-Za-z0-9_]+([-+.\'][A-Za-z0-9_]+)*@[A-Za-z0-9_]+([-.][A-Za-z0-9_]+)*\.[A-Za-z0-9_]+([-.][A-Za-z0-9_]+)*$', re.IGNORECASE|re.UNICODE)
	if not p.search(value):
		message = 'This is not a valid email address: ' + str(value) + '.'
		raise serializers.ValidationError(message)


def IsVersionValidator(value):
	IsStringTypeValidator(value)
	# this looks wrong
	#p = re.compile('^(?!\p{Zs})[\p{Zs}A-Za-z0-9+\.,\-_:;()]*(?<!\p{Zs})$', re.IGNORECASE|re.UNICODE)
	
	#this is ok, only allow spaces
	p = re.compile('^[ A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)
	if not p.search(value):
		message = 'This is not a valid version: ' + str(value) + '.'
		raise serializers.ValidationError(message)

def IsCollectionIDValidator(value):
	IsStringTypeValidator(value)
	# this looks wrong
	#p = re.compile('^(?!\p{Zs})[\p{Zs}A-Za-z0-9+\.,\-_:;()]*(?<!\p{Zs})$', re.IGNORECASE|re.UNICODE)
	p = re.compile('^[ A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)
	if not p.search(value):
		message = 'This is not a valid collection ID: ' + str(value) + '.'
		raise serializers.ValidationError(message)


class LengthValidator():
	def __init__(self, length):
		self.length = length
	
	def __call__(self, value):
		IsStringTypeValidator(value)
		if len(value) > self.length:
			message = 'Ensure this field has no more than ' + str(self.length) + ' characters.'
			raise serializers.ValidationError(message)


class ENUMValidator():
	def __init__(self, enum):
		self.enum = enum
	
	def __call__(self, value):
		IsNotBlankValidator(value)
		IsStringTypeValidator(value)
		check = [i for i in self.enum if i.lower() == value.lower()]
		if len(check) != 1:
			raise serializers.ValidationError('Invalid value: ' + str(value) + '.')
		return check[0]


class OntologyValidator():
	def find_term_or_uri_in_node(self, node, name_or_uri):
		if len(name_or_uri) > 0:
			e_s = {}
			if 'exact_synonyms' in node:
				e_s = {x.lower():x for x in node['exact_synonyms']}
			n_s = {}
			if 'narrow_synonyms' in node:
				n_s = {x.lower():x for x in node['narrow_synonyms']}
			if node['text'].lower() == name_or_uri.lower() or node['data']['uri'].lower() == name_or_uri.lower():
				# we are in the uri call where uri matches, perhaps the name might be a synonym, if the name even exists
				# we shouldn't be looking at self.term which is kinda like a global here...best is to rewrite all the validation
				if node['text'].lower() != name_or_uri.lower() and self.term != None:
					if self.term.lower() in e_s:
						return {'data': {'uri': node['data']['uri']},'text':e_s[self.term.lower()], 'is_synonym':'True'}
					elif self.term.lower() in n_s:
						return {'data': {'uri': node['data']['uri']},'text':n_s[self.term.lower()], 'is_synonym':'True'}
				# if not just return the regular node 
				return node
			elif name_or_uri.lower() in e_s:
				return {'data': {'uri': node['data']['uri']},'text':e_s[name_or_uri.lower()], 'is_synonym':'True'}
			elif name_or_uri.lower() in n_s:
				return {'data': {'uri': node['data']['uri']},'text':n_s[name_or_uri.lower()], 'is_synonym':'True'}
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
		# We accept Obsolete terms

		found = self.find_term_or_uri_in_node(self.EDAM_Obsolete, check_term)
		if found is not None:

			# The only thing to make sure is that they come from the same EDAM branch
			if found['data']['uri'].lower().find(self.ontology.lower().replace('edam_','')) >= 0:
				return {'status': 'ok', 'data': found}
			else:
				return {'status' : 'not_found'}


		# check if term is in ontology
		found = self.find_term_or_uri_in_node(self.EDAM_Ontology, check_term)
		if found is not None:
			if found.get('is_synonym') != 'True':
				return {'status': 'ok', 'data': found}
			else:
				return  {'status': 'ok', 'data': found, 'is_synonym':'True'}

		return {'status' : 'not_found'}

	def get_URI(self):
		return self.uri

	def get_term(self):
		return self.term

	def __init__(self, ontology):
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
				if (term and term.lower().strip() != found['data']['text'].lower() and found.get('is_synonym') != 'True'):
					message = 'The term does not match the URI: ' + term + ', ' + uri + '.'
					raise serializers.ValidationError(message)
				self.uri = found['data']['data']['uri']
				self.term = found['data']['text']
			elif found['status'] == 'not_found':
				message = 'Invalid URI: ' + uri + '.'
				raise serializers.ValidationError(message)
			# checking if the concept is an obsolete one
			elif found['status'] == 'obsolete':
				message = 'Obsolete URI: ' + found['data']['text'] + '.'
				raise serializers.ValidationError(message)
			else:
				message = 'Generic URI error'
				raise serializers.ValidationError(message)
		# if we don't have an uri then we need the term
		elif term:
			found = self.check_if_term_or_uri_in_ontology(term)
			if found['status'] == 'ok':
				self.uri = found['data']['data']['uri']
				self.term = found['data']['text']
			elif found['status'] == 'not_found':
				message = 'Invalid term: ' + term + '.'
				raise serializers.ValidationError(message)
			elif found['status'] == 'obsolete':
				message = 'Obsolete term: ' + found['data']['text'] + '.'
				raise serializers.ValidationError(message)
			else:
				message = 'Generic term error'
				raise serializers.ValidationError(message)
		else:
			message = 'Either the URI or term is required.'
			raise serializers.ValidationError(message)

