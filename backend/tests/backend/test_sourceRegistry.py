# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestSourceRegistry(BaseTestObject):

	def test_sourceRegistry_correct(self):
		"""Sending string as 'sourceRegistry'
		Purpose:
			Basic test of successful sending of a string as sourceRegistry
		Sent:
			sourceRegistry as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_sourceRegistry_correct'
		sent_resource['sourceRegistry'] = 'Just a sourceRegistry'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_sourceRegistry_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_sourceRegistry_correct'
		expected_resource['sourceRegistry'] = 'Just a sourceRegistry'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_sourceRegistry_empty_none(self):
		"""Sending null/None as 'sourceRegistry'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Resource registered with None as sourceRegistry
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_sourceRegistry_empty_none'
		sent_resource['sourceRegistry'] = None
		
		expected_response = {
			'sourceRegistry': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_sourceRegistry_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_sourceRegistry_empty_zero_length(self):
		"""Sending string of zero length as 'sourceRegistry'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Resource registered with zero-length string 'sourceRegistry'
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_sourceRegistry_zero_length'
		sent_resource['sourceRegistry'] = ''
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_sourceRegistry_zero_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_sourceRegistry_zero_length'
		expected_resource['sourceRegistry'] = ''

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_sourceRegistry_50_length(self):
		"""Sending 50 times character 'a' as 'sourceRegistry'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			50 times 'a'
		Expected outcome:
			Resource registered with 50 times 'a' as a sourceRegistry
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_sourceRegistry_50_length'
		sent_resource['sourceRegistry'] = 50*'a'

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_sourceRegistry_50_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_sourceRegistry_50_length'
		expected_resource['sourceRegistry'] = 50*'a'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_sourceRegistry_51_length(self):
		"""Sending 51 times character 'a' as 'sourceRegistry'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			51 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_sourceRegistry_51_length'
		sent_resource['sourceRegistry'] = 51*'a'
		
		expected_response = {
			'sourceRegistry': [
				'Ensure this field has no more than 50 characters.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_sourceRegistry_51_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_sourceRegistry_non_ascii(self):
		"""Sending string with non-ascii characters as 'sourceRegistry'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_sourceRegistry_non_ascii'
		sent_resource['sourceRegistry'] = 'ąęćżźń£ Ø Δ ♥ †'

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_sourceRegistry_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_sourceRegistry_non_ascii'
		expected_resource['sourceRegistry'] = 'ąęćżźń£ Ø Δ ♥ †'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_sourceRegistry_array(self):
		"""Sending array as 'sourceRegistry'
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
		sent_resource['id'] = 'test_sourceRegistry_array'
		sent_resource['sourceRegistry'] = ['a','b','c',['d']]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		
		response = self.client.get('/tool/test_sourceRegistry_array', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_sourceRegistry_array'
		expected_resource['sourceRegistry'] = "[u'a', u'b', u'c', [u'd']]"

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_sourceRegistry_dict(self):
		"""Sending dictionary as 'sourceRegistry'
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
		sent_resource['id'] = 'test_sourceRegistry_dict'
		sent_resource['sourceRegistry'] = {'a':'b','c':[1,2,3]}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_sourceRegistry_dict', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_sourceRegistry_dict'
		expected_resource['sourceRegistry'] = "{u'a': u'b', u'c': [1, 2, 3]}"

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_sourceRegistry_number(self):
		"""Sending number as 'sourceRegistry'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_sourceRegistry_number'
		sent_resource['sourceRegistry'] = 1234567890

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		
		response = self.client.get('/tool/test_sourceRegistry_number', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_sourceRegistry_number'
		expected_resource['sourceRegistry'] = '1234567890'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
