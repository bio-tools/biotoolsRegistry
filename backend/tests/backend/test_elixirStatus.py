# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestElixirStatus(BaseTestObject):

	def test_elixirStatus_correct_1(self):
		"""Sending one of the allowed values as 'elixirStatus'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_correct_1'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': 'ELIXIR Core Service'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirStatus_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirStatus_correct_1'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': 'ELIXIR Core Service'
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_elixirStatus_correct_2(self):
		"""Sending one of the allowed values as 'elixirStatus'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_correct_2'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': 'ELIXIR Named Service'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirStatus_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirStatus_correct_2'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': 'ELIXIR Named Service'
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_elixirStatus_empty_none(self):
		"""Sending null/None as 'elixirStatus'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_empty_none'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': None
		}

		expected_response = {
			'elixirInfo': {
				'elixirStatus': [
					'This field may not be null.'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_elixirStatus_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirStatus_empty_zero_length(self):
		"""Sending string of zero length as 'elixirStatus'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_empty_zero_length'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': ''
		}

		expected_response = {
			'elixirInfo': {
				'elixirStatus': [
					'This field may not be blank.'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_elixirStatus_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirStatus_invalid(self):
		"""Sending incorrect value as 'elixirStatus'
		Purpose:
			Sending incorrect value as elixirNode
		Sent:
			incorrect value for elixirNode
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_invalid'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': 'random string here'
		}

		expected_response = {
			'elixirInfo': {
				'elixirStatus': [
					'Invalid value: random string here.'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_elixirStatus_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirStatus_array(self):
		"""Sending array as 'elixirStatus'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_array'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': ['a','b','c',['d']]
		}

		expected_response = {
			'elixirInfo': {
				'elixirStatus': [
					"Invalid value: [u'a', u'b', u'c', [u'd']]."
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_elixirStatus_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirStatus_dict(self):
		"""Sending dictionary as 'elixirStatus'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_dict'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': {'a':'b','c':[1,2,3]}
		}

		expected_response = {
			'elixirInfo': {
				'elixirStatus': [
					"Invalid value: {u'a': u'b', u'c': [1, 2, 3]}."
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_elixirStatus_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirStatus_number(self):
		"""Sending number as 'elixirStatus'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_number'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': 1234567890
		}

		expected_response = {
			'elixirInfo': {
				'elixirStatus': [
					"Invalid value: 1234567890."
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_elixirStatus_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirStatus_case_sensitive(self):
		"""Sending correct value but with wrong case as 'elixirStatus'
		Purpose:
			What happens when we send correct value but with incorrect case (elixir core service instead of ELIXIR Core Service)
		Sent:
			Value with correct string but lowercase (elixir core service instead of ELIXIR Core Service)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirStatus_case_sensitive'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': 'elixir core service'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirStatus_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirStatus_case_sensitive'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': 'ELIXIR Core Service'
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
