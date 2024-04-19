# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestDescription(BaseTestObject):

	def test_description_correct(self):
		"""Sending string as 'description'
		Purpose:
			Basic test of successful sending of a string as description
		Sent:
			description as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_description_correct'
		sent_resource['description'] = 'Just a description'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_description_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_description_correct'
		expected_resource['description'] = 'Just a description'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_description_empty_none(self):
		"""Sending null/None as 'description'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_description_empty_none'
		sent_resource['description'] = None

		
		expected_response = {
			'description': [
				'This field may not be null.'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_description_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_description_empty_zero_length(self):
		"""Sending string of zero length as 'description'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_description_empty_zero_length'
		sent_resource['description'] = ''

		
		expected_response = {
			'description': [
				'This field may not be blank.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_description_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_description_1000_length(self):
		"""Sending 1000 times character 'a' as 'description'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			1000 times 'a'
		Expected outcome:
			Resource registered with 1000 times 'a' as a description
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_description_1000_length'
		sent_resource['description'] = 1000*'a'

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_description_1000_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_description_1000_length'
		expected_resource['description'] = 1000*'a'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_description_1001_length(self):
		"""Sending 1001 times character 'a' as 'description'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			1001 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_description_1001_length'
		sent_resource['description'] = 1001*'a'

		expected_response = {
			'description': [
				'Ensure this field has no more than 1000 characters.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_description_1001_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_description_non_ascii(self):
		"""Sending string with non-ascii characters as 'description'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_description_non_ascii'
		sent_resource['description'] = 'ąęćżźń£ Ø Δ ♥ †'

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_description_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_description_non_ascii'
		expected_resource['description'] = 'ąęćżźń£ Ø Δ ♥ †'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_description_array(self):
		"""Sending array as 'description'
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
		sent_resource['id'] = 'test_description_array'
		sent_resource['description'] = ['a','b','c',['d']]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)	

		response = self.client.get('/tool/test_description_array', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_description_array'
		expected_resource['description'] = "[u'a', u'b', u'c', [u'd']]"

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_description_dict(self):
		"""Sending dictionary as 'description'
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
		sent_resource['id'] = 'test_description_dict'
		sent_resource['description'] = {'a':'b','c':[1,2,3]}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)	
		
		response = self.client.get('/tool/test_description_dict', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_description_dict'
		expected_resource['description'] = "{u'a': u'b', u'c': [1, 2, 3]}"

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_description_number(self):
		"""Sending number as 'description'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_description_number'
		sent_resource['description'] = 1234567890

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_description_number', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_description_number'
		expected_resource['description'] = '1234567890'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
