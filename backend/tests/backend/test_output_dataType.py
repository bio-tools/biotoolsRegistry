from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestOutputDataType(BaseTestObject):
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
	
	def test_output_dataType_Pass_URI_only(self):
		"""Sending as 'dataType': correct URI
		Purpose:
			Sending correct URI
		Sent:
			Correct URI
		Expected outcome:
			Resource registered - URI resolves to a concept, term filled in
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_output_dataType_Pass_URI_only'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_2044'
						}
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_output_dataType_Pass_URI_only', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_output_dataType_Pass_URI_only'
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
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_2044',
							'term': 'Sequence'
						},
						'dataFormat':[],
						'dataHandle': None,
						'dataDescription': None
					}
				],
				'input': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_output_dataType_Pass_term_only(self):
		"""Sending as 'dataType': correct term
		Purpose:
			Sending correct term
		Sent:
			Correct term
		Expected outcome:
			Resource registered - term resolves to a concept, URI filled in
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_output_dataType_Pass_term_only'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'term': 'Sequence'
						}
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_output_dataType_Pass_term_only', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_output_dataType_Pass_term_only'
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
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_2044',
							'term': 'Sequence'
						},
						'dataFormat':[],
						'dataHandle': None,
						'dataDescription': None
					}
				],
				'input': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_output_dataType_Pass_URI_term(self):
		"""Sending as 'dataType': correct URI and term
		Purpose:
			Sending correct URI and term
		Sent:
			Correct URI and term
		Expected outcome:
			Resource registered - URI and term resolves to a concept
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_output_dataType_Pass_URI_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_2044',
							'term': 'Sequence'
						}
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_output_dataType_Pass_URI_term', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_output_dataType_Pass_URI_term'
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
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_2044',
							'term': 'Sequence'
						},
						'dataFormat':[],
						'dataHandle': None,
						'dataDescription': None
					}
				],
				'input': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_Obsolete_output_dataType_URI(self):
		"""Sending as 'dataType': obsolete URI
		Purpose:
			Sending obsolete URI to get an error
		Sent:
			Obsolete URI
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_output_dataType_URI'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_0005'
						}
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid URI: http://edamontology.org/data_0005.'
								]
							}
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
		
		response = self.client.get('/tool/test_Obsolete_output_dataType_URI')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Obsolete_output_dataType_term(self):
		"""Sending as 'dataType': obsolete term
		Purpose:
			Sending obsolete term to get an error
		Sent:
			Obsolete term
		Expected outcome:
			Error returned, term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_output_dataType_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'term': 'Resource type'
						}
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid term: Resource type.'
								]
							}
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
		
		response = self.client.get('/tool/test_Obsolete_output_dataType_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Obsolete_output_dataType_URI_term(self):
		"""Sending as 'dataType': obsolete URI and term
		Purpose:
			Sending obsolete URI and term to get an error
		Sent:
			Obsolete URI and term
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_output_dataType_URI_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_0005',
							'term': 'Resource type'
						}
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid URI: http://edamontology.org/data_0005.'
								]
							}
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
		
		response = self.client.get('/tool/test_Obsolete_output_dataType_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_output_dataType_URI(self):
		"""Sending as 'dataType': incorrect URI
		Purpose:
			Sending incorrect URI to get an error
		Sent:
			Obsolete URI
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_output_dataType_URI'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/invalid',
						}
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid URI: http://edamontology.org/invalid.'
								]
							}
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
		
		response = self.client.get('/tool/test_incorrect_output_dataType_URI')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_output_dataType_term(self):
		"""Sending as 'dataType': invalid term
		Purpose:
			Sending invalid term to get an error
		Sent:
			Obsolete term
		Expected outcome:
			Error returned, term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_output_dataType_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'term': 'Invalid dataType'
						}
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid term: Invalid dataType.'
								]
							}
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
		
		response = self.client.get('/tool/test_incorrect_output_dataType_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_output_dataType_URI_term(self):
		"""Sending as 'dataType': incorrect URI and term
		Purpose:
			Sending incorrect URI and term to get an error
		Sent:
			Obsolete URI and term
		Expected outcome:
			Error returned, URI and term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_output_dataType_URI_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/invalid',
							'term': 'Invalid dataType'
						}
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid URI: http://edamontology.org/invalid.'
								]
							}
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
		
		response = self.client.get('/tool/test_incorrect_output_dataType_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mismatch_correct_out_dataType_URI_term(self):
		"""Sending as 'dataType': mismatched URI and term
		Purpose:
			Sending correct URI with mismatched term
		Sent:
			Correct, but mismatched URI/term pair
		Expected outcome:
			Error returned, term does not match the URI
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mismatch_correct_out_dataType_URI_term'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_0006',
							'term': 'Ontology'
						}
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'The term does not match the URI: Ontology, http://edamontology.org/data_0006.'
								]
							}
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
		
		response = self.client.get('/tool/test_mismatch_correct_out_dataType_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)



	def test_out_dataType_string(self):
		"""Sending as 'dataType': string
		Purpose:
			What happens when we send wrong type as the field (this case - string)
		Sent:
			String as dataType
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dataType_string'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': 'just a string'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid data. Expected a dictionary, but got unicode.'
								]
							}
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
		
		response = self.client.get('/tool/test_out_dataType_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dataType_array(self):
		"""Sending dictionary as 'dataType'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dataType_array'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': ['a',1]
					}
				]
			}
		]
		
		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid data. Expected a dictionary, but got list.'
								]
							}
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
		
		response = self.client.get('/tool/test_out_dataType_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dataType_number(self):
		"""Sending number as 'dataType'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dataType_number'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': 1234567890
					}
				]
			}
		]
		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataType': {
								'general_errors': [
									'Invalid data. Expected a dictionary, but got int.'
								]
							}
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
		
		response = self.client.get('/tool/test_out_dataType_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dataType_extra_fields(self):
		"""Sending array of dicts with extra fields as 'dataType'
		Purpose:
			What happens when we send wrong type as the field (this case - add some fields to the object)
		Sent:
			Array of arrays of mixed types
		Expected outcome:
			Resource is registered, extra fields are ignored.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dataType_extra_fields'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_2044',
							'some': 'field'
						}
					}
				]
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_out_dataType_extra_fields', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_out_dataType_extra_fields'
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
				'output': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_2044',
							'term': 'Sequence'
						},
						'dataFormat':[],
						'dataHandle': None,
						'dataDescription': None
					}
				],
				'input': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
