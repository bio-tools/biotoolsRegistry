# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestCost(BaseTestObject):

	def test_cost_correct_1(self):
		"""Sending one of the allowed values as 'cost'
		Purpose:
			Basic test of successful sending of an allowed value for cost
		Sent:
			Allowed value for cost
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_correct_1'
		sent_resource['cost'] = 'Free'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_cost_correct_1', format='json')

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_cost_correct_1'
		expected_resource['cost'] = 'Free'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(expected_resource, received_resource)


	def test_cost_correct_2(self):
		"""Sending one of the allowed values as 'cost'
		Purpose:
			Basic test of successful sending of an allowed value for cost
		Sent:
			Allowed value for cost
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_correct_2'
		sent_resource['cost'] = 'Free with restrictions'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_cost_correct_2', format='json')

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_cost_correct_2'
		expected_resource['cost'] = 'Free with restrictions'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(expected_resource, received_resource)


	def test_cost_correct_3(self):
		"""Sending one of the allowed values as 'cost'
		Purpose:
			Basic test of successful sending of an allowed value for cost
		Sent:
			Allowed value for cost
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_correct_3'
		sent_resource['cost'] = 'Commercial'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_cost_correct_3', format='json')

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_cost_correct_3'
		expected_resource['cost'] = 'Commercial'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(expected_resource, received_resource)


	def test_cost_empty_none(self):
		"""Sending null/None as 'cost'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_empty_none'
		sent_resource['cost'] = None
		
		
		expected_response = {
			'cost': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_cost_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_cost_empty_zero_length(self):
		"""Sending string of zero length as 'cost'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_zero_length'
		sent_resource['cost'] = ''
		
		expected_response =  {
			'cost': [
				'This field may not be blank.'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_cost_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_cost_invalid(self):
		"""Sending incorrect value as 'cost'
		Purpose:
			Sending incorrect value as elixirNode
		Sent:
			incorrect value for elixirNode
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_invalid'
		sent_resource['cost'] = 'random string here'

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

		response = self.client.get('/tool/test_cost_invalid', format='json')

		expected_response = {
			'cost': [
				'Invalid value: random string here.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_cost_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_cost_array(self):
		"""Sending array as 'cost'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_array'
		sent_resource['cost'] = ['a','b','c',['d']]

		expected_response = {
			'cost': [
				"Invalid value: [u'a', u'b', u'c', [u'd']]."
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_cost_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_cost_dict(self):
		"""Sending dictionary as 'cost'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_dict'
		sent_resource['cost'] = {'a':'b','c':[1,2,3]}

		expected_response = {
			'cost': [
				"Invalid value: {u'a': u'b', u'c': [1, 2, 3]}."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_cost_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_cost_number(self):
		"""Sending number as 'cost'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_number'
		sent_resource['cost'] = 1234567890

		expected_response = {
			'cost': [
				"Invalid value: 1234567890."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_cost_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)

	
	def test_cost_case_insensitive(self):
		"""Sending correct value but with wrong case as 'cost'
		Purpose:
			What happens when we send correct value but with incorrect case (free instead of Free)
		Sent:
			Value with correct string but lowercase (free instead of Free)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_cost_case_insensitive'
		sent_resource['cost'] = 'free'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_cost_case_insensitive', format='json')

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_cost_case_insensitive'
		expected_resource['cost'] = 'Free'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(expected_resource, received_resource)
