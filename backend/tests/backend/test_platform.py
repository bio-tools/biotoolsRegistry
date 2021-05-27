# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestPlatform(BaseTestObject):

	def test_platform_correct_1(self):
		"""Sending one of the allowed values as 'platform'
		Purpose:
			Basic test of successful sending of an allowed value for platform
		Sent:
			Allowed value for platform
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_correct_1'
		sent_resource['platform'] = ['Mac']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_platform_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_platform_correct_1'
		expected_resource['platform'] = ['Mac']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_platform_correct_2(self):
		"""Sending one of the allowed values as 'platform'
		Purpose:
			Basic test of successful sending of an allowed value for platform
		Sent:
			Allowed value for platform
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_correct_2'
		sent_resource['platform'] = ['Linux']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_platform_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_platform_correct_2'
		expected_resource['platform'] = ['Linux']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_platform_correct_3(self):
		"""Sending one of the allowed values as 'platform'
		Purpose:
			Basic test of successful sending of an allowed value for platform
		Sent:
			Allowed value for platform
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_correct_3'
		sent_resource['platform'] = ['Windows']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_platform_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_platform_correct_3'
		expected_resource['platform'] = ['Windows']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_platform_empty_none(self):
		"""Sending null/None as 'platform'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_empty_none'
		sent_resource['platform'] = None

		expected_response = {
			'platform': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_platform_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_platform_empty_zero_length(self):
		"""Sending empty array as 'platform'
		Purpose:
			What happens when we send empty array
		Sent:
			[]
		Expected outcome:
			Error informing that this field cannot be empty
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_empty_zero_length'
		sent_resource['platform'] = []

		expected_response = {
			'platform': {
				'general_errors': [
					'This list may not be empty.'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_platform_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_platform_invalid(self):
		"""Sending incorrect value as 'platform'
		Purpose:
			Sending incorrect value as platform
		Sent:
			incorrect value for platform
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_invalid'
		sent_resource['platform'] = ['random string here']

		expected_response = {
			'platform': [
				[
					'Invalid value: random string here.'
				]
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_platform_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)

	
	def test_platform_string(self):
		"""Sending a string as 'platform'
		Purpose:
			What happens when we send a string
		Sent:
			'random string here'
		Expected outcome:
			Error stating incorrect type
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_string'
		sent_resource['platform'] = 'random string here'

		expected_response = {
			'platform': {
				'general_errors': [
					'Expected a list of items but got type "unicode".'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_platform_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_platform_array(self):
		"""Sending array as 'platform'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_array'
		sent_resource['platform'] = ['a','b','c',['d']]

		expected_response = {
			'platform': [
				[
					'Invalid value: a.'
				],
				[
					'Invalid value: b.'
				],
				[
					'Invalid value: c.'
				],
				[
					'Wrong type found, expected unicode/string, got array/list.'
				]
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_platform_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_platform_dict(self):
		"""Sending dictionary as 'platform'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_dict'
		sent_resource['platform'] = {'a':'b','c':[1, 2, 3]}

		expected_response = {
			'platform': {
				'general_errors': [
					'Expected a list of items but got type "dict".'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_platform_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_platform_number(self):
		"""Sending number as 'platform'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_number'
		sent_resource['platform'] = 1234567890

		expected_response = {
			'platform': {
				'general_errors': [
					'Expected a list of items but got type "int".'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_platform_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_platform_case_sensitive(self):
		"""Sending correct value but with wrong case as 'platform'
		Purpose:
			What happens when we send correct value but with incorrect case (mac instead of Mac)
		Sent:
			Value with correct string but lowercase (mac instead of Mac)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_case_sensitive'
		sent_resource['platform'] = ['mac']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_platform_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_platform_case_sensitive'
		expected_resource['platform'] = ['Mac']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_platform_duplicate(self):
		"""Sending two identical strings as 'platform'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical platform strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_platform_duplicate'
		sent_resource['platform'] = ['Mac', 'Mac', 'mac']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_platform_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_platform_duplicate'
		expected_resource['platform'] = ['Mac']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
