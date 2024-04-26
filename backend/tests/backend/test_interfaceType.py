# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestInterfaceType(BaseTestObject):

	def test_interfaceType_correct_1(self):
		"""Sending one of the allowed values as 'interfaceType'
		Purpose:
			Basic test of successful sending of an allowed value for interfaceType
		Sent:
			Allowed value for interfaceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_correct_1'
		sent_resource['interface'] = [
			{
				'interfaceType': 'Command line'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceType_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceType_correct_1'
		expected_resource['interface'] = [
			{
				'interfaceType': 'Command line',
				'interfaceDocs': None,
				'interfaceSpecURL': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_interfaceType_correct_2(self):
		"""Sending one of the allowed values as 'interfaceType'
		Purpose:
			Basic test of successful sending of an allowed value for interfaceType
		Sent:
			Allowed value for interfaceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_correct_2'
		sent_resource['interface'] = [
			{
				'interfaceType': 'Web UI'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceType_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceType_correct_2'
		expected_resource['interface'] = [
			{
				'interfaceType': 'Web UI',
				'interfaceDocs': None,
				'interfaceSpecURL': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	def test_interfaceType_correct_3(self):
		"""Sending one of the allowed values as 'interfaceType'
		Purpose:
			Basic test of successful sending of an allowed value for interfaceType
		Sent:
			Allowed value for interfaceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_correct_3'
		sent_resource['interface'] = [
			{
				'interfaceType': 'Desktop GUI'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceType_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceType_correct_3'
		expected_resource['interface'] = [
			{
				'interfaceType': 'Desktop GUI',
				'interfaceDocs': None,
				'interfaceSpecURL': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_interfaceType_correct_4(self):
		"""Sending one of the allowed values as 'interfaceType'
		Purpose:
			Basic test of successful sending of an allowed value for interfaceType
		Sent:
			Allowed value for interfaceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_correct_4'
		sent_resource['interface'] = [
			{
				'interfaceType': 'SOAP WS'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceType_correct_4', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceType_correct_4'
		expected_resource['interface'] = [
			{
				'interfaceType':'SOAP WS',
				'interfaceDocs': None,
				'interfaceSpecURL': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_interfaceType_correct_5(self):
		"""Sending one of the allowed values as 'interfaceType'
		Purpose:
			Basic test of successful sending of an allowed value for interfaceType
		Sent:
			Allowed value for interfaceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_correct_5'
		sent_resource['interface'] = [
			{
				'interfaceType': 'HTTP WS'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceType_correct_5', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceType_correct_5'
		expected_resource['interface'] = [
			{
				'interfaceType': 'HTTP WS',
				'interfaceDocs': None,
				'interfaceSpecURL': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_interfaceType_correct_6(self):
		"""Sending one of the allowed values as 'interfaceType'
		Purpose:
			Basic test of successful sending of an allowed value for interfaceType
		Sent:
			Allowed value for interfaceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_correct_6'
		sent_resource['interface'] = [
			{
				'interfaceType': 'API'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceType_correct_6', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceType_correct_6'
		expected_resource['interface'] = [
			{
				'interfaceType': 'API',
				'interfaceDocs': None,
				'interfaceSpecURL': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_interfaceType_correct_7(self):
		"""Sending one of the allowed values as 'interfaceType'
		Purpose:
			Basic test of successful sending of an allowed value for interfaceType
		Sent:
			Allowed value for interfaceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_correct_7'
		sent_resource['interface'] = [
			{
				'interfaceType': 'QL'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceType_correct_7', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceType_correct_7'
		expected_resource['interface'] = [
			{
				'interfaceType': 'QL',
				'interfaceDocs': None,
				'interfaceSpecURL': None,
				'interfaceSpecFormat': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_interfaceType_empty_none(self):
		"""Sending null/None as 'interfaceType'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_empty_none'
		sent_resource['interface'] = [
			{
				'interfaceType': None
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceType': [
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
		
		response = self.client.get('/tool/test_interfaceType_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceType_empty_zero_length(self):
		"""Sending empty array as 'interfaceType'
		Purpose:
			What happens when we send empty array
		Sent:
			[]
		Expected outcome:
			Error informing that this field cannot be empty
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_empty_zero_length'
		sent_resource['interface'] = [
			{
				'interfaceType': []
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceType': [
						'Invalid value: [].'
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
		
		response = self.client.get('/tool/test_interfaceType_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceType_array(self):
		"""Sending incorrect value as 'interfaceType'
		Purpose:
			Sending incorrect value as interfaceType
		Sent:
			incorrect value for interfaceType
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_array'
		sent_resource['interface'] = [
			{
				'interfaceType': [
					'random string here'
				]
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceType': [
						"Invalid value: [u'random string here']."
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
		
		response = self.client.get('/tool/test_interfaceType_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)

	
	def test_interfaceType_string(self):
		"""Sending a string as 'interfaceType'
		Purpose:
			What happens when we send a string
		Sent:
			'random string here'
		Expected outcome:
			Error stating incorrect type
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_string'
		sent_resource['interface'] = [
			{
				'interfaceType': 'random string here'
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceType': [
						'Invalid value: random string here.'
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
		
		response = self.client.get('/tool/test_interfaceType_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceType_array(self):
		"""Sending array as 'interfaceType'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_array'
		sent_resource['interface'] = [
			{
				'interfaceType': [
					['d']
				]
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceType': [
						"Invalid value: [[u'd']]."
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
		
		response = self.client.get('/tool/test_interfaceType_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceType_dict(self):
		"""Sending dictionary as 'interfaceType'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_dict'
		sent_resource['interface'] = [
			{
				'interfaceType': {'a':'b','c':[1, 2, 3]}
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceType': [
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
		
		response = self.client.get('/tool/test_interfaceType_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceType_number(self):
		"""Sending number as 'interfaceType'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_number'
		sent_resource['interface'] = [
			{
				'interfaceType': 1234567890
			}
		]

		expected_response = {
			'interface': [
				{
					'interfaceType': [
						'Invalid value: 1234567890.'
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
		
		response = self.client.get('/tool/test_interfaceType_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_interfaceType_case_sensitive(self):
		"""Sending correct value but with wrong case as 'interfaceType'
		Purpose:
			What happens when we send correct value but with incorrect case (command line instead of Command line)
		Sent:
			Value with correct string but lowercase (command line instead of Command line)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_interfaceType_case_sensitive'
		sent_resource['interface'] = [
			{
				'interfaceType': 'command line'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_interfaceType_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_interfaceType_case_sensitive'
		expected_resource['interface'] = [
			{
				'interfaceType': 'Command line',
				'interfaceDocs': None,
				'interfaceSpecFormat': None,
				'interfaceSpecURL': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
