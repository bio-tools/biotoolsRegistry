# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestInterfaceSpecURL(BaseTestObject):

	def test_interfaceSpecURL_correct(self):
		"""Sending a correctly formatted string as 'interfaceSpecURL'
		Purpose:
			Basic test of successful sending of a string as interfaceSpecURL
		Sent:
			interfaceDocs as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_correct'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'http://example.org'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceSpecURL_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceSpecURL_correct'
		expected_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'http://example.org',
				'interfaceDocs': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_interfaceSpecURL_empty_none(self):
		"""Sending null/None as 'interfaceSpecURL'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_empty_none'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': None
			}
		]
		
		expected_response = {
			'interface': [
				{
					'interfaceSpecURL': [
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
		
		response = self.client.get('/tool/test_interfaceSpecURL_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecURL_empty_zero_length(self):
		"""Sending string of zero length as 'interfaceSpecURL'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_empty_zero_length'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': ''
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecURL': [
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
		
		response = self.client.get('/tool/test_interfaceSpecURL_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecURL_300_length(self):
		"""Sending 300 times character 'a' as 'interfaceSpecURL'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			300 times 'a'
		Expected outcome:
			Resource registered with 300 times 'a' as a interfaceDocs
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_300_length'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'http://' + 293*'a'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceSpecURL_300_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceSpecURL_300_length'
		expected_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'http://' + 293*'a',
				'interfaceDocs': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_interfaceSpecURL_301_length(self):
		"""Sending 301 times character 'a' as 'interfaceSpecURL'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			301 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_301_length'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'http://' + 294*'a'
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecURL': [
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
		
		response = self.client.get('/tool/test_interfaceSpecURL_301_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecURL_non_ascii(self):
		"""Sending string with non-ascii characters as 'interfaceSpecURL'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with non-ascii URL
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_non_ascii'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'http://ąęćżźń£ØΔ♥†.com'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceSpecURL_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceSpecURL_non_ascii'
		expected_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'http://ąęćżźń£ØΔ♥†.com',
				'interfaceDocs': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_interfaceSpecURL_incorrect(self):
		"""Sending an incorrect string as 'interfaceSpecURL'
		Purpose:
			What happens when we send a non-link as interfaceSpecURL
		Sent:
			Non-link string
		Expected outcome:
			Error informing about malformed URL
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_incorrect'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'ssh://example.org'
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecURL': [
						'This is not a valid URL: ssh://example.org.'
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
		
		response = self.client.get('/tool/test_interfaceSpecURL_incorrect')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecURL_array(self):
		"""Sending as 'interfaceSpecURL': array
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_array'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': ['a','b','c',['d']]
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecURL': [
						"This is not a valid URL: [u'a', u'b', u'c', [u'd']]."
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
		
		response = self.client.get('/tool/test_interfaceSpecURL_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecURL_dict(self):
		"""Sending as 'interfaceSpecURL': dictionary
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_dict'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': {'a':'b','c':[1,2,3]}
			}
		]
		
		expected_response = {
			'interface': [
				{
					'interfaceSpecURL': [
						"This is not a valid URL: {u'a': u'b', u'c': [1, 2, 3]}."
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
		
		response = self.client.get('/tool/test_interfaceSpecURL_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecURL_number(self):
		"""Sending as 'interfaceSpecURL': number
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_number'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 1234567890
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecURL': [
						"This is not a valid URL: 1234567890."
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
		
		response = self.client.get('/tool/test_interfaceSpecURL_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecURL_case_sensitive(self):
		"""Sending camel case url as 'interfaceSpecURL'
		Purpose:
			What happens when we send URL with camel case
		Sent:
			Camel case URL
		Expected outcome:
			Resource registered with lowercase URL string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecURL_case_sensitive'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'HTTP://ExAmPlE.cOm'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceSpecURL_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceSpecURL_case_sensitive'
		expected_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecURL': 'HTTP://ExAmPlE.cOm',
				'interfaceDocs': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
