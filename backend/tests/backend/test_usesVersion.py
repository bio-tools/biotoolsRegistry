# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestUsesVersion(BaseTestObject):

	def test_usesVersion_correct(self):
		"""Sending string as 'usesVersion'
		Purpose:
			Basic test of successful sending of a string as usesVersion
		Sent:
			usesVersion as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesVersion_correct'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': 'just a version'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesVersion_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesVersion_correct'
		expected_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': 'just a version',
				'usesHomepage': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesVersion_empty_none(self):
		"""Sending null/None as 'usesVersion'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Resource registered with None as usesVersion
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesVersion_empty_none'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': None
			}
		]

		expected_response = {
			'uses': [
				{
					'usesVersion': [
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
		
		response = self.client.get('/tool/test_usesVersion_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_usesVersion_empty_zero_length(self):
		"""Sending string of zero length as 'usesVersion'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Resource registered with zero-length string 'usesVersion'
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesVersion_zero_length'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': ''
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesVersion_zero_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesVersion_zero_length'
		expected_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesHomepage': None,
				'usesVersion': ''
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesVersion_50_length(self):
		"""Sending 50 times character 'a' as 'usesVersion'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			50 times 'a'
		Expected outcome:
			Resource registered with 50 times 'a' as a usesVersion
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesVersion_50_length'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': 50*'a'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesVersion_50_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesVersion_50_length'
		expected_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': 50*'a',
				'usesHomepage': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesVersion_51_length(self):
		"""Sending 51 times character 'a' as 'usesVersion'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			51 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""	
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesVersion_51_length'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': 51*'a'
			}
		]

		expected_response = {
			'uses': [
				{
					'usesVersion': [
						'Ensure this field has no more than 50 characters.'
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

		response = self.client.get('/tool/test_usesVersion_51_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_usesVersion_non_ascii(self):
		"""Sending string with non-ascii characters as 'usesVersion'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesVersion_non_ascii'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': 'ąęćżźń£ Ø Δ ♥ †'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesVersion_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesVersion_non_ascii'
		expected_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': 'ąęćżźń£ Ø Δ ♥ †',
				'usesHomepage': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesVersion_array(self):
		"""Sending array as 'usesVersion'
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
		sent_resource['id'] = 'test_usesVersion_array'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': ['a','b','c',['d']]
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesVersion_array', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesVersion_array'
		expected_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': "[u'a', u'b', u'c', [u'd']]",
				'usesHomepage': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesVersion_dict(self):
		"""Sending dictionary as 'usesVersion'
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
		sent_resource['id'] = 'test_usesVersion_dict'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': {'a':'b','c':[1,2,3]}
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesVersion_dict', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesVersion_dict'
		expected_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': "{u'a': u'b', u'c': [1, 2, 3]}",
				'usesHomepage': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_usesVersion_number(self):
		"""Sending number as 'usesVersion'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_usesVersion_number'
		sent_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': 1234567890
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_usesVersion_number', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_usesVersion_number'
		expected_resource['uses'] = [
			{
				'usesName': 'just a usesName',
				'usesVersion': '1234567890',
				'usesHomepage': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
