from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestOutputDataFormat(BaseTestObject):
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
	
	def test_output_dataFormat_Pass_URI_only(self):
		"""Sending as 'dataFormat': correct URI
		Purpose:
			Sending correct URI
		Sent:
			Correct URI
		Expected outcome:
			Resource registered - URI resolves to a concept, term filled in
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_output_dataFormat_Pass_URI_only'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1929'
							}
						]
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_output_dataFormat_Pass_URI_only', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_output_dataFormat_Pass_URI_only'
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
						'dataFormat':[
							{
								'uri': 'http://edamontology.org/format_1929',
								'term': 'FASTA'
							}
						],
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

		self.assertItemsEqual(expected_resource, received_resource)


	def test_output_dataFormat_Pass_term_only(self):
		"""Sending as 'dataFormat': correct term
		Purpose:
			Sending correct term
		Sent:
			Correct term
		Expected outcome:
			Resource registered - term resolves to a concept, URI filled in
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_output_dataFormat_Pass_term_only'
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
						},
						'dataFormat': [
							{
								'term': 'FASTA'
							}
						]
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_output_dataFormat_Pass_term_only', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_output_dataFormat_Pass_term_only'
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
						'dataFormat':[
							{
								'uri': 'http://edamontology.org/format_1929',
								'term': 'FASTA'
							}
						],
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

		self.assertItemsEqual(expected_resource, received_resource)


	def test_output_dataFormat_Pass_URI_term(self):
		"""Sending as 'dataFormat': correct URI and term
		Purpose:
			Sending correct URI and term
		Sent:
			Correct URI and term
		Expected outcome:
			Resource registered - URI and term resolves to a concept
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_output_dataFormat_Pass_URI_term'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1929',
								'term': 'FASTA'
							}
						]
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_output_dataFormat_Pass_URI_term', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_output_dataFormat_Pass_URI_term'
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
						'dataFormat':[
							{
								'uri': 'http://edamontology.org/format_1929',
								'term': 'FASTA'
							}
						],
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

		self.assertItemsEqual(expected_resource, received_resource)


	def test_Obsolete_output_dataFormat_URI(self):
		"""Sending as 'dataFormat': obsolete URI
		Purpose:
			Sending obsolete URI to get an error
		Sent:
			Obsolete URI
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_output_dataFormat_URI'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1228'
							}
						]
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
								{
									'general_errors': [
										'Invalid URI: http://edamontology.org/format_1228.'
									]
								}
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
		
		response = self.client.get('/tool/test_Obsolete_output_dataFormat_URI')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Obsolete_output_dataFormat_term(self):
		"""Sending as 'dataFormat': obsolete term
		Purpose:
			Sending obsolete term to get an error
		Sent:
			Obsolete term
		Expected outcome:
			Error returned, term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_output_dataFormat_term'
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
						},
						'dataFormat': [
							{
								'term': 'UniGene entry format'
							}
						]
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
								{
									'general_errors': [
										'Invalid term: UniGene entry format.'
									]
								}
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
		
		response = self.client.get('/tool/test_Obsolete_output_dataFormat_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Obsolete_output_dataFormat_URI_term(self):
		"""Sending as 'dataFormat': obsolete URI and term
		Purpose:
			Sending obsolete URI and term to get an error
		Sent:
			Obsolete URI and term
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_output_dataFormat_URI_term'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1228',
								'term': 'UniGene entry format'
							}
						]
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
								{
									'general_errors': [
										'Invalid URI: http://edamontology.org/format_1228.'
									]
								}
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
		
		response = self.client.get('/tool/test_Obsolete_output_dataFormat_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_output_dataFormat_URI(self):
		"""Sending as 'dataFormat': incorrect URI
		Purpose:
			Sending incorrect URI to get an error
		Sent:
			Obsolete URI
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_output_dataFormat_URI'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/invalid'
							}
						]
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
								{
									'general_errors': [
										'Invalid URI: http://edamontology.org/invalid.'
									]
								}
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
		
		response = self.client.get('/tool/test_incorrect_output_dataFormat_URI')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_output_dataFormat_term(self):
		"""Sending as 'dataFormat': invalid term
		Purpose:
			Sending invalid term to get an error
		Sent:
			Obsolete term
		Expected outcome:
			Error returned, term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_output_dataFormat_term'
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
						},
						'dataFormat': [
							{
								'term': 'Invalid dataFormat'
							}
						]
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
								{
									'general_errors': [
										'Invalid term: Invalid dataFormat.'
									]
								}
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
		
		response = self.client.get('/tool/test_incorrect_output_dataFormat_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_output_dataFormat_URI_term(self):
		"""Sending as 'dataFormat': incorrect URI and term
		Purpose:
			Sending incorrect URI and term to get an error
		Sent:
			Obsolete URI and term
		Expected outcome:
			Error returned, URI and term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_output_dataFormat_URI_term'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/invalid',
								'term': 'Invalid dataFormat'
							}
						]
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
								{
									'general_errors': [
										'Invalid URI: http://edamontology.org/invalid.'
									]
								}
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
		
		response = self.client.get('/tool/test_incorrect_output_dataFormat_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mismatch_correct_out_dataFormat_URI_term(self):
		"""Sending as 'dataFormat': mismatched URI and term
		Purpose:
			Sending correct URI with mismatched term
		Sent:
			Correct, but mismatched URI/term pair
		Expected outcome:
			Error returned, term does not match the URI
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mismatch_correct_out_dataFormat_URI_term'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1218',
								'term': 'pure protein'
							}
						]
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [ 
								{
									'general_errors': [
										'The term does not match the URI: pure protein, http://edamontology.org/format_1218.'
									]
								}
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
		
		response = self.client.get('/tool/test_mismatch_correct_out_dataFormat_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_dataFormat_Pass_2_dataFormats(self):
		"""Sending as 'dataFormat': 2 objects
		Purpose:
			Sending 2 dataFormat objects to test if saving multiple dataFormats works
		Sent:
			2 correct URI/term pairs
		Expected outcome:
			Resource registered with 2 dataFormats
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_dataFormat_Pass_2_dataFormats'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1218',
								'term': 'unambiguous pure protein'
							},
							{
								'uri': 'http://edamontology.org/format_1219',
								'term': 'pure protein'
							}
						]
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_dataFormat_Pass_2_dataFormats', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_dataFormat_Pass_2_dataFormats'
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
						'dataFormat':[
							{
								'uri': 'http://edamontology.org/format_1218',
								'term': 'unambiguous pure protein'
							},
							{
								'uri': 'http://edamontology.org/format_1219',
								'term': 'pure protein'
							}

						],
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

		self.assertItemsEqual(expected_resource, received_resource)


	def test_dataFormat_2_dFormats_incorrect(self):
		"""Sending as 'dataFormat': 2 objects, one has incorrect URI
		Purpose:
			Sending 2 dataFormats with 1 being incorrect to test if catching error works for multiple objects
		Sent:
			Array of 2 dataFormats, 1 incorrect
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_dataFormat_2_dFormats_incorrect'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1218',
								'term': 'unambiguous pure protein'
							},
							{
								'uri': 'http://edamontology.org/invalid',
								'term': 'Invalid dataFormat'
							}
						]
					}
				]
			}
		]
		
		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
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
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_dataFormat_2_dFormats_incorrect')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dFormat_string(self):
		"""Sending as 'dataFormat': string
		Purpose:
			What happens when we send wrong type as the field (this case - string)
		Sent:
			String as dataFormat
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dFormat_string'
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
						},
						'dataFormat': 'just a string'
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': {
								'general_errors': [
									'Expected a list of items but got type "unicode".'
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
		
		response = self.client.get('/tool/test_out_dFormat_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dFormat_dict(self):
		"""Sending dictionary as 'dataFormat'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dFormat_dict'
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
						},
						'dataFormat': {'a':'b','c':[1,2,3]}
					}
				]
			}
		]
		
		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': {
								'general_errors': [
									'Expected a list of items but got type "dict".'
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
		
		response = self.client.get('/tool/test_out_dFormat_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dFormat_number(self):
		"""Sending number as 'dataFormat'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dFormat_number'
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
						},
						'dataFormat': 1234567890
					}
				]
			}
		]
		
		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': {
								'general_errors': [
									'Expected a list of items but got type "int".'
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
		
		response = self.client.get('/tool/test_out_dFormat_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dFormat_array_number(self):
		"""Sending array of numbers as 'dataFormat'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of numbers
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dFormat_array_number'
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
						},
						'dataFormat': [1]
					}
				]
			}
		]
		
		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
								{
									'general_errors': [
										'Invalid data. Expected a dictionary, but got int.'
									]
								}
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
		
		response = self.client.get('/tool/test_out_dFormat_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dFormat_array_array(self):
		"""Sending array of arrays as 'dataFormat'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of arrays of mixed types
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dFormat_array_array'
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
						},
						'dataFormat': [[2,3],'7']
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
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
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_out_dFormat_array_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dFormat_empty_array(self):
		"""Sending an empty arrays as 'dataFormat'
		Purpose:
			What happens when we send wrong type as the field (this case - empty array)
		Sent:
			Empty array
		Expected outcome:
			Error informing about empty array
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dFormat_empty_array'
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
						},
						'dataFormat': []
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': {
								'general_errors': [
									'This list may not be empty.'
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
		
		response = self.client.get('/tool/test_out_dFormat_empty_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dFormat_none(self):
		"""Sending a null/None as 'dataFormat'
		Purpose:
			What happens when we send wrong type as the field (this case - null/None)
		Sent:
			null/None
		Expected outcome:
			Error informing about the null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dFormat_none'
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
						},
						'dataFormat': None
					}
				]
			}
		]

		expected_response = {
			'function': [
				{
					'output': [
						{
							'dataFormat': [
								'This field may not be null.'
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
		
		response = self.client.get('/tool/test_out_dFormat_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_out_dFormat_extra_fields(self):
		"""Sending array of dicts with extra fields as 'dataFormat'
		Purpose:
			What happens when we send wrong type as the field (this case - add some fields to the object)
		Sent:
			Array of arrays of mixed types
		Expected outcome:
			Resource is registered, extra fields are ignored.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dFormat_extra_fields'
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
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1929',
								'some': 'field'
							}
						]
					}
				]
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_out_dFormat_extra_fields', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_out_dFormat_extra_fields'
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
						'dataFormat':[
							{
								'uri': 'http://edamontology.org/format_1929',
								'term': 'FASTA'
							}
						],
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

		self.assertItemsEqual(expected_resource, received_resource)


	def test_out_dataFormat_duplicate(self):
		"""Sending two identical strings as 'out_dataFormat'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical inp_dataFormat strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_out_dataFormat_duplicate'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'input': [
					{
						'dataType': {
							'uri': 'http://edamontology.org/data_2044',
							'term': 'Sequence'
						},
						'dataFormat': [
							{
								'uri': 'http://edamontology.org/format_1929'
							},
							{
								'uri': 'http://edamontology.org/format_1929'
							}
						]
					}
				]
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_out_dataFormat_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_out_dataFormat_duplicate'
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
						'dataFormat':[
							{
								'uri': 'http://edamontology.org/format_1929',
								'term': 'FASTA'
							}
						],
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

		self.assertItemsEqual(expected_resource, received_resource)
