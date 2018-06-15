search_struct = {
	'id': {
		'attribute': 'id',
		'search_field': ['id'],
		'exact': True
	},
	'name': {
		'attribute': 'name',
		'search_field': ['name.raw'],
		'exact': True
	},
	'topic': {
		'attribute': 'topic',
		'search_field': ['topic.term.raw'],
		'exact': True
	},
	'function': {
		'attribute': 'function',
		'search_field': ['function.operation.term.raw'],
		'exact': True
	},
	'operation': {
		'attribute': 'operation',
		'search_field': ['function.operation.term.raw'],
		'exact': True
	},
	'input': {
		'attribute': 'input',
		'search_field': ['function.input.data.term.raw', 'function.input.format.term.raw'],
		'exact': True
	},
	'inputDataFormat': {
		'attribute': 'inputDataFormat',
		'search_field': ['function.input.format.term.raw'],
		'exact': True
	},
	'inputDataType': {
		'attribute': 'inputDataType',
		'search_field': ['function.input.data.term.raw'],
		'exact': True
	},
	'output': {
		'attribute': 'output',
		'search_field': ['function.output.format.term.raw', 'function.output.data.term.raw'],
		'exact': True
	},
	'outputDataFormat': {
		'attribute': 'outputDataFormat',
		'search_field': ['function.output.format.term.raw'],
		'exact': True
	},
	'outputDataType': {
		'attribute': 'outputDataType',
		'search_field': ['function.output.data.term.raw'],
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
	'credit': {
		'attribute': 'credit',
		'search_field': ['credit.name.raw', 'credit.comment'],
		'exact': True
	},
	'contact': {
		'attribute': 'contact',
		'search_field': ['contact.name.raw'],
		'exact': True
	},
	'documentation': {
		'attribute': 'documentation',
		'search_field': ['documentation.comment'],
		'exact': True
	},
	'owner': {
		'attribute': 'owner',
		'search_field': ['owner'],
		'exact': True
	}
}