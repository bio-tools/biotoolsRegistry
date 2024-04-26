from copy import deepcopy

# empty minimal data structure that passes the validation
input_base_struct = {
  "name": "Resource Name",
  "homepage": "http://example.com",
  "toolType": [
    "Command-line tool"
  ],
  "description": "Example description of the resource.",
  "topic": [
    {
      "term": "Topic"
    }
  ],
  "function": [
    {
      "operation": [
        {
          "term": "Operation"
        }
      ]
    }
  ],
  "contact": [
    {
      "email": "person@example.com"
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
    "biotoolsID": "Resource_Name",
    "biotoolsCURIE": "biotools:Resource_Name",
    "name": "Resource Name",
    "topic": [
        {
            "uri": "http://edamontology.org/topic_0003",
            "term": "Topic"
        }
    ],
    "function": [
        {
            "note": None,
            "cmd": None,
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
    "version": [],
    "homepage": "http://example.com",
    "description": "Example description of the resource.",
    "canonicalID": None,
    "accessibility": [],
    "additionDate": "2018-07-04T11:50:25Z",
    "lastUpdate": "2018-07-04T11:50:25Z",
    "availability": None,
    "downtime": None,
    "cost": None,
    "maturity": None,
    "credit": [],
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
            "metadata": None
        }
    ],
    "collectionID": [],
    "otherID": [],
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