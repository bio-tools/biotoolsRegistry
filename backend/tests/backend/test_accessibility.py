# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestAccessibility(BaseTestObject):

	def test_accessibility_correct_1(self):
		"""Sending one of allowed values as 'accessibility'
		Purpose:
			Basic test of successful sending of an allowed value for accessibility
		Sent:
			Allowed value for accessibility
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_correct_1'
		sent_resource['accessibility'] = 'Public'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_accessibility_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_accessibility_correct_1'
		expected_resource['accessibility'] = 'Public'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_accessibility_correct_2(self):
		"""Sending one of allowed values as 'accessibility'
		Purpose:
			Basic test of successful sending of an allowed value for accessibility
		Sent:
			Allowed value for accessibility
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_correct_2'
		sent_resource['accessibility'] = 'Private'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_accessibility_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_accessibility_correct_2'
		expected_resource['accessibility'] = 'Private'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_accessibility_empty_none(self):
		"""Sending null/None as 'accessibility'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_empty_none'
		sent_resource['accessibility'] = None

		expected_response = {
			'accessibility': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_accessibility_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_accessibility_empty_zero_length(self):
		"""Sending as 'accessibility': string of zero length
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Resource registered with blank accessibility
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_empty_zero_length'
		sent_resource['accessibility'] = ''
		
		expected_response = {
			'accessibility': [
				'This field may not be blank.'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_accessibility_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_accessibility_invalid(self):
		"""Sending incorrect value as 'accessibility'
		Purpose:
			Sending incorrect value as accessibility
		Sent:
			incorrect value for accessibility
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_invalid'
		sent_resource['accessibility'] = 'random string here'

		expected_response = {
			'accessibility': [
				'Invalid value: random string here.'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_accessibility_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_accessibility_array(self):
		"""Sending as 'accessibility': array
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_array'
		sent_resource['accessibility'] = ['a','b','c',['d']]

		expected_response = {
			'accessibility': [
				"Invalid value: [u'a', u'b', u'c', [u'd']]."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_accessibility_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_accessibility_dict(self):
		"""Sending as 'accessibility': dictionary
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_dict'
		sent_resource['accessibility'] = {'a':'b','c':[1,2,3]}

		expected_response = {
			'accessibility': [
				"Invalid value: {u'a': u'b', u'c': [1, 2, 3]}."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_accessibility_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_accessibility_number(self):
		"""Sending as 'accessibility': number
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_number'
		sent_resource['accessibility'] = 1234567890

		expected_response = {
			'accessibility': [
				"Invalid value: 1234567890."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_accessibility_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_accessibility_case_sensitive(self):
		"""Sending correct value but with wrong case as 'accessibility'
		Purpose:
			What happens when we send correct value but with incorrect case (public instead of Public)
		Sent:
			Value with correct string but lowercase (public instead of Public)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_accessibility_case_sensitive'
		sent_resource['accessibility'] = 'public'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_accessibility_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_accessibility_case_sensitive'
		expected_resource['accessibility'] = 'Public'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
