# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestContactName(BaseTestObject):

	def test_contactName_correct(self):
		"""Sending a correctly formatted string as 'contactName'
		Purpose:
			Basic test of successful sending of a string as contactName
		Sent:
			contactName as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_correct'
		sent_resource['contact'] = [
			{
				'contactName': 'just a contactName',
				'contactURL': 'http://example.com'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactName_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactName_correct'
		expected_resource['contact'] = [
			{
				'contactName': 'just a contactName',
				'contactURL': 'http://example.com',
				'contactEmail': None,
				'contactTel': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_contactName_empty_none(self):
		"""Sending null/None as 'contactName'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_empty_none'
		sent_resource['contact'] = [
			{
				'contactName': None,
				'contactURL': 'http://example.com'
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactName': [
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
		
		response = self.client.get('/tool/test_contactName_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactName_empty_zero_length(self):
		"""Sending string of zero length as 'contactName'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_empty_zero_length'
		sent_resource['contact'] = [
			{
				'contactName': '',
				'contactURL': 'http://example.com'
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactName': [
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
		
		response = self.client.get('/tool/test_contactName_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactName_300_length(self):
		"""Sending 300 times character 'a' as 'contactName'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			300 times 'a'
		Expected outcome:
			Resource registered with 300 times 'a' as a contactName
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_300_length'
		sent_resource['contact'] = [
			{
				'contactName': 300*'a',
				'contactURL': 'http://example.com'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactName_300_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactName_300_length'
		expected_resource['contact'] = [
			{
				'contactName': 300*'a',
				'contactURL': 'http://example.com',
				'contactEmail': None,
				'contactTel': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_contactName_301_length(self):
		"""Sending 301 times character 'a' as 'contactName'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			301 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_301_length'
		sent_resource['contact'] = [
			{
				'contactName': 301*'a',
				'contactURL': 'http://example.com'
			}
		]

		expected_response = {
			'contact': [
				{
					'contactName': [
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
		
		response = self.client.get('/tool/test_contactName_301_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactName_non_ascii(self):
		"""Sending string with non-ascii characters as 'contactName'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Error informing about invalid email address.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_non_ascii'
		sent_resource['contact'] = [
			{
				'contactName': 'ąęćżźń£ØΔ♥†',
				'contactURL': 'http://example.com'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactName_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactName_non_ascii'
		expected_resource['contact'] = [
			{
				'contactName': 'ąęćżźń£ØΔ♥†',
				'contactURL': 'http://example.com',
				'contactEmail': None,
				'contactTel': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_contactName_array(self):
		"""Sending as 'contactName': array
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Resource registered with stringified contactName
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_array'
		sent_resource['contact'] = [
			{
				'contactName': ['a','b','c',['d']],
				'contactURL': 'http://example.com'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactName_array', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactName_array'
		expected_resource['contact'] = [
			{
				'contactName': "[u'a', u'b', u'c', [u'd']]",
				'contactURL': 'http://example.com',
				'contactEmail': None,
				'contactTel': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_contactName_dict(self):
		"""Sending as 'contactName': dictionary
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Resource registered with stringified value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_dict'
		sent_resource['contact'] = [
			{
				'contactName': {'a':'b','c':[1,2,3]},
				'contactURL': 'http://example.com'
			}
		]
		

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactName_dict', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactName_dict'
		expected_resource['contact'] = [
			{
				'contactName': "{u'a': u'b', u'c': [1, 2, 3]}",
				'contactURL': 'http://example.com',
				'contactEmail': None,
				'contactTel': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_contactName_number(self):
		"""Sending as 'contactName': number
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactName_number'
		sent_resource['contact'] = [
			{
				'contactName': 1234567890,
				'contactURL': 'http://example.com'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactName_number', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactName_number'
		expected_resource['contact'] = [
			{
				'contactName': '1234567890',
				'contactURL': 'http://example.com',
				'contactEmail': None,
				'contactTel': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
