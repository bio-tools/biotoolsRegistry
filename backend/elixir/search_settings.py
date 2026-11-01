search_struct = {
	'biotoolsID': {
		'attribute': 'biotoolsID',
		'search_field': ['biotoolsID'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'name': {
		'attribute': 'name',
		'search_field': ['name.raw','name'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'topic': {
		'attribute': 'topic',
		'search_field': ['topic.term.raw', 'topic.term'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'topicID': {
		'attribute': 'topicID',
		'search_field': ['topic.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'function': {
		'attribute': 'function',
		'search_field': ['function.operation.term.raw','function.operation.term','function.input.data.term.raw', 'function.input.format.term.raw', 'function.input.data.term', 'function.input.format.term', 'function.output.format.term.raw', 'function.output.data.term.raw', 'function.output.format.term', 'function.output.data.term','function.note','function.cmd'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'operation': {
		'attribute': 'operation',
		'search_field': ['function.operation.term.raw', 'function.operation.term'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'operationID': {
		'attribute': 'operationID',
		'search_field': ['function.operation.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'dataType': {
		'attribute': 'dataType',
		'search_field': ['function.input.data.term.raw','function.input.data.term','function.output.data.term', 'function.output.data.term.raw'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'dataTypeID': {
		'attribute': 'dataTypeID',
		'search_field': ['function.input.data.uri','function.output.data.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'dataFormat': {
		'attribute': 'dataFormat',
		'search_field': ['function.input.format.term.raw','function.input.format.term','function.output.format.term', 'function.output.format.term.raw'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'dataFormatID': {
		'attribute': 'dataFormatID',
		'search_field': ['function.input.format.uri','function.output.format.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'input': {
		'attribute': 'input',
		'search_field': ['function.input.data.term.raw', 'function.input.format.term.raw', 'function.input.data.term', 'function.input.format.term'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'inputID': {
		'attribute': 'inputID',
		'search_field': ['function.input.data.uri', 'function.input.format.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'inputDataFormat': {
		'attribute': 'inputDataFormat',
		'search_field': ['function.input.format.term.raw', 'function.input.format.term'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'inputDataFormatID': {
		'attribute': 'inputDataFormatID',
		'search_field': ['function.input.format.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'inputDataType': {
		'attribute': 'inputDataType',
		'search_field': ['function.input.data.term.raw','function.input.data.term'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'inputDataTypeID': {
		'attribute': 'inputDataTypeID',
		'search_field': ['function.input.data.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'output': {
		'attribute': 'output',
		'search_field': ['function.output.format.term.raw', 'function.output.data.term.raw', 'function.output.format.term', 'function.output.data.term'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'outputID': {
		'attribute': 'outputID',
		'search_field': ['function.output.data.uri', 'function.output.format.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'outputDataFormat': {
		'attribute': 'outputDataFormat',
		'search_field': ['function.output.format.term.raw','function.output.format.term'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'outputDataFormatID': {
		'attribute': 'outputDataFormatID',
		'search_field': ['function.output.format.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'outputDataType': {
		'attribute': 'outputDataType',
		'search_field': ['function.output.data.term.raw','function.output.data.term'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'outputDataTypeID': {
		'attribute': 'outputDataTypeID',
		'search_field': ['function.output.data.uri'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'homepage': {
		'attribute': 'homepage',
		'search_field': ['homepage'],
		'exact': False,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'description': {
		'attribute': 'description',
		'search_field': ['description'],
		'exact': False,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'version': {
		'attribute': 'version',
		'search_field': ['version'],
		'exact': False,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'toolType': {
		'attribute': 'toolType',
		'search_field': ['toolType'],
		'exact': False,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'collectionID': {
		'attribute': 'collectionID',
		'search_field': ['collectionID'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'maturity': {
		'attribute': 'maturity',
		'search_field': ['maturity'],
		'exact': False,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'operatingSystem': {
		'attribute': 'operatingSystem',
		'search_field': ['operatingSystem'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'language': {
		'attribute': 'language',
		'search_field': ['language'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'cost': {
		'attribute': 'cost',
		'search_field': ['cost'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'license': {
		'attribute': 'license',
		'search_field': ['license'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'accessibility': {
		'attribute': 'accessibility',
		'search_field': ['accessibility'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'credit': {
		'attribute': 'credit',
		'search_field': ['credit.name.raw', 'credit.name', 'credit.note', 'credit.typeRole', 'credit.typeEntity', 'credit.orcidid', 'credit.url','credit.email'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'creditName': {
		'attribute': 'creditName',
		'search_field': ['credit.name.raw', 'credit.name'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'creditTypeRole': {
		'attribute': 'creditTypeRole',
		'search_field': ['credit.typeRole'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'creditTypeEntity': {
		'attribute': 'creditTypeEntity',
		'search_field': ['credit.typeEntity'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'creditOrcidID': {
		'attribute': 'creditOrcidID',
		'search_field': ['credit.orcidid'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'creditGridID': {
		'attribute': 'creditGridID',
		'search_field': ['credit.gridid'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'creditRORID': {
		'attribute': 'creditRORID',
		'search_field': ['credit.rorid'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'creditFundRefID': {
		'attribute': 'creditFundRefID',
		'search_field': ['credit.fundrefid'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'publication': {
		'attribute': 'publication',
		'search_field': ['publication.doi', 'publication.pmid', 'publication.pmcid','publication.type','publication.version'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'publicationID': {
		'attribute': 'publicationID',
		'search_field': ['publication.doi', 'publication.pmid', 'publication.pmcid'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'publicationType': {
		'attribute': 'publicationType',
		'search_field': ['publication.type'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'publicationVersion': {
		'attribute': 'publicationVersion',
		'search_field': ['publication.version'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'link': {
		'attribute': 'link',
		'search_field': ['link.url','link.type','link.note'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'linkType': {
		'attribute': 'linkType',
		'search_field': ['link.type'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'documentation': {
		'attribute': 'documentation',
		'search_field': ['documentation.note','documentation.url','documentation.type'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'documentationType': {
		'attribute': 'documentationType',
		'search_field': ['documentation.type'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'download': {
		'attribute': 'download',
		'search_field': ['download.note','download.url','download.type','download.version'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'downloadType': {
		'attribute': 'downloadType',
		'search_field': ['download.type'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'downloadVersion': {
		'attribute': 'downloadVersion',
		'search_field': ['download.version'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'otherID': {
		'attribute': 'otherID',
		'search_field': ['otherID.value','otherID.type','otherID.version'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'otherIDType': {
		'attribute': 'otherIDType',
		'search_field': ['otherID.type'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'otherIDVersion': {
		'attribute': 'otherIDVersion',
		'search_field': ['otherID.version'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'otherIDValue': {
		'attribute': 'otherIDValue',
		'search_field': ['otherID.value'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'elixirNode': {
		'attribute': 'elixirNode',
		'search_field': ['elixirNode'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'elixirPlatform': {
		'attribute': 'elixirPlatform',
		'search_field': ['elixirPlatform'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'elixirCommunity': {
		'attribute': 'elixirCommunity',
		'search_field': ['elixirCommunity'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	},
	'owner': {
		'attribute': 'owner',
		'search_field': ['owner'],
		'exact': True,
		'simple_query':'default',
		'quoted_query':'phrase'
	}
}

elastic_query = {
	"default":
	"""
	[
		{
		"match": {
			"%(field)s":{
				"query": "%(search_text)s",
					"fuzziness": 2
				}
			}
		},
		{
		"prefix": {
			"%(field)s":{
				"value": "%(search_text)s"
				}
			}
		}
	]
	"""
	,
	"phrase":
	"""
	[
		{
		"match_phrase": {
			"%(field)s": "%(search_text)s"
			}
		}
	]
	"""
	,
	"simple_match":
	"""
	[
		{
		"match": {
			"%(field)s": "%(search_text)s"
			}
		}
	]
	"""
}