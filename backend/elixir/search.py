from elixir.models import *
from rest_framework.settings import api_settings
from elasticsearch import Elasticsearch
from django.conf import settings
import elixir.search_settings, re
import json

es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)

def _byteify(data, ignore_dicts = False):
		# if this is a unicode string, return its string representation
		if isinstance(data, str):
				return data.encode('utf-8')
		# if this is a list of values, return list of byteified values
		if isinstance(data, list):
				return [ _byteify(item, ignore_dicts=True) for item in data ]
		# if this is a dictionary, return dictionary of byteified keys and values
		# but only if we haven't already byteified it
		if isinstance(data, dict) and not ignore_dicts:
				return {
						_byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
						for key, value in data.items()
				}
		# if it's anything else, return it in its original form
		return data

def json_loads_byteified(json_text):
		return _byteify(
				json.loads(json_text, object_hook=_byteify),
				ignore_dicts=True
		)


def format_search(attribute, search_field, search_text,search_struct, elastic_query, query_type):
	q = elastic_query[search_struct[attribute][query_type]]
	q_formatted = q % {"field":search_field,"search_text":search_text}
	#return q
	#return q_formatted
	
	return json.loads(q_formatted)
	# return json_loads_byteified(q_formatted)

def get_list_of_terms(field):
	query_struct = {
		'size': 0,
		'aggs' : {
			field : {
				'terms': {
					'field': field,
					'size': 50000
				}
			}
		}
	}
	
	result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body=query_struct)
	return [x['key'] for x in result['aggregations'][field]['buckets']]


def get_exact_term(term, field):
	term_lower = term.lower()
	o_list = get_list_of_terms(field)
	for o in o_list:
		if term_lower == o.lower():
			return o
	return False


def construct_es_query(query_dict):
	page = int(query_dict.get('page', '1'))
	q = query_dict.get('q', None)
	sort_attribute = query_dict.get('sort', None)
	sort_order = query_dict.get('ord', None) or 'desc'
	search_struct = elixir.search_settings.search_struct
	elastic_query = elixir.search_settings.elastic_query

	query_struct = {
		'size': api_settings.PAGE_SIZE,
		'from': api_settings.PAGE_SIZE*(page-1),
		'query': {},
		'sort': {
			'lastUpdate': {
				'order': 'desc'
			}
		},
		'track_total_hits': True
	}

	if sort_attribute and (sort_attribute in ['score', 'lastUpdate', 'name', 'additionDate', 'citationCount', 'citationDate']):
		if sort_attribute == 'score':
			sort_attribute = '_score'
		elif sort_attribute == 'citationCount':
			sort_attribute = 'publication.metadata.citationCount'
		elif sort_attribute == 'citationDate':
			sort_attribute = 'publication.metadata.date'

		query_struct['sort'] = {
			sort_attribute:  {
				'order': sort_order
			}
		}

	query_struct['query']['bool'] = {
		'must': [],
		'should': []
	}

	# if 'everything' search used
	if q:
		# search terms in quotes
		exact = re.findall(r"""[\"'](.+?)[\"']""", q)
		# search terms outside of quotes
		trimmed = re.sub(r"[\"'](.+?)[\"']",'', q)
		# remove weird symbols
		trimmed = re.sub(r"[^\w_-]", ' ', trimmed)
		# remaining search terms
		rest = re.findall(r"[\w'-_\\/]+", trimmed)
		

		# construct query for terms in quotes
		for term in exact:
			dis_max = {"dis_max": {
				"queries": [
					{ "match_phrase": { "name": {"query": term, "boost": 10.0 }}},
					{ "match_phrase": { "description":  {"query": term, "boost": 0.05 } }},
					{ "match_phrase": { "collectionID": {"query": term, "boost": 4.0 } }},
					{ "match_phrase": { "topic.term":  {"query": term, "boost": 0.5 } }},
					{ "match_phrase": { "function.operation.term":  {"query": term, "boost": 0.5 } }},
					{ "match_phrase": { "function.input.data.term":  {"query": term, "boost": 0.5 } }},
					{ "match_phrase": { "function.input.format.term":  {"query": term, "boost": 0.5 } }},
					{ "match_phrase": { "function.output.data.term":  {"query": term, "boost": 0.5 } }},
					{ "match_phrase": { "function.output.format.term":  {"query": term, "boost": 0.5 } }},
					{ "match_phrase": { "function.note":  {"query": term, "boost": 0.5 } }},
					#{ "match_phrase": { "contact.name":  {"query": term, "boost": 0.5 } }},
					{ "match_phrase": { "credit.name":  {"query": term, "boost": 0.5 } }},
					{ "match_phrase": { "credit.note":  {"query": term, "boost": 0.05 } }},
					{ "match_phrase": { "documentation.note":  {"query": term, "boost": 0.05 } }},
					{ "match_phrase": { "language": {"query": term, "boost": 0.5 }}},
					{ "match_phrase": { "license": {"query": term, "boost": 0.5 }}},
					{ "match_phrase": { "operatingSystem": {"query": term, "boost": 0.5 }}},
					{ "match_phrase": { "toolType": {"query": term, "boost": 0.5 }}},
					{ "match_phrase": { "version.version": {"query": term, "boost": 1.0 }}}
				],
				"tie_breaker": 0.6
			}}
			query_struct['query']['bool']['must'].append(dis_max)

		# construct query for terms outside of quotes
		for term in rest:
			dis_max = {"dis_max": {
				"queries": [
					# this should be "biotoolsID" instead of "id"
					{ "match": { "biotoolsID": {"query": term, "boost": 40.0 }}},
					{ "match": { "name": {"query": term, "boost": 20.0 }}},
					{ "prefix": { "name":  {"value": term, "boost": 15.0 } }},
					{ "wildcard" : { "name" : { "value" : "*"+term+"*", "boost" : 10.0 } }},
					{ "match": { "name.raw": {"query": term, "boost": 200.0 }}},
					{ "prefix": { "name.raw":  {"value": term, "boost": 150.0 } }},
					{ "wildcard" : { "name.raw" : { "value" : "*"+term+"*", "boost" : 100.0 } }},
					{ "match": { "description":  {"query": term, "boost": 0.05 } }},
					{ "match": { "collectionID": {"query": term, "boost": 4.0 } }},
					{ "prefix": { "collectionID": {"value": term, "boost": 2.0 } }},
					{ "match": { "topic.term":  {"query": term, "boost": 0.5 } }},
					{ "match": { "function.operation.term":  {"query": term, "boost": 0.5 } }},
					{ "match": { "function.input.data.term":  {"query": term, "boost": 0.5 } }},
					{ "match": { "function.input.format.term":  {"query": term, "boost": 0.5 } }},
					{ "match": { "function.output.data.term":  {"query": term, "boost": 0.5 } }},
					{ "match": { "function.output.format.term":  {"query": term, "boost": 0.5 } }},
					{ "match": { "function.note":  {"query": term, "boost": 0.05 } }},
					#{ "match": { "contact.name":  {"query": term, "boost": 0.5 } }},
					{ "match": { "credit.name":  {"query": term, "boost": 0.5 } }},
					{ "match": { "credit.note":  {"query": term, "boost": 0.05 } }},
					{ "match": { "documentation.note":  {"query": term, "boost": 0.05 } }},
					{ "match": { "language": {"query": term, "boost": 0.5 }}},
					{ "match": { "license": {"query": term, "boost": 0.5 }}},
					{ "match": { "operatingSystem": {"query": term, "boost": 0.5 }}},
					{ "match": { "toolType": {"query": term, "boost": 0.5 }}},
					{ "match": { "version.version": {"query": term, "boost": 1.0 }}}
				],
				"tie_breaker": 0.6
			}}
			query_struct['query']['bool']['must'].append(dis_max)

	# search other than 'everything'
	for attribute in list(query_dict.keys()):
		# only on possible search attributes
		if attribute in list(search_struct.keys()):
			search_value = query_dict.get(attribute, None)
			# search terms in quotes
			exact = re.findall(r"""[\"'](.+?)[\"']""", search_value)
			# search terms outside of quotes
			trimmed = re.sub(r"[\"'](.+?)[\"']",'', search_value)
			# remove weird symbols
			trimmed = re.sub(r"[^\w_-]", ' ', trimmed)
			# remaining search terms
			rest = re.findall(r"[\w'-_\\/]+", trimmed)

			for term in exact:
				inner_should = {
					"bool": {
						"should": []
					}
				}
				for field in search_struct[attribute]['search_field']:
					# inner_should['bool']['should'].append(
					# 	{
					# 		'match_phrase': {
					# 			field: term
					# 		}
					# 	}
					# )
					inner_should['bool']['should'].extend(
						format_search(attribute,field,term, search_struct, elastic_query, "quoted_query")
						)
				query_struct['query']['bool']['must'].append(inner_should)

			inexact = ' '.join(rest)
			if inexact:
				inner_should = {
					"bool": {
						"should": []
					}
				}
				for field in search_struct[attribute]['search_field']:
					# inner_should['bool']['should'].extend([
					# 	#{
					# 	#	'fuzzy': {
					# 	#		field: {
					# 	#			'value': inexact
					# 	#		}
					# 	#	}
					# 	#}
					# 	{
					# 		"match": {
 				# 				field:{
					# 				"query": inexact,
					# 					"fuzziness": 2
					# 				}
					# 			}
					# 		},
					# 		{
					# 		"prefix": {
 				# 				field:{
					# 				"value": inexact
					# 				}
					# 			}
					# 		}

					# ])
					inner_should['bool']['should'].extend(
						format_search(attribute,field,inexact, search_struct, elastic_query, "simple_query")
						)
				query_struct['query']['bool']['must'].append(inner_should)
	return query_struct
