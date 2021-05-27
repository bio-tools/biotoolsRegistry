# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestVersion(BaseTestObject):

	def test_version_correct(self):
		"""Sending string as 'version'
		Purpose:
			Basic test of successful sending of a string as version
		Sent:
			Version as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_version_correct'
		sent_resource['version'] = 'Just a version'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_version_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_version_correct'
		expected_resource['version'] = 'Just a version'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_version_empty_none(self):
		"""Sending null/None as 'version'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Resource registered with None as version
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_version_empty_none'
		sent_resource['version'] = None
		
		expected_response = {
			'version': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_version_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_version_empty_zero_length(self):
		"""Sending string of zero length as 'version'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Resource registered with zero-length string 'version'
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_version_zero_length'
		sent_resource['version'] = ''
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_version_zero_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_version_zero_length'
		expected_resource['version'] = ''

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_version_50_length(self):
		"""Sending 50 times character 'a' as 'version'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			50 times 'a'
		Expected outcome:
			Resource registered with 50 times 'a' as a version
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_version_50_length'
		sent_resource['version'] = 50*'a'

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_version_50_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_version_50_length'
		expected_resource['version'] = 50*'a'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_version_51_length(self):
		"""Sending 51 times character 'a' as 'version'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			51 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""	
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_version_51_length'
		sent_resource['version'] = 51*'a'

		expected_response = {
			'version': [
				'Ensure this field has no more than 50 characters.'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}

		response = self.client.get('/tool/test_version_51_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_version_non_ascii(self):
		"""Sending string with non-ascii characters as 'version'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_version_non_ascii'
		sent_resource['version'] = 'ąęćżźń£ Ø Δ ♥ †'

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_version_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_version_non_ascii'
		expected_resource['version'] = 'ąęćżźń£ Ø Δ ♥ †'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_version_array(self):
		"""Sending array as 'version'
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
		sent_resource['id'] = 'test_version_array'
		sent_resource['version'] = ['a','b','c',['d']]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_version_array', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_version_array'
		expected_resource['version'] = "[u'a', u'b', u'c', [u'd']]"

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_version_dict(self):
		"""Sending dictionary as 'version'
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
		sent_resource['id'] = 'test_version_dict'
		sent_resource['version'] = {'a':'b','c':[1,2,3]}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_version_dict', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_version_dict'
		expected_resource['version'] = "{u'a': u'b', u'c': [1, 2, 3]}"

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_version_number(self):
		"""Sending number as 'version'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_version_number'
		sent_resource['version'] = 1234567890

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_version_number', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_version_number'
		expected_resource['version'] = '1234567890'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
