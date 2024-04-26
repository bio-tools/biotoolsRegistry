# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestMirror(BaseTestObject):

	def test_mirror_correct_1(self):
		"""Sending one URL as 'mirror'
		Purpose:
			Basic test of successful sending of an allowed value for mirror
		Sent:
			Allowed value for mirror
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_correct_1'
		sent_resource['mirror'] = ['http://example.org']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_mirror_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_mirror_correct_1'
		expected_resource['mirror'] = ['http://example.org']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_mirror_correct_2(self):
		"""Sending sending two correct values as 'mirror'
		Purpose:
			Basic test of successful sending of two allowed values for mirror
		Sent:
			Two allowed values for mirror
		Expected outcome:
			Resource registered with two sent values
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_correct_2'
		sent_resource['mirror'] = ['http://example.org','http://example.com']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_mirror_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_mirror_correct_2'
		expected_resource['mirror'] = ['http://example.org','http://example.com']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_mirror_empty_none(self):
		"""Sending null/None as 'mirror'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_empty_none'
		sent_resource['mirror'] = None

		expected_response = {
			'mirror': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_mirror_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mirror_empty_zero_length(self):
		"""Sending empty array as 'mirror'
		Purpose:
			What happens when we send empty array
		Sent:
			[]
		Expected outcome:
			Error informing that this field cannot be empty
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_empty_zero_length'
		sent_resource['mirror'] = []

		expected_response = {
			'mirror': {
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
		
		response = self.client.get('/tool/test_mirror_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mirror_invalid(self):
		"""Sending incorrect value as 'mirror'
		Purpose:
			Sending incorrect value as mirror
		Sent:
			incorrect value for mirror
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_invalid'
		sent_resource['mirror'] = ['random string here']

		expected_response = {
			'mirror': [
				[
					'This is not a valid URL: random string here.'
				]
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_mirror_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)

	
	def test_mirror_string(self):
		"""Sending a string as 'mirror'
		Purpose:
			What happens when we send a string
		Sent:
			'random string here'
		Expected outcome:
			Error stating incorrect type
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_string'
		sent_resource['mirror'] = 'random string here'

		expected_response = {
			'mirror': {
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
		
		response = self.client.get('/tool/test_mirror_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mirror_array(self):
		"""Sending array as 'mirror'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_array'
		sent_resource['mirror'] = ['a','b','c',['d']]

		expected_response = {
			'mirror': [
				[
					'This is not a valid URL: a.'
				],
				[
					'This is not a valid URL: b.'
				],
				[
					'This is not a valid URL: c.'
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
		
		response = self.client.get('/tool/test_mirror_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mirror_dict(self):
		"""Sending dictionary as 'mirror'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_dict'
		sent_resource['mirror'] = {'a':'b','c':[1, 2, 3]}

		expected_response = {
			'mirror': {
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
		
		response = self.client.get('/tool/test_mirror_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mirror_number(self):
		"""Sending number as 'mirror'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_number'
		sent_resource['mirror'] = 1234567890

		expected_response = {
			'mirror': {
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
		
		response = self.client.get('/tool/test_mirror_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mirror_case_sensitive(self):
		"""Sending camel case url as 'mirror'
		Purpose:
			What happens when we send URL with camel case
		Sent:
			Camel case URL
		Expected outcome:
			Resource registered with lowercase URL string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_case_sensitive'
		sent_resource['mirror'] = ['HTTP://ExAmPlE.cOm']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_mirror_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_mirror_case_sensitive'
		expected_resource['mirror'] = ['HTTP://ExAmPlE.cOm']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_mirror_300_length(self):
		"""Sending 300 times character 'a' as 'mirror'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			300 times 'a'
		Expected outcome:
			Resource registered with 300 times 'a' as a mirror
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_300_length'
		sent_resource['mirror'] = ['http://' + 293*'a']

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_mirror_300_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_mirror_300_length'
		expected_resource['mirror'] = ['http://'+293*'a']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_mirror_301_length(self):
		"""Sending 301 times character 'a' as 'mirror'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			301 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_301_length'
		sent_resource['mirror'] = ['http://' + 294*'a']

		expected_response = {
			'mirror': [
				[
					'Ensure this field has no more than 300 characters.'
				]
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_mirror_301_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mirror_non_ascii(self):
		"""Sending string with non-ascii characters as 'mirror'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with non-ascii URL
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_non_ascii'
		sent_resource['mirror'] = ['http://ąęćżźń£ØΔ♥†.com']

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_mirror_non_ascii', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_mirror_non_ascii'
		expected_resource['mirror'] = ['http://ąęćżźń£ØΔ♥†.com']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_mirror_duplicate(self):
		"""Sending two identical strings as 'mirror'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical mirror strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mirror_duplicate'
		sent_resource['mirror'] = ['http://example.org', 'http://example.org']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_mirror_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_mirror_duplicate'
		expected_resource['mirror'] = ['http://example.org']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
