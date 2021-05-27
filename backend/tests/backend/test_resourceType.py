# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestResourceType(BaseTestObject):

	def test_resourceType_correct_1(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_correct_1'
		sent_resource['resourceType'] = ['Database']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_correct_1'
		expected_resource['resourceType'] = ['Database']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_resourceType_correct_2(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_correct_2'
		sent_resource['resourceType'] = ['Tool']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_correct_2'
		expected_resource['resourceType'] = ['Tool']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
	

	def test_resourceType_correct_3(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_correct_3'
		sent_resource['resourceType'] = ['Service']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_correct_3'
		expected_resource['resourceType'] = ['Service']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
	

	def test_resourceType_correct_4(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_correct_4'
		sent_resource['resourceType'] = ['Workflow']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_correct_4', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_correct_4'
		expected_resource['resourceType'] = ['Workflow']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
	

	def test_resourceType_correct_5(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_correct_5'
		sent_resource['resourceType'] = ['Platform']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_correct_5', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_correct_5'
		expected_resource['resourceType'] = ['Platform']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
	

	def test_resourceType_correct_6(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_correct_6'
		sent_resource['resourceType'] = ['Container']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_correct_6', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_correct_6'
		expected_resource['resourceType'] = ['Container']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
	

	def test_resourceType_correct_7(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_correct_7'
		sent_resource['resourceType'] = ['Library']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_correct_7', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_correct_7'
		expected_resource['resourceType'] = ['Library']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_resourceType_correct_8(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_correct_8'
		sent_resource['resourceType'] = ['Other']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_correct_8', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_correct_8'
		expected_resource['resourceType'] = ['Other']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_resourceType_2_correct(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_2_correct'
		sent_resource['resourceType'] = ['Tool', 'Other']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_2_correct', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_2_correct'
		expected_resource['resourceType'] = ['Tool', 'Other']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_resourceType_1_correct_1_not(self):
		"""Sending one of the allowed values as 'resourceType'
		Purpose:
			Basic test of successful sending of an allowed value for resourceType
		Sent:
			Allowed value for resourceType
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_1_correct_1_not'
		sent_resource['resourceType'] = ['Tool', 'random string here']
		
		expected_response = {
			'resourceType': [
				{},
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
		
		response = self.client.get('/tool/test_resourceType_1_correct_1_not')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_resourceType_empty_none(self):
		"""Sending null/None as 'resourceType'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_empty_none'
		sent_resource['resourceType'] = None

		expected_response = {
			'resourceType': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_resourceType_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_resourceType_empty_zero_length(self):
		"""Sending empty array as 'resourceType'
		Purpose:
			What happens when we send empty array
		Sent:
			[]
		Expected outcome:
			Error informing that this field cannot be empty
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_empty_zero_length'
		sent_resource['resourceType'] = []

		expected_response = {
			'resourceType': {
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
		
		response = self.client.get('/tool/test_resourceType_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_resourceType_invalid(self):
		"""Sending incorrect value as 'resourceType'
		Purpose:
			Sending incorrect value as resourceType
		Sent:
			incorrect value for resourceType
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_invalid'
		sent_resource['resourceType'] = ['random string here']

		expected_response = {
			'resourceType': [
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
		
		response = self.client.get('/tool/test_resourceType_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)

	
	def test_resourceType_string(self):
		"""Sending a string as 'resourceType'
		Purpose:
			What happens when we send a string
		Sent:
			'random string here'
		Expected outcome:
			Error stating incorrect type
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_string'
		sent_resource['resourceType'] = 'random string here'

		expected_response = {
			'resourceType': {
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
		
		response = self.client.get('/tool/test_resourceType_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_resourceType_array(self):
		"""Sending array as 'resourceType'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_array'
		sent_resource['resourceType'] = ['a','b','c',['d']]

		expected_response = {
			'resourceType': [
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
		
		response = self.client.get('/tool/test_resourceType_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_resourceType_dict(self):
		"""Sending dictionary as 'resourceType'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_dict'
		sent_resource['resourceType'] = {'a':'b','c':[1, 2, 3]}

		expected_response = {
			'resourceType': {
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
		
		response = self.client.get('/tool/test_resourceType_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_resourceType_number(self):
		"""Sending number as 'resourceType'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_number'
		sent_resource['resourceType'] = 1234567890

		expected_response = {
			'resourceType': {
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
		
		response = self.client.get('/tool/test_resourceType_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_resourceType_case_sensitive(self):
		"""Sending correct value but with wrong case as 'resourceType'
		Purpose:
			What happens when we send correct value but with incorrect case (tool instead of Tool)
		Sent:
			Value with correct string but lowercase (tool instead of Tool)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_case_sensitive'
		sent_resource['resourceType'] = ['tool']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_case_sensitive'
		expected_resource['resourceType'] = ['Tool']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_resourceType_duplicate(self):
		"""Sending two identical strings as 'resourceType'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical resourceType strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_resourceType_duplicate'
		sent_resource['resourceType'] = ['Database', 'Database']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_resourceType_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_resourceType_duplicate'
		expected_resource['resourceType'] = ['Database']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
