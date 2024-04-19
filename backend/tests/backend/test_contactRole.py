# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestContactRole(BaseTestObject):

	def test_contactRole_correct_1(self):
		"""Sending one string as 'contactRole'
		Purpose:
			Basic test of successful sending of a string as contactRole
		Sent:
			contactRole as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_correct_1'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['General']
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_correct_1'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['General'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_contactRole_correct_2(self):
		"""Sending one string as 'contactRole'
		Purpose:
			Basic test of successful sending of a string as contactRole
		Sent:
			contactRole as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_correct_2'
		sent_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Developer']
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_correct_2'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Developer'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_contactRole_correct_3(self):
		"""Sending one string as 'contactRole'
		Purpose:
			Basic test of successful sending of a string as contactRole
		Sent:
			contactRole as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_correct_3'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Technical']
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_correct_3'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Technical'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_contactRole_correct_4(self):
		"""Sending one string as 'contactRole'
		Purpose:
			Basic test of successful sending of a string as contactRole
		Sent:
			contactRole as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_correct_4'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Scientific']
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_correct_4', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_correct_4'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Scientific'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_contactRole_correct_5(self):
		"""Sending one string as 'contactRole'
		Purpose:
			Basic test of successful sending of a string as contactRole
		Sent:
			contactRole as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_correct_5'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Maintainer']
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_correct_5', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_correct_5'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Maintainer'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_contactRole_correct_6(self):
		"""Sending one string as 'contactRole'
		Purpose:
			Basic test of successful sending of a string as contactRole
		Sent:
			contactRole as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_correct_6'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Helpdesk']
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_correct_6', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_correct_6'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Helpdesk'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_contactRole_correct_3_diff(self):
		"""Sending set of strings as 'contactRole'
		Purpose:
			Basic test of successful sending of a string as contactRole
		Sent:
			contactRole as a string
		Expected outcome:
			Resource registered with the sent array of 2 strings
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_correct_3'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['General', 'Maintainer', 'Helpdesk']
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_correct_3'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['General', 'Maintainer', 'Helpdesk'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_contactRole_1_correct_1_wrong(self):
		"""Sending two strings as 'contactRole'
		Purpose:
			Basic test of successful sending of a string as contactRole
		Sent:
			contactRole as a string
		Expected outcome:
			Resource registered with the sent array of 2 strings
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_1_correct_1_wrong'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['Helpdesk', 'Maintainer', 'string here']
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactRole': [
						{}, 
						{}, 
						[
							'Invalid value: string here.'
						]
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
		
		response = self.client.get('/tool/test_contactRole_1_correct_1_wrong')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_empty_none(self):
		"""Sending null/None as 'contactRole'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_empty_none'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': None
			}
		]

		
		expected_response = {
			'contact': [
				{
					'contactRole': [
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
		
		response = self.client.get('/tool/test_contactRole_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_empty_zero_length(self):
		"""Sending string of zero length as 'contactRole'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_empty_zero_length'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ''
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactRole': {
						'general_errors': [
							'Expected a list of items but got type "unicode".'
						]
					}
				}
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_contactRole_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_non_ascii(self):
		"""Sending string with non-ascii characters as 'contactRole'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_non_ascii'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['ąęćżźń£ Ø Δ ♥ †']
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactRole': [
						[
							'Invalid value: ąęćżźń£ Ø Δ ♥ †.'
						]
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
		
		response = self.client.get('/tool/test_contactRole_non_ascii')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_array(self):
		"""Sending array as 'contactRole'
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
		sent_resource['id'] = 'test_contactRole_array'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': [['d']]
			}
		]

		expected_response = {
			'contact': [
				{
					'contactRole': [
						[
							'Wrong type found, expected unicode/string, got array/list.'
						]
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
		
		response = self.client.get('/tool/test_contactRole_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_dict(self):
		"""Sending dictionary as 'contactRole'
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
		sent_resource['id'] = 'test_contactRole_dict'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': {'a':'b','c':[1,2,3]}
			}
		]

		expected_response = {
			'contact': [
				{
					'contactRole': {
						'general_errors': [
							'Expected a list of items but got type "dict".'
						]
					}
				}
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_contactRole_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_number(self):
		"""Sending number as 'contactRole'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_number'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': 1234567890
			}
		]

		expected_response = {
			'contact': [
				{
					'contactRole': {
						'general_errors': [
							'Expected a list of items but got type "int".'
						]
					}
				}
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)
		
		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_contactRole_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_array_number(self):
		"""Sending array of numbers as 'contactRole'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of numbers
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_array_number'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': [1]
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactRole': [
						[
							'Wrong type found, expected unicode/string, got integer/number.'
						]
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
		
		response = self.client.get('/tool/test_contactRole_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_array_dict(self):
		"""Sending array of dictionaries as 'contactRole'
		Purpose:
			What happens when we send wrong type as the field (this case - array of dictionaries)
		Sent:
			Array of dictionaries
		Expected outcome:
			Registered resource with stringified value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_array_dict'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': [{'a':'b','c':5}]
			}
		]

		expected_response = {
			'contact': [
				{
					'contactRole': [
						[
							'Wrong type found, expected unicode/string, got dictionary/hash.'
						]
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
		
		response = self.client.get('/tool/test_contactRole_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactRole_case_sensitive(self):
		"""Sending correct value but with wrong case as 'contactRole'
		Purpose:
			What happens when we send correct value but with incorrect case (general instead of General)
		Sent:
			Value with correct string but lowercase (general instead of General)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_case_sensitive'
		sent_resource['contact'] = [ 
			{
				'contactURL': 'http://example.com',
				'contactRole': ['general']
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_case_sensitive'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['General'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_contactRole_duplicate(self):
		"""Sending two identical strings as 'contactRole'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical contactRole strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactRole_duplicate'
		sent_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': [
					'General',
					'General'
				]
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactRole_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactRole_duplicate'
		expected_resource['contact'] = [
			{
				'contactURL': 'http://example.com',
				'contactRole': ['General'],
				'contactEmail': None,
				'contactTel': None,
				'contactName': None
			}
		]
		
		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
