# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestCreditsAffiliation(BaseTestObject):

	def test_creditsAffiliation_correct_1(self):
		"""Sending one string as 'creditsAffiliation'
		Purpose:
			Basic test of successful sending of a string as creditsAffiliation
		Sent:
			creditsAffiliation as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_correct_1'
		sent_resource['credits'] = {
			'creditsAffiliation' : [
				'Just a creditsAffiliation'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_creditsAffiliation_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_creditsAffiliation_correct_1'
		expected_resource['credits'] = {
			'creditsAffiliation' : [
				'Just a creditsAffiliation'
			],
			'creditsDeveloper': [],
			'creditsContributor': [],
			'creditsInfrastructure': [],
			'creditsFunding': [],
			'creditsInstitution': []
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_creditsAffiliation_correct_2(self):
		"""Sending two strings as 'creditsAffiliation'
		Purpose:
			Basic test of successful sending of a string as creditsAffiliation
		Sent:
			creditsAffiliation as a string
		Expected outcome:
			Resource registered with the sent array of 2 strings
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_correct_2'
		sent_resource['credits'] = {
			'creditsAffiliation': [
				'Just a creditsAffiliation', 
				'another creditsAffiliation'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_creditsAffiliation_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_creditsAffiliation_correct_2'
		expected_resource['credits'] = {
			'creditsAffiliation' : [
				'Just a creditsAffiliation', 
				'another creditsAffiliation'
			],
			'creditsDeveloper': [],
			'creditsContributor': [],
			'creditsInfrastructure': [],
			'creditsFunding': [],
			'creditsInstitution': []
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_creditsAffiliation_empty_none(self):
		"""Sending null/None as 'creditsAffiliation'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_empty_none'
		sent_resource['credits'] = {
			'creditsAffiliation': None
		}

		expected_response = {
			'credits': {
				'creditsAffiliation': [
					'This field may not be null.'
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_creditsAffiliation_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_creditsAffiliation_empty_zero_length(self):
		"""Sending string of zero length as 'creditsAffiliation'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_empty_zero_length'
		sent_resource['credits'] = {
			'creditsAffiliation': ''
		}

		expected_response = {
			'credits': {
				'creditsAffiliation': {
					'general_errors': [
						'Expected a list of items but got type "unicode".'
					]
				}
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_creditsAffiliation_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_creditsAffiliation_300_length(self):
		"""Sending 300 times character 'a' as 'creditsAffiliation'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			300 times 'a'
		Expected outcome:
			Resource registered with 300 times 'a' as a creditsAffiliation
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_300_length'
		sent_resource['credits'] = {
			'creditsAffiliation': [
				300*'a'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_creditsAffiliation_300_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_creditsAffiliation_300_length'
		expected_resource['credits'] = {
			'creditsAffiliation' : [
				300*'a'
			],
			'creditsDeveloper': [],
			'creditsContributor': [],
			'creditsInfrastructure': [],
			'creditsFunding': [],
			'creditsInstitution': []
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_creditsAffiliation_301_length(self):
		"""Sending 301 times character 'a' as 'creditsAffiliation'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			301 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_301_length'
		sent_resource['credits'] = {
			'creditsAffiliation': [
				301*'a'
			]
		}

		expected_response = {
			'credits': {
				'creditsAffiliation': [
					[
						'Ensure this field has no more than 300 characters.'
					]
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_creditsAffiliation_301_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_creditsAffiliation_non_ascii(self):
		"""Sending string with non-ascii characters as 'creditsAffiliation'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_non_ascii'
		sent_resource['credits'] = {
			'creditsAffiliation': [
				'ąęćżźń£ Ø Δ ♥ †'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_creditsAffiliation_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_creditsAffiliation_non_ascii'
		expected_resource['credits'] = {
			'creditsAffiliation' : [
				'ąęćżźń£ Ø Δ ♥ †'
			],
			'creditsDeveloper': [],
			'creditsContributor': [],
			'creditsInfrastructure': [],
			'creditsFunding': [],
			'creditsInstitution': []
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_creditsAffiliation_array(self):
		"""Sending array as 'creditsAffiliation'
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
		sent_resource['id'] = 'test_creditsAffiliation_array'
		sent_resource['credits'] = {
			'creditsAffiliation': ['a','b','c',['d']]
		}

		expected_response = {
			'credits': {
				'creditsAffiliation': [
					{}, 
					{}, 
					{}, 
					[
						'Wrong type found, expected unicode/string, got array/list.'
					]
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_creditsAffiliation_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_creditsAffiliation_dict(self):
		"""Sending dictionary as 'creditsAffiliation'
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
		sent_resource['id'] = 'test_creditsAffiliation_dict'
		sent_resource['credits'] = {
			'creditsAffiliation': {'a':'b','c':[1,2,3]}
		}

		expected_response = {
			'credits': {
				'creditsAffiliation': {
					'general_errors': [
						'Expected a list of items but got type "dict".'
					]
				}
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_creditsAffiliation_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_creditsAffiliation_number(self):
		"""Sending number as 'creditsAffiliation'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_number'
		sent_resource['credits'] = {
			'creditsAffiliation': 1234567890
		}

		expected_response = {
			'credits': {
				'creditsAffiliation': {
					'general_errors': [
						'Expected a list of items but got type "int".'
					]
				}
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)
		
		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_creditsAffiliation_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_creditsAffiliation_array_number(self):
		"""Sending array of numbers as 'creditsAffiliation'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of numbers
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_array_number'
		sent_resource['credits'] = {
			'creditsAffiliation': [1]
		}
		
		expected_response = {
			'credits': {
				'creditsAffiliation': [
					[
						'Wrong type found, expected unicode/string, got integer/number.'
					]
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_creditsAffiliation_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_creditsAffiliation_array_dict(self):
		"""Sending array of dictionaries as 'creditsAffiliation'
		Purpose:
			What happens when we send wrong type as the field (this case - array of dictionaries)
		Sent:
			Array of dictionaries
		Expected outcome:
			Registered resource with stringified value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_array_dict'
		sent_resource['credits'] = {
			'creditsAffiliation': [{'a':'b','c':5}]
		}

		expected_response = {
			'credits': {
				'creditsAffiliation': [
					[
						'Wrong type found, expected unicode/string, got dictionary/hash.'
					]
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_creditsAffiliation_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_creditsAffiliation_duplicate(self):
		"""Sending two identical strings as 'creditsAffiliation'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical creditsAffiliation strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_creditsAffiliation_duplicate'
		sent_resource['credits'] = {
			'creditsAffiliation' : [
				'Just a creditsAffiliation',
				'Just a creditsAffiliation'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_creditsAffiliation_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_creditsAffiliation_duplicate'
		expected_resource['credits'] = {
			'creditsAffiliation' : [
				'Just a creditsAffiliation'
			],
			'creditsDeveloper': [],
			'creditsContributor': [],
			'creditsInfrastructure': [],
			'creditsFunding': [],
			'creditsInstitution': []
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
