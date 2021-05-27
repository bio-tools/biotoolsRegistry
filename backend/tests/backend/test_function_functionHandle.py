# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestFunctionHandle(BaseTestObject):

	def test_functionHandle_correct(self):
		"""Sending string as 'functionHandle'
		Purpose:
			Basic test of successful sending of a string as description
		Sent:
			description as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_correct'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': 'Just a functionHandle'
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_functionHandle_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_functionHandle_correct'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': 'Just a functionHandle',
				'functionDescription': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_functionHandle_empty_none(self):
		"""Sending null/None as 'functionHandle'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_empty_none'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': None
			}
		]
		
		expected_response = {
			'function': [
				{
					'functionHandle': [
						'This field may not be null.'
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
		
		response = self.client.get('/tool/test_functionHandle_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_functionHandle_empty_zero_length(self):
		"""Sending string of zero length as 'functionHandle'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_empty_zero_length'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': ''
			}
		]

		expected_response = {
			'function': [
				{
					'functionHandle': [
						'This field may not be blank.'
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
		
		response = self.client.get('/tool/test_functionHandle_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_functionHandle_300_length(self):
		"""Sending 300 times character 'a' as 'functionHandle'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			300 times 'a'
		Expected outcome:
			Resource registered with 300 times 'a' as a description
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_300_length'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': 300*'a'
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_functionHandle_300_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_functionHandle_300_length'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': 300*'a',
				'functionDescription': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_functionHandle_301_length(self):
		"""Sending 301 times character 'a' as 'functionHandle'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			301 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_301_length'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': 301*'a'
			}
		]

		expected_response = {
			'function': [
				{
					'functionHandle': [
						'Ensure this field has no more than 300 characters.'
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
		
		response = self.client.get('/tool/test_functionHandle_301_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_functionHandle_non_ascii(self):
		"""Sending string with non-ascii characters as 'functionHandle'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_non_ascii'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': 'ąęćżźń£ Ø Δ ♥ †'
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_functionHandle_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_functionHandle_non_ascii'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': 'ąęćżźń£ Ø Δ ♥ †',
				'functionDescription': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_functionHandle_array(self):
		"""Sending array as 'functionHandle'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Resource registered with stringified array.
		Note:
			Spaces are added to the stringified value.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_array'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': ['a','b','c',['d']]
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_functionHandle_array', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_functionHandle_array'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': "[u'a', u'b', u'c', [u'd']]",
				'functionDescription': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_functionHandle_dict(self):
		"""Sending dictionary as 'functionHandle'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Resource registered with stringified dictionary.
		Note:
			Spaces are added to the stringified value.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_dict'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': {'a':'b','c':[1,2,3]}
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_functionHandle_dict', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_functionHandle_dict'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': "{u'a': u'b', u'c': [1, 2, 3]}",
				'functionDescription': None,
				'input': [],
				'output': []
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_functionHandle_number(self):
		"""Sending number as 'functionHandle'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_functionHandle_number'
		sent_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': 1234567890
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_functionHandle_number', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_functionHandle_number'
		expected_resource['function'] = [
			{
				'operation': [
					{
						'uri': 'http://edamontology.org/operation_0004',
						'term': 'Operation'
					}
				],
				'functionHandle': '1234567890',
				'functionDescription': None,
				'input': [],
				'output': []
			}
		]
		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
