# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestPublicationsOtherID(BaseTestObject):

	def test_publicationsOtherID_correct_1(self):
		"""Sending one string as 'publicationsOtherID'
		Purpose:
			Basic test of successful sending of a string as publicationsOtherID
		Sent:
			publicationsOtherID as a string
		Expected outcome:
			Resource registered with the sent string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_correct_1'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['21959131']
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_publicationsOtherID_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_publicationsOtherID_correct_1'
		expected_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['21959131']
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_publicationsOtherID_correct_2(self):
		"""Sending two strings as 'publicationsOtherID'
		Purpose:
			Basic test of successful sending of a string as publicationsOtherID
		Sent:
			publicationsOtherID as a string
		Expected outcome:
			Resource registered with the sent array of 2 strings
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_correct_2'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['PMC21959131']
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_publicationsOtherID_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_publicationsOtherID_correct_2'
		expected_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['PMC21959131']
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_publicationsOtherID_correct_3(self):
		"""Sending two strings as 'publicationsOtherID'
		Purpose:
			Basic test of successful sending of a string as publicationsOtherID
		Sent:
			publicationsOtherID as a string
		Expected outcome:
			Resource registered with the sent array of 2 strings
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_correct_3'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['doi:10.1038/nmeth.1701']
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_publicationsOtherID_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_publicationsOtherID_correct_3'
		expected_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['doi:10.1038/nmeth.1701']
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_publicationsOtherID_correct_3_diff(self):
		"""Sending two strings as 'publicationsOtherID'
		Purpose:
			Basic test of successful sending of a string as publicationsOtherID
		Sent:
			publicationsOtherID as a string
		Expected outcome:
			Resource registered with the sent array of 2 strings
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_correct_3'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['21959131', 'PMC21959131', 'doi:10.1038/nmeth.1701']
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_publicationsOtherID_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_publicationsOtherID_correct_3'
		expected_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['21959131', 'PMC21959131', 'doi:10.1038/nmeth.1701']
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_publicationsOtherID_1_correct_1_wrong(self):
		"""Sending two strings as 'publicationsOtherID'
		Purpose:
			Basic test of successful sending of a string as publicationsOtherID
		Sent:
			publicationsOtherID as a string
		Expected outcome:
			Resource registered with the sent array of 2 strings
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_1_correct_1_wrong'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['21959131', 'PMC21959131', 'string here']
		}
		
		expected_response = {
			'publications': {
				'publicationsOtherID': [
					{},
					{},
					{
						'general_errors': [
							'This is not a valid publication ID: string here.'
						]
					}
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsOtherID_1_correct_1_wrong')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_empty_none(self):
		"""Sending null/None as 'publicationsOtherID'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_empty_none'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': None
		}

		
		expected_response = {
			'publications': {
				'publicationsOtherID': [
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
		
		response = self.client.get('/tool/test_publicationsOtherID_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_empty_zero_length(self):
		"""Sending string of zero length as 'publicationsOtherID'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_empty_zero_length'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ''
		}
		
		expected_response = {
			'publications': {
				'publicationsOtherID': {
					'general_errors': [
						'Expected a list of items but got type "unicode".'
					]
				}
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsOtherID_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_non_ascii(self):
		"""Sending string with non-ascii characters as 'publicationsOtherID'
		Purpose:
			What happens when we send non-ascii characters
		Sent:
			String with non-ascii characters
		Expected outcome:
			Resource registered with the non-ascii characters
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_non_ascii'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['ąęćżźń£ Ø Δ ♥ †']
		}
		
		expected_response = {
			'publications': {
				'publicationsOtherID': [
					{
						'general_errors': [
							'This is not a valid publication ID: ąęćżźń£ Ø Δ ♥ †.'
						]
					}
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsOtherID_non_ascii')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_array(self):
		"""Sending array as 'publicationsOtherID'
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
		sent_resource['id'] = 'test_publicationsOtherID_array'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': [['d']]
		}

		expected_response = {
			'publications': {
				'publicationsOtherID': [
					{
						'general_errors': [
							'Wrong type found, expected unicode/string, got array/list.'
						]
					}
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsOtherID_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_dict(self):
		"""Sending dictionary as 'publicationsOtherID'
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
		sent_resource['id'] = 'test_publicationsOtherID_dict'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': {'a':'b','c':[1,2,3]}
		}

		expected_response = {
			'publications': {
				'publicationsOtherID': {
					'general_errors': [
						'Expected a list of items but got type "dict".'
					]
				}
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsOtherID_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_number(self):
		"""Sending number as 'publicationsOtherID'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Resource registered with stringified number.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_number'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': 1234567890
		}

		expected_response = {
			'publications': {
				'publicationsOtherID': {
					'general_errors': [
						'Expected a list of items but got type "int".'
					]
				}
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)
		
		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsOtherID_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_array_number(self):
		"""Sending array of numbers as 'publicationsOtherID'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of numbers
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_array_number'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': [1]
		}
		
		expected_response = {
			'publications': {
				'publicationsOtherID': [
					{
						'general_errors': [
							'Wrong type found, expected unicode/string, got integer/number.'
						]
					}
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsOtherID_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_array_dict(self):
		"""Sending array of dictionaries as 'publicationsOtherID'
		Purpose:
			What happens when we send wrong type as the field (this case - array of dictionaries)
		Sent:
			Array of dictionaries
		Expected outcome:
			Registered resource with stringified value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_array_dict'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': [{'a':'b','c':5}]
		}

		expected_response = {
			'publications': {
				'publicationsOtherID': [
					{
						'general_errors': [
							'Wrong type found, expected unicode/string, got dictionary/hash.'
						]
					}
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsOtherID_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsOtherID_duplicate(self):
		"""Sending two identical strings as 'publicationsOtherID'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical publicationsOtherID strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsOtherID_duplicate'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['21959131', '21959131']
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_publicationsOtherID_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_publicationsOtherID_duplicate'
		expected_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': ['21959131']
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
