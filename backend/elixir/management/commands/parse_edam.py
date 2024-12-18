from django.core.management.base import BaseCommand, CommandError
from elasticsearch import Elasticsearch
from elixir.models import *
from xml.dom import minidom
import json, os


def f(node, term):
	if len(term) > 0:
		if node['data']['uri'] == term:
			return node
		else:
			if len(node['children']) > 0:
				for child in node['children']:
					n = f(child, term)
					if n is not None:
						return n
			else:
				return None
	return None


def getNode(node, name):
	if len(name) > 0:
		if node['text'] == name:
			return node
		else:
			if len(node['children']) > 0:
				for child in node['children']:
					n = getNode(child, name)
					if n is not None:
						return n
			else:
				return None
	return None


def getName(node):
	for n2 in node.childNodes:
		if n2.nodeName == 'rdfs:label':
			return n2.firstChild.nodeValue


def getRemoved(node):
	number = 0
	for el in node:
		if el['remove'] == 1:
			number = number + 1
	return number


def flatten(lst, node, prev):
	tmp = {}
	tmp['definition'] = ''
	tmp['path'] = {}
	tmp['path']['name'] = ''
	tmp['path']['key']  = ''
	tmp['name'] = node['text']
		
	if prev == '':
		tmp['path']['name'] = node['text']
		tmp['path']['key'] =  node['data']['uri'].lower().replace('http://edamontology.org/','')
	else:
		tmp['path']['name'] = prev['name'] + '||' + node['text']
		tmp['path']['key'] =  prev['key'] + '||' + node['data']['uri'].lower().replace('http://edamontology.org/','')

	if 'definition' in node:
		tmp['definition'] = node['definition']
	tmp['uri'] = node['data']['uri']
	tmp['exact_synonyms'] = node['exact_synonyms']
	tmp['narrow_synonyms'] = node['narrow_synonyms']

	tmp['children'] = []
	if not(tmp.get('children')):
		for ch in node['children']:
			tmp['children'].append({'name':ch['text'], 'uri':ch['data']['uri']})

	lst.append(tmp)
	if len(node['children']) > 0:
		for child in node['children']:
			flatten(lst, child, tmp['path'])
	return None


def listify(input_list):
	obj_list = []
	for el in input_list:
		node = el['node']
		if node.hasChildNodes() and el['remove'] == 0:
			if node.attributes:
				attrs = {}
				attrs['text'] = ''
				attrs['data'] = {}
				attrs['definition'] = ''
				attrs['data']['uri'] = ''
				attrs['parents'] = []
				attrs['used_parents'] = []
				attrs['remove'] = 0
				attrs['children'] = []
				attrs['exact_synonyms'] = []
				attrs['narrow_synonyms'] = []
				attrs['replaced_by'] = []
				attrs['consider'] = []
				attrs['has_input'] = []
				attrs['has_topic'] = []
				attrs['has_output'] = []
				for n2 in node.childNodes:
					if n2.nodeName == 'rdfs:label':
						attrs['text'] = n2.firstChild.nodeValue
						attrs['data']['uri'] = node.attributes['rdf:about'].value
					if n2.nodeName == 'rdfs:subClassOf':
						if n2.attributes:
							attrs['parents'].append(n2.attributes['rdf:resource'].value)
						else:
							for child in n2.childNodes:
								if child.nodeName == 'owl:Restriction':
									restriction = parse_restriction(child)
									if restriction['property'] == 'http://edamontology.org/has_input':
										attrs['has_input'].append(restriction['value'])
									elif restriction['property'] == 'http://edamontology.org/has_output':
										attrs['has_output'].append(restriction['value'])
									elif restriction['property'] == 'http://edamontology.org/has_topic':
										attrs['has_topic'].append(restriction['value'])
					if n2.nodeName == 'oboInOwl:hasExactSynonym' and n2.firstChild:
						attrs['exact_synonyms'].append(n2.firstChild.nodeValue)
					if n2.nodeName == 'oboInOwl:hasNarrowSynonym' and n2.firstChild:
						attrs['narrow_synonyms'].append(n2.firstChild.nodeValue)
					if n2.nodeName == 'oboInOwl:replacedBy' and n2.attributes['rdf:resource'].value:
						attrs['replaced_by'].append(n2.attributes['rdf:resource'].value)
					if n2.nodeName == 'oboInOwl:consider' and n2.attributes['rdf:resource'].value:
						attrs['consider'].append(n2.attributes['rdf:resource'].value)
					if n2.nodeName == 'oboInOwl:hasDefinition':
						attrs['definition'] = n2.firstChild.nodeValue
				obj_list.append(attrs)
				el['remove'] = 1
	return obj_list


def parse_restriction(restriction_node):
	restriction = {}
	for child in restriction_node.childNodes:
		if child.nodeName == 'owl:onProperty':
			restriction['property'] = child.attributes['rdf:resource'].value
		elif child.nodeName == 'owl:someValuesFrom':
			restriction['value'] = child.attributes['rdf:resource'].value
	return restriction

def treefy(node, o):
	for el in o:
		for parent in el["parents"]:
			if node["data"]["uri"] == parent:
				exists = False
				for ch in node["children"]:
					if ch["data"]["uri"] == el["data"]["uri"]:
						exists = True
				if not exists:
					node["children"].append(
						{
							"text": el["text"],
							"data": {"uri": el["data"]["uri"]},
							"children": [],
							"exact_synonyms": el["exact_synonyms"],
							"narrow_synonyms": el["narrow_synonyms"],
							"replaced_by": el["replaced_by"],
							"consider": el["consider"],
							"definition": el["definition"],
							'has_input': el.get('has_input', []),
							'has_output': el.get('has_output', []),
							'has_topic': el.get('has_topic', [])
						}
					)
	for ch in node["children"]:
		treefy(ch, o)

def minify_tree(data):
	return json.loads(json.dumps(data)
		.replace('"definition":','"d":')
		.replace('"text":','"t":')
		.replace('"narrow_synonyms":','"ns":')
		.replace('"exact_synonyms":','"es":')
		.replace('"children":','"ch":')
		.replace('"consider":','"co":')
		.replace('"replaced_by":','"rb":')
		.replace('"has_input":','"hi":')
		.replace('"has_topic":','"ht":')
		.replace('"has_output":','"ho":')
	)

def indexify(flat_data):
	index_data = {}
	for el in flat_data:
		key = el['uri'].lower().replace('http://edamontology.org/','')
		if index_data.get(key) == None:
			index_data[key] = el
			index_data[key]['path'] = [index_data[key]['path']]
		else:
			index_data[key]['path'].append(el['path'])

	return index_data

def minify_data(data):
	return json.loads(json.dumps(data).replace('http://edamontology.org/',''))

def minify_flat_data(flat_data):
	new_flat_data = []
	for e in flat_data:
		n = {}
		n['d'] = e['definition']
		n['n'] = e['name']
		n['ns'] = e['narrow_synonyms']
		n['u'] = e['uri']
		n['es'] = e['exact_synonyms']
		n['ch'] = json.loads(json.dumps(e['children'])
			.replace('"name":','"n":')
			.replace('"uri":','"u":')
		)
		n['p'] = json.loads(json.dumps(e['path'])
			.replace('"name":','"n":')
			.replace('"key":','"k":')
		)
		n['hi'] = e.get('has_input')
		n['ht'] = e.get('has_topic')
		n['ho'] = e.get('has_output')
		
		new_flat_data.append(n)

	return new_flat_data

def minify_index_data(index_data):
	new_index_data = {}
	for k in list(index_data.keys()):
		new_index_data[k] = {}
		new_index_data[k]['d'] = index_data[k]['definition']
		new_index_data[k]['n'] = index_data[k]['name']
		new_index_data[k]['ns'] = index_data[k]['narrow_synonyms']
		new_index_data[k]['u'] = index_data[k]['uri']
		new_index_data[k]['es'] = index_data[k]['exact_synonyms']
		new_index_data[k]['ns'] = index_data[k]['narrow_synonyms']
		new_index_data[k]['ch'] = json.loads(json.dumps(index_data[k]['children'])
			.replace('"name":','"n":')
			.replace('"uri":','"u":')
		)
		new_index_data[k]['p'] = json.loads(json.dumps(index_data[k]['path'])
			.replace('"name":','"n":')
			.replace('"key":','"k":')
		)
		new_index_data[k]['hi'] = index_data[k].get('has_input', [])
		new_index_data[k]['ho'] = index_data[k].get('has_output', [])
		new_index_data[k]['ht'] = index_data[k].get('has_topic', [])
	
	return new_index_data


def minify_string_data(string_data):
	return string_data.replace('http://edamontology.org/','')


def ontology_save(name, data, path_edam_json, version):

	# data -> tree of the ontology
	# flat_data -> flattened tree
	# index_data -> index tree
	flat_data = []
	flatten(flat_data, data, '')
	for el in flat_data:
		if el['definition'] == '' and el['name'] == '' and el['uri'] == '':
			flat_data.remove(el)
	index_data = indexify(flat_data)
	min_data = minify_data(data)
	min_data = minify_tree(min_data)
	
	# if name != 'EDAM_obsolete':
	# 	min_data = minify_tree_properties(min_data, False)
	# else:
	# 	min_data = minify_tree_properties(min_data, True)

	min_flat_data = minify_data(flat_data)
	min_flat_data = minify_flat_data(min_flat_data)
	min_index_data = minify_data(index_data)
	min_index_data = minify_index_data(min_index_data)

	# Generic unversioned (latest) EDAM

	# regular data + min data
	with open(path_edam_json + '/current/' + name + '.json', 'w') as outfile:
		json.dump(data, outfile)
	with open(path_edam_json + '/current/min_' + name + '.json', 'w') as outfile:
		json.dump(min_data, outfile)

	# flat data + min flat data
	with open(path_edam_json + '/current/flat_' + name + '.json', 'w') as outfile:
		json.dump(flat_data, outfile)
	with open(path_edam_json + '/current/min_flat_' + name + '.json', 'w') as outfile:
		json.dump(min_flat_data, outfile)
	
	# index data + min index data
	with open(path_edam_json + '/current/index_' + name + '.json', 'w') as outfile:
		json.dump(index_data, outfile)
	with open(path_edam_json + '/current/min_index_' + name + '.json', 'w') as outfile:
		json.dump(min_index_data, outfile)

	# Versioned EDAM

	# regular data + min data
	with open(path_edam_json + '/' + version + '/' + name + '_' + version + '.json', 'w') as outfile:
		json.dump(data, outfile)
	with open(path_edam_json + '/' + version + '/min_' + name + '_' + version + '.json', 'w') as outfile:
		json.dump(min_data, outfile)
	
	# flat data + min flat data
	with open(path_edam_json + '/' + version + '/flat_' + name + '_' + version + '.json', 'w') as outfile:
		json.dump(flat_data, outfile)
	with open(path_edam_json + '/' + version + '/min_flat_' + name + '_' + version + '.json', 'w') as outfile:
		json.dump(min_flat_data, outfile)

	# index data + min index data
	with open(path_edam_json + '/' + version + '/index_' + name + '_' + version + '.json', 'w') as outfile:
		json.dump(index_data, outfile)
	with open(path_edam_json + '/' + version + '/min_index_' + name + '_' + version + '.json', 'w') as outfile:
		json.dump(min_index_data, outfile)


	ontology_structure_json = json.dumps(data)
	min_ontology_structure_json = json.dumps(min_data)
	
	flat_data_structure_json = json.dumps(flat_data)
	min_flat_data_structure_json = json.dumps(min_flat_data)

	index_data_structure_json = json.dumps(index_data)
	min_index_data_structure_json = json.dumps(min_index_data)

	# regular EDAM
	# populating a fresh DB 'current'
	query = Ontology.objects.filter(name__exact=name)
	if len(query) == 0:
		o = Ontology(name=name, data=ontology_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + name)

	# populating a DB with version EDAM
	query = Ontology.objects.filter(name__exact=name + '_' + version)
	if len(query) == 0:
		o = Ontology(name=name + '_' + version, data=ontology_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + name + '_' + version)

	# flat EDAM
	# populating a fresh DB 'current'
	query = Ontology.objects.filter(name__exact='flat_' + name)
	if len(query) == 0:
		o = Ontology(name='flat_' + name, data=flat_data_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(flat_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + 'flat_' + name)

	# populating a DB with version EDAM
	query = Ontology.objects.filter(name__exact='flat_' + name + '_' + version)
	if len(query) == 0:
		o = Ontology(name='flat_' + name + '_' + version, data=flat_data_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(flat_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + 'flat_' + name + '_' + version)

	# index EDAM
	# populating a fresh DB 'current'
	query = Ontology.objects.filter(name__exact='index_' + name)
	if len(query) == 0:
		o = Ontology(name='index_' + name, data=index_data_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(index_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + 'index_' + name)

	# populating a DB with version EDAM
	query = Ontology.objects.filter(name__exact='index_' + name + '_' + version)
	if len(query) == 0:
		o = Ontology(name='index_' + name + '_' + version, data=index_data_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(index_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + 'index_' + name + '_' + version)


	# min regular EDAM
	# populating a fresh DB 'current'
	query = Ontology.objects.filter(name__exact='min_' + name)
	if len(query) == 0:
		o = Ontology(name='min_' + name, data=min_ontology_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(min_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + name)

	# populating a DB with version EDAM
	query = Ontology.objects.filter(name__exact='min_' + name + '_' + version)
	if len(query) == 0:
		o = Ontology(name='min_' + name + '_' + version, data=min_ontology_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(min_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING min_' + name + '_' + version)

	# min flat EDAM
	# populating a fresh DB 'current'
	query = Ontology.objects.filter(name__exact='min_flat_' + name)
	if len(query) == 0:
		o = Ontology(name='min_flat_' + name, data=min_flat_data_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(min_flat_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + 'min_flat_' + name)

	# populating a DB with version EDAM
	query = Ontology.objects.filter(name__exact='min_flat_' + name + '_' + version)
	if len(query) == 0:
		o = Ontology(name='min_flat_' + name + '_' + version, data=min_flat_data_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(min_flat_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + 'min_flat_' + name + '_' + version)

	
	# min index EDAM
	# populating a fresh DB 'current'
	query = Ontology.objects.filter(name__exact='min_index_' + name)
	if len(query) == 0:
		o = Ontology(name='min_index_' + name, data=min_index_data_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(min_index_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + 'min_index_' + name)

	# populating a DB with version EDAM
	query = Ontology.objects.filter(name__exact='min_index_' + name + '_' + version)
	if len(query) == 0:
		o = Ontology(name='min_index_' + name + '_' + version, data=min_index_data_structure_json)
		o.save()
	# updating records
	elif len(query) == 1:
		o = query[0]
		o.data = json.dumps(min_index_data)
		o.save()
	else:
		self.stdout.write('ERROR PARSING ' + 'min_index_' + name + '_' + version)

class Command(BaseCommand):
	help = 'Regenerate the EDAM ontology'

	def handle(self, *args, **options):
		version = ''
		# path_edam_data = '/elixir/application/backend/data/edam'
		path_edam_data = './data/edam'
		with open(path_edam_data + '/current_version.txt') as f:
			version = f.read().strip('\n')
		path_edam_json = path_edam_data + '/json'

		self.stdout.write('------------------------------------')
		self.stdout.write('Regenerating the EDAM version '+ version)

		xmldoc = minidom.parse(path_edam_data + '/owl/EDAM_' + version + '.owl')
		il = xmldoc.getElementsByTagName('owl:Class')

		topic_list = []
		operation_list = []
		data_list = []
		format_list = []
		obsolete_list = []

		for el in il:
			marker = None
			try:
				marker = el.attributes['rdf:about'].nodeValue
			except:
				marker = None
				continue
			if marker is not None:
				if 'http://edamontology.org/' in marker:
					obsolete = False
					for n in el.childNodes:
						if n.nodeName == 'rdfs:subClassOf' and n.attributes and not obsolete:
							if n.attributes['rdf:resource'].value == 'http://www.w3.org/2002/07/owl#DeprecatedClass':
								obsolete = True
					if obsolete:
						obsolete_list.append({'remove':0,'node':el})
					else:
						if 'http://edamontology.org/topic_' in marker:
							topic_list.append({'remove':0,'node':el})
						elif 'http://edamontology.org/operation_' in marker:
							operation_list.append({'remove':0,'node':el})
						elif 'http://edamontology.org/data_' in marker:
							data_list.append({'remove':0,'node':el})
						elif 'http://edamontology.org/format_' in marker:
							format_list.append({'remove':0,'node':el})

		obsolete_tree = {
			'text': 'Deprecated',
			'data': {
				'uri': 'http://www.w3.org/2002/07/owl#DeprecatedClass'
			},
			"narrow_synonyms": [],
			"exact_synonyms": [],
			'children': []
		}
		treefy(obsolete_tree, listify(obsolete_list))
		
		topic_tree = {
			'text': 'Topic',
			'data': {
				'uri': 'http://edamontology.org/topic_0003'
			},
			'definition':'A category denoting a rather broad domain or field of interest, of study, application, work, data, or technology. Topics have no clearly defined borders between each other.',
			'exact_synonyms':[],
			'narrow_synonyms': [],
			'children': []

		}
		treefy(topic_tree, listify(topic_list))

		operation_tree = {
			'text': 'Operation',
			'data': {
				'uri': 'http://edamontology.org/operation_0004'
			},
			'definition':'A function that processes a set of inputs and results in a set of outputs, or associates arguments (inputs) with values (outputs). Special cases are: a) An operation that consumes no input (has no input arguments). Such operation is either a constant function, or an operation depending only on the underlying state. b) An operation that may modify the underlying state but has no output. c) The singular-case operation with no input or output, that still may modify the underlying state.',
			'exact_synonyms':[],
			'narrow_synonyms': ['Computational procedure', 'Computational subroutine', 'Computational tool', 'Computational operation', 'Function (programming)', 'Lambda abstraction', 'sumo:Function', 'Mathematical function', 'Process', 'Mathematical operation', 'Function', 'Computational method'],
			'children': []
		}
		treefy(operation_tree, listify(operation_list))

		data_tree = {
			'text': 'Data',
			'data': {
				'uri': 'http://edamontology.org/data_0006'
			},
			'definition':"Information, represented in an information artefact (data record) that is 'understandable' by dedicated computational tools that can use the data as input or produce it as output.",
			'exact_synonyms': ["Data record"],
			'narrow_synonyms': ["Data set","Datum"],
			'children': []
		}
		treefy(data_tree, listify(data_list))

		format_tree = {
			'text': 'Format',
			'data': {
				'uri': 'http://edamontology.org/format_1915'
			},
			'definition':"A defined way or layout of representing and structuring data in a computer file, blob, string, message, or elsewhere. The main focus in EDAM lies on formats as means of structuring data exchanged between different tools or resources. The serialisation, compression, or encoding of concrete data formats/models is not in scope of EDAM. Format 'is format of' Data.",
			'exact_synonyms':["Exchange format","Data format"],
			'narrow_synonyms': ["File format"],
			'children': []
		}
		treefy(format_tree, listify(format_list))


		############################### Dirs
		# version folder
		if not os.path.exists(path_edam_json + '/' + version):
			os.makedirs(path_edam_json + '/' + version)
		
		if not os.path.exists(path_edam_json + '/current'):
			os.makedirs(path_edam_json + '/current')

		############################### Topic
		ontology_save('EDAM_Topic', topic_tree, path_edam_json, version)
		self.stdout.write('Topic saved.')

		############################### Operation
		ontology_save('EDAM_Operation', operation_tree, path_edam_json, version)
		self.stdout.write('Operation saved.')

		############################### Data
		ontology_save('EDAM_Data', data_tree, path_edam_json, version)
		self.stdout.write('Data saved.')

		############################### Format
		ontology_save('EDAM_Format', format_tree, path_edam_json, version)
		self.stdout.write('Format saved.')

		############################### Obsolete
		ontology_save('EDAM_obsolete', obsolete_tree, path_edam_json, version)
		self.stdout.write('Obsolete saved.')


		self.stdout.write('All done.')
