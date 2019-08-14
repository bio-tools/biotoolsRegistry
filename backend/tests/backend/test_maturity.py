# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestMaturity(BaseTestObject):

	def test_maturity_correct_1(self):
		"""Sending one of the allowed values as 'maturity'
		Purpose:
			Basic test of successful sending of an allowed value for maturity
		Sent:
			Allowed value for maturity
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_correct_1'
		sent_resource['maturity'] = 'Early'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_maturity_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_maturity_correct_1'
		expected_resource['maturity'] = 'Early'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_maturity_correct_2(self):
		"""Sending one of the allowed values as 'maturity'
		Purpose:
			Basic test of successful sending of an allowed value for maturity
		Sent:
			Allowed value for maturity
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_correct_2'
		sent_resource['maturity'] = 'Stable'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_maturity_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_maturity_correct_2'
		expected_resource['maturity'] = 'Stable'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_maturity_correct_3(self):
		"""Sending one of the allowed values as 'maturity'
		Purpose:
			Basic test of successful sending of an allowed value for maturity
		Sent:
			Allowed value for maturity
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_correct_3'
		sent_resource['maturity'] = 'Deprecated'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_maturity_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_maturity_correct_3'
		expected_resource['maturity'] = 'Deprecated'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_maturity_empty_none(self):
		"""Sending null/None as 'maturity'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_empty_none'
		sent_resource['maturity'] = None

		expected_response = {
			'maturity': [
				'This field may not be null.'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_maturity_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_maturity_empty_zero_length(self):
		"""Sending string of zero length as 'maturity'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_empty_zero_length'
		sent_resource['maturity'] = ''

		expected_response = {
			'maturity': [
				'This field may not be blank.'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_maturity_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_maturity_invalid(self):
		"""Sending incorrect value as 'maturity'
		Purpose:
			Sending incorrect value as maturity
		Sent:
			incorrect value for maturity
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_invalid'
		sent_resource['maturity'] = 'random string here'

		expected_response = {
			'maturity': [
				'Invalid value: random string here.'
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_maturity_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_maturity_array(self):
		"""Sending as 'maturity': array
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_array'
		sent_resource['maturity'] = ['a','b','c',['d']]

		expected_response = {
			'maturity': [
				"Invalid value: [u'a', u'b', u'c', [u'd']]."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_maturity_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_maturity_dict(self):
		"""Sending as 'maturity': dictionary
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_dict'
		sent_resource['maturity'] = {'a':'b','c':[1,2,3]}

		expected_response = {
			'maturity': [
				"Invalid value: {u'a': u'b', u'c': [1, 2, 3]}."
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_maturity_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_maturity_number(self):
		"""Sending as 'maturity': number
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_number'
		sent_resource['maturity'] = 1234567890

		expected_response = {
			'maturity': [
				"Invalid value: 1234567890."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)	
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_maturity_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_maturity_case_sensitive(self):
		"""Sending correct value but with wrong case as 'maturity'
		Purpose:
			What happens when we send correct value but with incorrect case (stable instead of Stable)
		Sent:
			Value with correct string but lowercase (stable instead of Stable)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_maturity_case_sensitive'
		sent_resource['maturity'] = 'stable'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_maturity_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_maturity_case_sensitive'
		expected_resource['maturity'] = 'Stable'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		