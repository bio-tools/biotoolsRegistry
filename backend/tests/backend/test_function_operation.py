from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestFunctionName(BaseTestObject):
	"""General structure for the EDAM tests:
	============================	======	======
									URI 	Term
	============================	======	======
	present, correct				x
											x
									x		x
	present, obsolete 				x
											x
									x		x
	present, incorrect 				x
											x
									x		x
	present, mismatch 				x		x
	2 present, correct 				x		x
	2 present, 1 incorrect 			x		x
	============================	======	======
	It doesn't matter if the term is OK or not (e.g. obsolete) if it doesn't match a correct URI.
	"""
	
	def test_operation_Pass_URI_only(self):
		"""Sending as 'operation': correct URI
		Purpose:
			Sending correct URI
		Sent:
			Correct URI
		Expected outcome:
			Resource registered - URI resolves to a concept, term filled in
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_Pass_URI_only'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004'
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_operation_Pass_URI_only', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_operation_Pass_URI_only'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionDescription': None,
				'functionHandle': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)

		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_operation_Pass_term_only(self):
		"""Sending as 'operation': correct term
		Purpose:
			Sending correct term
		Sent:
			Correct term
		Expected outcome:
			Resource registered - term resolves to a concept, URI filled in
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_Pass_term_only'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'term': 'Operation'
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_operation_Pass_term_only', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_operation_Pass_term_only'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionDescription': None,
				'functionHandle': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_operation_Pass_URI_term(self):
		"""Sending as 'operation': correct URI and term
		Purpose:
			Sending correct URI and term
		Sent:
			Correct URI and term
		Expected outcome:
			Resource registered - URI and term resolves to a concept
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_Pass_URI_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_operation_Pass_URI_term', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_operation_Pass_URI_term'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionDescription': None,
				'functionHandle': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_Obsolete_operation_URI(self):
		"""Sending as 'operation': obsolete URI
		Purpose:
			Sending obsolete URI to get an error
		Sent:
			Obsolete URI
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_operation_URI'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0229'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'Invalid URI: http://edamontology.org/operation_0229.'
							]
						}
					]
				}	
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_Obsolete_operation_URI')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Obsolete_operation_term(self):
		"""Sending as 'operation': obsolete term
		Purpose:
			Sending obsolete term to get an error
		Sent:
			Obsolete term
		Expected outcome:
			Error returned, term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_operation_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'term': 'Annotation retrieval (sequence)'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'Invalid term: Annotation retrieval (sequence).'
							]
						}
					]
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_Obsolete_operation_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Obsolete_operation_URI_term(self):
		"""Sending as 'operation': obsolete URI and term
		Purpose:
			Sending obsolete URI and term to get an error
		Sent:
			Obsolete URI and term
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_operation_URI_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0229',
						'term': 'Annotation retrieval (sequence)'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'Invalid URI: http://edamontology.org/operation_0229.'
							]
						}
					]
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_Obsolete_operation_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_operation_URI(self):
		"""Sending as 'operation': incorrect URI
		Purpose:
			Sending incorrect URI to get an error
		Sent:
			Obsolete URI
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_operation_URI'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_invalid'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'Invalid URI: http://edamontology.org/operation_invalid.'
							]
						}
					]
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_incorrect_operation_URI')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_operation_term(self):
		"""Sending as 'operation': invalid term
		Purpose:
			Sending invalid term to get an error
		Sent:
			Obsolete term
		Expected outcome:
			Error returned, term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_operation_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'term': 'Incorrect operation'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'Invalid term: Incorrect operation.'
							]
						}
					]
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_incorrect_operation_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_operation_URI_term(self):
		"""Sending as 'operation': incorrect URI and term
		Purpose:
			Sending incorrect URI and term to get an error
		Sent:
			Obsolete URI and term
		Expected outcome:
			Error returned, URI and term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_operation_URI_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_invalid',
						'term': 'Incorrect operation'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'Invalid URI: http://edamontology.org/operation_invalid.'
							]
						}
					]
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_incorrect_operation_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mismatch_correct_fName_URI_term(self):
		"""Sending as 'operation': mismatched URI and term
		Purpose:
			Sending correct URI with mismatched term
		Sent:
			Correct, but mismatched URI/term pair
		Expected outcome:
			Error returned, term does not match the URI
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mismatch_correct_fName_URI_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Indexing'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'The term does not match the URI: Indexing, http://edamontology.org/operation_0004.'
							]
						}
					]
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_mismatch_correct_fName_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_operation_Pass_2_operations(self):
		"""Sending as 'operation': 2 objects
		Purpose:
			Sending 2 operation objects to test if saving multiple operations works
		Sent:
			2 correct URI/term pairs
		Expected outcome:
			Resource registered with 2 operations
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_Pass_2_operations'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					},
					{
						'uri': 'http://edamontology.org/operation_0227',
						'term': 'Indexing'
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_operation_Pass_2_operations', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_operation_Pass_2_operations'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					},
					{
						'uri': 'http://edamontology.org/operation_0227',
						'term': 'Indexing'
					}
				],
				'functionDescription': None,
				'functionHandle': None,
				'input': [],
				'output': []
			}
		]
		
		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_operation_2_fNames_incorrect(self):
		"""Sending as 'operation': 2 objects, one has incorrect URI
		Purpose:
			Sending 2 operations with 1 being incorrect to test if catching error works for multiple objects
		Sent:
			Array of 2 operations, 1 incorrect
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_2_fNames_incorrect'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					},
					{
						'uri': 'http://edamontology.org/invalid',
						'term': 'Unicellular eukaryotes'
					}
				]
			}
		]
		
		expected_response = {
			'function': [
				{
					'operation': [
						{},
						{
							'general_errors': [
								'Invalid URI: http://edamontology.org/invalid.'
							]
						}
					]
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_operation_2_fNames_incorrect')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_operation_string(self):
		"""Sending as 'operation': string
		Purpose:
			What happens when we send wrong type as the field (this case - string)
		Sent:
			String as operation
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_string'
		sent_resource['function'] = [
			{
				'operation': 'just a string'
			}
		]

		expected_response = {
			'function': [
				{
					'operation': {
						'general_errors': [
							'Expected a list of items but got type "unicode".'
						]
					}
				}
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_operation_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_operation_dict(self):
		"""Sending dictionary as 'operation'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_dict'
		sent_resource['function'] = [
			{
				'operation': {'a':'b','c':[1,2,3]}
			}
		]

		expected_response = {
			'function': [
				{
					'operation': {
						'general_errors': [
							'Expected a list of items but got type "dict".'
						]
					}
				}
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_operation_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_operation_number(self):
		"""Sending number as 'operation'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_number'
		sent_resource['function'] = [
			{
				'operation': 1234567890
			}
		]
		
		expected_response = {
			'function': [
				{
					'operation': {
						'general_errors': [
							'Expected a list of items but got type "int".'
						]
					}
				}
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_operation_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_operation_array_number(self):
		"""Sending array of numbers as 'operation'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of numbers
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_array_number'
		sent_resource['function'] = [
			{
				'operation': [1]
			}
		]
		
		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'Invalid data. Expected a dictionary, but got int.'
							]
						}
					]
				}
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_operation_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_operation_array_array(self):
		"""Sending array of arrays as 'operation'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of arrays of mixed types
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_array_array'
		sent_resource['function'] = [
			{
				'operation': [[2,3],'7']
			}
		]

		expected_response = {
			'function': [
				{
					'operation': [
						{
							'general_errors': [
								'Invalid data. Expected a dictionary, but got list.'
							]
						},
						{
							'general_errors': [
								'Invalid data. Expected a dictionary, but got unicode.'
							]
						}
					]
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_operation_array_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_operation_extra_fields(self):
		"""Sending array of dicts with extra fields as 'operation'
		Purpose:
			What happens when we send wrong type as the field (this case - add some fields to the object)
		Sent:
			Array of arrays of mixed types
		Expected outcome:
			Resource is registered, extra fields are ignored.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_extra_fields'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'some': 'field'
					}
				]
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_operation_extra_fields', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_operation_extra_fields'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionDescription': None,
				'functionHandle': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_operation_empty_zero_length(self):
		"""Sending empty array as 'operation'
		Purpose:
			What happens when we send empty array
		Sent:
			[]
		Expected outcome:
			Error informing that this field cannot be empty
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_empty_zero_length'
		sent_resource['function'] = [
			{
				'operation': []
			}
		]

		expected_response = {
			'function': [
				{
					'operation': {
						'general_errors': [
							'This list may not be empty.'
						]
					}
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_operation_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_operation_duplicate(self):
		"""Sending two identical strings as 'operation'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical operation strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_operation_duplicate'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004'
					},
					{
						'uri': 'http://edamontology.org/operation_0004'
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_operation_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_operation_duplicate'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionDescription': None,
				'functionHandle': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
