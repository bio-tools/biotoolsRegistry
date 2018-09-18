search_struct = {
	'biotoolsID': {
		'attribute': 'biotoolsID',
		'search_field': ['biotoolsID'],
		'exact': True
	},
	'name': {
		'attribute': 'name',
		'search_field': ['name.raw','name'],
		'exact': True
	},
	'topic': {
		'attribute': 'topic',
		'search_field': ['topic.term.raw', 'topic.term'],
		'exact': True
	},
	'topicID': {
		'attribute': 'topicID',
		'search_field': ['topic.uri'],
		'exact': True
	},
	'function': {
		'attribute': 'function',
		'search_field': ['function.operation.term.raw','function.operation.term','function.input.data.term.raw', 'function.input.format.term.raw', 'function.input.data.term', 'function.input.format.term', 'function.output.format.term.raw', 'function.output.data.term.raw', 'function.output.format.term', 'function.output.data.term','function.note','function.cmd'],
		'exact': True
	},
	'operation': {
		'attribute': 'operation',
		'search_field': ['function.operation.term.raw', 'function.operation.term'],
		'exact': True
	},
	'operationID': {
		'attribute': 'operationID',
		'search_field': ['function.operation.uri'],
		'exact': True
	},
	'dataType': {
		'attribute': 'dataType',
		'search_field': ['function.input.data.term.raw','function.input.data.term','function.output.data.term', 'function.output.data.term.raw'],
		'exact': True
	},
	'dataTypeID': {
		'attribute': 'dataTypeID',
		'search_field': ['function.input.data.uri','function.output.data.uri'],
		'exact': True
	},
	'dataFormat': {
		'attribute': 'dataFormat',
		'search_field': ['function.input.format.term.raw','function.input.format.term','function.output.format.term', 'function.output.format.term.raw'],
		'exact': True
	},
	'dataFormatID': {
		'attribute': 'dataFormatID',
		'search_field': ['function.input.format.uri','function.output.format.uri'],
		'exact': True
	},
	'input': {
		'attribute': 'input',
		'search_field': ['function.input.data.term.raw', 'function.input.format.term.raw', 'function.input.data.term', 'function.input.format.term'],
		'exact': True
	},
	'inputID': {
		'attribute': 'inputID',
		'search_field': ['function.input.data.uri', 'function.input.format.uri'],
		'exact': True
	},
	'inputDataFormat': {
		'attribute': 'inputDataFormat',
		'search_field': ['function.input.format.term.raw', 'function.input.format.term'],
		'exact': True
	},
	'inputDataFormatID': {
		'attribute': 'inputDataFormatID',
		'search_field': ['function.input.format.uri'],
		'exact': True
	},
	'inputDataType': {
		'attribute': 'inputDataType',
		'search_field': ['function.input.data.term.raw','function.input.data.term'],
		'exact': True
	},
	'inputDataTypeID': {
		'attribute': 'inputDataTypeID',
		'search_field': ['function.input.data.uri'],
		'exact': True
	},
	'output': {
		'attribute': 'output',
		'search_field': ['function.output.format.term.raw', 'function.output.data.term.raw', 'function.output.format.term', 'function.output.data.term'],
		'exact': True
	},
	'outputID': {
		'attribute': 'outputID',
		'search_field': ['function.output.data.uri', 'function.output.format.uri'],
		'exact': True
	},
	'outputDataFormat': {
		'attribute': 'outputDataFormat',
		'search_field': ['function.output.format.term.raw','function.output.format.term'],
		'exact': True
	},
	'outputDataFormatID': {
		'attribute': 'outputDataFormatID',
		'search_field': ['function.output.format.uri'],
		'exact': True
	},
	'outputDataType': {
		'attribute': 'outputDataType',
		'search_field': ['function.output.data.term.raw','function.output.data.term'],
		'exact': True
	},
	'outputDataTypeID': {
		'attribute': 'outputDataTypeID',
		'search_field': ['function.output.data.uri'],
		'exact': True
	},
	'homepage': {
		'attribute': 'homepage',
		'search_field': ['homepage'],
		'exact': False
	},
	'description': {
		'attribute': 'description',
		'search_field': ['description'],
		'exact': False
	},
	'version': {
		'attribute': 'version',
		'search_field': ['version'],
		'exact': False
	},
	'toolType': {
		'attribute': 'toolType',
		'search_field': ['toolType'],
		'exact': False
	},
	'collectionID': {
		'attribute': 'collectionID',
		'search_field': ['collectionID'],
		'exact': True
	},
	'maturity': {
		'attribute': 'maturity',
		'search_field': ['maturity'],
		'exact': False
	},
	'operatingSystem': {
		'attribute': 'operatingSystem',
		'search_field': ['operatingSystem'],
		'exact': True
	},
	'language': {
		'attribute': 'language',
		'search_field': ['language'],
		'exact': True
	},
	'cost': {
		'attribute': 'cost',
		'search_field': ['cost'],
		'exact': True
	},
	'license': {
		'attribute': 'license',
		'search_field': ['license'],
		'exact': True
	},
	'accessibility': {
		'attribute': 'accessibility',
		'search_field': ['accessibility'],
		'exact': True
	},
	'credit': {
		'attribute': 'credit',
		'search_field': ['credit.name.raw', 'credit.name', 'credit.note', 'credit.typeRole', 'credit.typeEntity', 'credit.orcidid', 'credit.url','credit.email'],
		'exact': True
	},
	'creditName': {
		'attribute': 'creditName',
		'search_field': ['credit.name.raw', 'credit.name'],
		'exact': True
	},
	'creditTypeRole': {
		'attribute': 'creditTypeRole',
		'search_field': ['credit.typeRole'],
		'exact': True
	},
	'creditTypeEntity': {
		'attribute': 'creditTypeEntity',
		'search_field': ['credit.typeEntity'],
		'exact': True
	},
	'creditOrcidID': {
		'attribute': 'creditOrcidID',
		'search_field': ['credit.orcidid'],
		'exact': True
	},
	'publication': {
		'attribute': 'publication',
		'search_field': ['publication.doi', 'publication.pmid', 'publication.pmcid','publication.type','publication.version'],
		'exact': True
	},
	'publicationID': {
		'attribute': 'publicationID',
		'search_field': ['publication.doi', 'publication.pmid', 'publication.pmcid'],
		'exact': True
	},
	'publicationType': {
		'attribute': 'publicationType',
		'search_field': ['publication.type'],
		'exact': True
	},
	'publicationVersion': {
		'attribute': 'publicationVersion',
		'search_field': ['publication.version'],
		'exact': True
	},
	'link': {
		'attribute': 'link',
		'search_field': ['link.url','link.type','link.note'],
		'exact': True
	},
	'linkType': {
		'attribute': 'linkType',
		'search_field': ['link.type'],
		'exact': True
	},
	# 'contact': {
	# 	'attribute': 'contact',
	# 	'search_field': ['contact.name.raw'],
	# 	'exact': True
	# },
	'documentation': {
		'attribute': 'documentation',
		'search_field': ['documentation.note','documentation.url','documentation.type'],
		'exact': True
	},
	'documentationType': {
		'attribute': 'documentationType',
		'search_field': ['documentation.type'],
		'exact': True
	},
	'download': {
		'attribute': 'download',
		'search_field': ['download.note','download.url','download.type','download.version'],
		'exact': True
	},
	'downloadType': {
		'attribute': 'downloadType',
		'search_field': ['download.type'],
		'exact': True
	},
	'downloadVersion': {
		'attribute': 'downloadVersion',
		'search_field': ['download.version'],
		'exact': True
	},
	'otherID': {
		'attribute': 'otherID',
		'search_field': ['otherID.value','otherID.type','otherID.version'],
		'exact': True
	},
	'otherIDType': {
		'attribute': 'otherIDType',
		'search_field': ['otherID.type'],
		'exact': True
	},
	'otherIDVersion': {
		'attribute': 'otherIDVersion',
		'search_field': ['otherID.version'],
		'exact': True
	},
	'owner': {
		'attribute': 'owner',
		'search_field': ['owner'],
		'exact': True
	}
}