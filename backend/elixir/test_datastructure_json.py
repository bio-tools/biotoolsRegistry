from copy import deepcopy

# empty minimal data structure that passes the validation
input_base_struct = {
	'name': 'Resource Name',
	'homepage': 'http://example.com',
	'toolType': [
		'Command-line tool'
	],
	'description': 'Example description of the resource.',
	'topic': [
		{
			'term': 'Topic'
		}
	],
	'function': [
		{
			'operation': [
				{
					'term': 'Operation'
				}
			]
		}
	],
	'contact': [
		{
			'email': 'person@example.com'
		}
	],
  "publication": [
    {
      "pmid": "21959131"
    }
  ]
}

# expected response for the minimal input structure
output_base_struct = {
  "additionDate": None,
  "lastUpdate": None,
  "id": "Resource_Name",
  "name": "Resource Name",
  "topic": [
    {
      "uri": "http://edamontology.org/topic_0003",
      "term": "Topic"
    }
  ],
  "function": [
    {
      "comment": None,
      "operation": [
        {
          "uri": "http://edamontology.org/operation_0004",
          "term": "Operation"
        }
      ],
      "input": [],
      "output": []
    }
  ],
  "version": None,
  "homepage": "http://example.com",
  "description": "Example description of the resource.",
  "canonicalID": None,
  "accessibility": [],
  "availability": None,
  "downtime": None,
  "cost": None,
  "maturity": None,
  "credit": [],
  "elixirInfo": None,
  "link": [],
  "download": [],
  "license": None,
  "operatingSystem": [],
  "toolType": [
    "Command-line tool"
  ],
  "language": [],
  "documentation": [],
  "publication": [
    {
      "pmcid": None,
      "pmid": "21959131",
      "doi": None,
      "type": None,
      "version": None,
      "metadata": {
        "title": "SignalP 4.0: Discriminating signal peptides from transmembrane regions",
        "abstract": "",
        "date": "2011-10-01T00:00:00Z",
        "citationCount": 0,
        "authors": [
          {
            "name": "Petersen T.N."
          },
          {
            "name": "Brunak S."
          },
          {
            "name": "Von Heijne G."
          },
          {
            "name": "Nielsen H."
          }
        ],
        "journal": "Nature Methods"
      }
    }
  ],
  "collectionID": [],
  "contact": [
    {
      "name": None,
      "url": None,
      "email": "person@example.com",
      "tel": None
    }
  ],
  "owner": "admin",
  "editPermission": {
    "type": "private",
    "authors": []
  },
  "validated": 0,
  "homepage_status": 0
}

def emptyInputTool():
	return deepcopy(input_base_struct)

def emptyOutputTool():
	return deepcopy(output_base_struct)