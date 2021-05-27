# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestContactEmail(BaseTestObject):

	def test_contactEmail_correct(self):
		"""Sending a correctly formatted string as 'contactEmail'
		Purpose:
			Basic test of successful sending of a string as contactEmail
		Sent:
			contactEmail as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_correct'
		sent_resource['contact'] = [
			{
				'contactEmail': 'person@example.com'
			}
		]
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactEmail_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactEmail_correct'
		expected_resource['contact'] = [
			{
				'contactEmail': 'person@example.com',
				'contactURL': None,
				'contactName': None,
				'contactTel': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_contactEmail_empty_none(self):
		"""Sending null/None as 'contactEmail'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_empty_none'
		sent_resource['contact'] = [
			{
				'contactEmail': None
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactEmail': [
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
		
		response = self.client.get('/tool/test_contactEmail_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactEmail_empty_zero_length(self):
		"""Sending string of zero length as 'contactEmail'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_empty_zero_length'
		sent_resource['contact'] = [
			{
				'contactEmail': ''
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactEmail': [
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
		
		response = self.client.get('/tool/test_contactEmail_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactEmail_300_length(self):
		"""Sending 300 times character 'a' as 'contactEmail'
		Purpose:
			What happens when we send string of max allowed length
		Sent:
			300 times 'a'
		Expected outcome:
			Resource registered with 300 times 'a' as a contactEmail
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_300_length'
		sent_resource['contact'] = [
			{
				'contactEmail': 'a@' + 294*'a' + '.com'
			}
		]

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_contactEmail_300_length', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_contactEmail_300_length'
		expected_resource['contact'] = [
			{
				'contactEmail': 'a@' + 294*'a' + '.com',
				'contactURL': None,
				'contactName': None,
				'contactTel': None
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_contactEmail_301_length(self):
		"""Sending 301 times character 'a' as 'contactEmail'
		Purpose:
			What happens when we send more characters than allowed
		Sent:
			301 times 'a'
		Expected outcome:
			Error message informing user of the string length limit
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_301_length'
		sent_resource['contact'] = [
			{
				'contactEmail': 'a@' + 295*'a' + '.com'
			}
		]

		expected_response = {
			'contact': [
				{
					'contactEmail': [
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
		
		response = self.client.get('/tool/test_contactEmail_301_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactEmail_non_ascii(self):
		"""Sending string with non-ascii characters as 'contactEmail'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Error informing about invalid email address.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_non_ascii'
		sent_resource['contact'] = [
			{
				'contactEmail': 'ąęćżźń£ØΔ♥†@example.com'
			}
		]

		expected_response = {
			'contact': [
				{
					'contactEmail': [
						'This is not a valid email address: ąęćżźń£ØΔ♥†@example.com.'
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
		
		response = self.client.get('/tool/test_contactEmail_non_ascii')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactEmail_incorrect(self):
		"""Sending an incorrect string as 'contactEmail'
		Purpose:
			What happens when we send a non-link as contactEmail
		Sent:
			Non-link string
		Expected outcome:
			Error informing about malformed email address
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_incorrect'
		sent_resource['contact'] = [
			{
				'contactEmail': 'person at example.org'
			}
		]

		expected_response = {
			'contact': [
				{
					'contactEmail': [
						'This is not a valid email address: person at example.org.'
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
		
		response = self.client.get('/tool/test_contactEmail_incorrect')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactEmail_array(self):
		"""Sending as 'contactEmail': array
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_array'
		sent_resource['contact'] = [
			{
				'contactEmail': ['a','b','c',['d']]
			}
		]

		expected_response = {
			'contact': [
				{
					'contactEmail': [
						"This is not a valid email address: [u'a', u'b', u'c', [u'd']]."
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
		
		response = self.client.get('/tool/test_contactEmail_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactEmail_dict(self):
		"""Sending as 'contactEmail': dictionary
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_dict'
		sent_resource['contact'] = [
			{
				'contactEmail': {'a':'b','c':[1,2,3]}
			}
		]
		
		expected_response = {
			'contact': [
				{
					'contactEmail': [
						"This is not a valid email address: {u'a': u'b', u'c': [1, 2, 3]}."
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
		
		response = self.client.get('/tool/test_contactEmail_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_contactEmail_number(self):
		"""Sending as 'contactEmail': number
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_contactEmail_number'
		sent_resource['contact'] = [
			{
				'contactEmail': 1234567890
			}
		]

		expected_response = {
			'contact': [
				{
					'contactEmail': [
						"This is not a valid email address: 1234567890."
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
		
		response = self.client.get('/tool/test_contactEmail_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)
