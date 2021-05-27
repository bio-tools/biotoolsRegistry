# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestUsesName(BaseTestObject):

	def test_usesName_correct(self):
		"""Sending string as 'usesName'
		Purpose:
			Basic test of successful sending of a string as usesName
		Sent:
			usesName as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesName_correct'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesName_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesName_correct'
		expected_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesHomepage': None,
				'usesVersion': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesName_empty_none(self):
		"""Sending null/None as 'usesName'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Resource registered with None as usesName
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesName_empty_none'
		sent_resource['uses'] = [
			{
				'usesName': None
			}
		]
		
		expected_response = {
			'uses': [
				{
					'usesName': [
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
		
		response = self.client.get('/tool/test_usesName_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_usesName_empty_zero_length(self):
		"""Sending string of zero length as 'usesName'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Resource registered with zero-length string 'usesName'
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesName_zero_length'
		sent_resource['uses'] = [
			{
				'usesName': ''
			}
		]
		
		expected_response = {
			'uses': [
				{
					'usesName': [
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

		response = self.client.get('/tool/test_usesName_zero_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_usesName_50_length(self):
		"""Sending 50 times character 'a' as 'usesName'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			50 times 'a'
		Expected outcome:
			Resource registered with 50 times 'a' as a usesName
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesName_50_length'
		sent_resource['uses'] = [
			{
				'usesName': 300*'a'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesName_50_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesName_50_length'
		expected_resource['uses'] = [
			{
				'usesName': 300*'a',
				'usesHomepage': None,
				'usesVersion': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesName_301_length(self):
		"""Sending 301 times character 'a' as 'usesName'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			51 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""	
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesName_301_length'
		sent_resource['uses'] = [
			{
				'usesName': 301*'a'
			}
		]

		expected_response = {
			'uses': [
				{
					'usesName': [
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

		response = self.client.get('/tool/test_usesName_301_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_usesName_non_ascii(self):
		"""Sending string with non-ascii characters as 'usesName'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesName_non_ascii'
		sent_resource['uses'] = [
			{
				'usesName': 'ąęćżźń£ Ø Δ ♥ †'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesName_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesName_non_ascii'
		expected_resource['uses'] = [
			{
				'usesName': 'ąęćżźń£ Ø Δ ♥ †',
				'usesHomepage': None,
				'usesVersion': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesName_array(self):
		"""Sending array as 'usesName'
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
		sent_resource['id'] = 'test_usesName_array'
		sent_resource['uses'] = [
			{
				'usesName': ['a','b','c',['d']]
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesName_array', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesName_array'
		expected_resource['uses'] = [
			{
				'usesName': "[u'a', u'b', u'c', [u'd']]",
				'usesHomepage': None,
				'usesVersion': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesName_dict(self):
		"""Sending dictionary as 'usesName'
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
		sent_resource['id'] = 'test_usesName_dict'
		sent_resource['uses'] = [
			{
				'usesName': {'a':'b','c':[1,2,3]}
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesName_dict', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesName_dict'
		expected_resource['uses'] = [
			{
				'usesName': "{u'a': u'b', u'c': [1, 2, 3]}",
				'usesHomepage': None,
				'usesVersion': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesName_number(self):
		"""Sending number as 'usesName'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesName_number'
		sent_resource['uses'] = [
			{
				'usesName': 1234567890
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesName_number', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesName_number'
		expected_resource['uses'] = [
			{
				'usesName': '1234567890',
				'usesHomepage': None,
				'usesVersion': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
