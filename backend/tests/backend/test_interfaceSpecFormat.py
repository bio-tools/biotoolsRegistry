# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestInterfaceSpecFormat(BaseTestObject):

	def test_interfaceSpecFormat_correct_1(self):
		"""Sending a correctly formatted string as 'interfaceSpecFormat'
		Purpose:
			Basic test of successful sending of a string as interfaceSpecFormat
		Sent:
			interfaceSpecFormat as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_correct_1'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 'WSDL'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceSpecFormat_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceSpecFormat_correct_1'
		expected_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 'WSDL',
				'interfaceDocs': None,
				'interfaceSpecURL': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_interfaceSpecFormat_correct_2(self):
		"""Sending a correctly formatted string as 'interfaceSpecFormat'
		Purpose:
			Basic test of successful sending of a string as interfaceSpecFormat
		Sent:
			interfaceSpecFormat as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_correct_2'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 'WSDL2'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceSpecFormat_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceSpecFormat_correct_2'
		expected_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 'WSDL2',
				'interfaceDocs': None,
				'interfaceSpecURL': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_interfaceSpecFormat_empty_none(self):
		"""Sending null/None as 'interfaceSpecFormat'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_empty_none'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': None
			}
		]
		
		expected_response = {
			'interface': [
				{
					'interfaceSpecFormat': [
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
		
		response = self.client.get('/tool/test_interfaceSpecFormat_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecFormat_empty_zero_length(self):
		"""Sending string of zero length as 'interfaceSpecFormat'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_empty_zero_length'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': ''
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecFormat': [
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
		
		response = self.client.get('/tool/test_interfaceSpecFormat_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecFormat_non_ascii(self):
		"""Sending string with non-ascii characters as 'interfaceSpecFormat'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with non-ascii URL
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_non_ascii'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 'http://ąęćżźń£ØΔ♥†.com'
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecFormat': [
						'Invalid value: http://ąęćżźń£ØΔ♥†.com.'
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
		
		response = self.client.get('/tool/test_interfaceSpecFormat_non_ascii')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecFormat_incorrect(self):
		"""Sending an incorrect string as 'interfaceSpecFormat'
		Purpose:
			What happens when we send a non-link as interfaceSpecFormat
		Sent:
			Non-link string
		Expected outcome:
			Error informing about malformed URL
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_incorrect'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 'ssh://example.org'
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecFormat': [
						'Invalid value: ssh://example.org.'
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
		
		response = self.client.get('/tool/test_interfaceSpecFormat_incorrect')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecFormat_array(self):
		"""Sending as 'interfaceSpecFormat': array
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_array'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': ['a','b','c',['d']]
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecFormat': [
						"Invalid value: [u'a', u'b', u'c', [u'd']]."
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
		
		response = self.client.get('/tool/test_interfaceSpecFormat_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecFormat_dict(self):
		"""Sending as 'interfaceSpecFormat': dictionary
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_dict'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': {'a':'b','c':[1,2,3]}
			}
		]
		
		expected_response = {
			'interface': [
				{
					'interfaceSpecFormat': [
						"Invalid value: {u'a': u'b', u'c': [1, 2, 3]}."
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
		
		response = self.client.get('/tool/test_interfaceSpecFormat_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecFormat_number(self):
		"""Sending as 'interfaceSpecFormat': number
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_number'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 1234567890
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceSpecFormat': [
						"Invalid value: 1234567890."
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
		
		response = self.client.get('/tool/test_interfaceSpecFormat_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceSpecFormat_case_sensitive(self):
		"""Sending correct value but with wrong case as 'interfaceSpecFormat'
		Purpose:
			What happens when we send correct value but with incorrect case (wsdl instead of WSDL)
		Sent:
			Value with correct string but lowercase (wsdl instead of WSDL)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceSpecFormat_case_sensitive'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 'wsdl'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceSpecFormat_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceSpecFormat_case_sensitive'
		expected_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceSpecFormat': 'WSDL',
				'interfaceDocs': None,
				'interfaceSpecURL': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
