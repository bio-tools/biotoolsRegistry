# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestPublicationsPrimaryID(BaseTestObject):

	def test_publicationsPrimaryID_correct_1(self):
		"""Sending one of the allowed values as 'publicationsPrimaryID'
		Purpose:
			Basic test of successful sending of an allowed value for publicationsPrimaryID
		Sent:
			Allowed value for publicationsPrimaryID
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_correct_1'
		sent_resource['publications'] = {
			'publicationsPrimaryID': '21959131'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_publicationsPrimaryID_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_publicationsPrimaryID_correct_1'
		expected_resource['publications'] = {
			'publicationsPrimaryID': '21959131',
			'publicationsOtherID': []
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_publicationsPrimaryID_correct_2(self):
		"""Sending one of the allowed values as 'publicationsPrimaryID'
		Purpose:
			Basic test of successful sending of an allowed value for publicationsPrimaryID
		Sent:
			Allowed value for publicationsPrimaryID
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_correct_2'
		sent_resource['publications'] = {
			'publicationsPrimaryID': 'PMC21959131'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_publicationsPrimaryID_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_publicationsPrimaryID_correct_2'
		expected_resource['publications'] = {
			'publicationsPrimaryID': 'PMC21959131',
			'publicationsOtherID': []
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_publicationsPrimaryID_correct_3(self):
		"""Sending one of the allowed values as 'publicationsPrimaryID'
		Purpose:
			Basic test of successful sending of an allowed value for publicationsPrimaryID
		Sent:
			Allowed value for publicationsPrimaryID
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_correct_3'
		sent_resource['publications'] = {
			'publicationsPrimaryID': 'doi:10.1038/nmeth.1701'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_publicationsPrimaryID_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_publicationsPrimaryID_correct_3'
		expected_resource['publications'] = {
			'publicationsPrimaryID': 'doi:10.1038/nmeth.1701',
			'publicationsOtherID': []
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_publicationsPrimaryID_empty_none(self):
		"""Sending null/None as 'publicationsPrimaryID'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_empty_none'
		sent_resource['publications'] = {
			'publicationsPrimaryID': None
		}

		expected_response = {
			'publications': {
				'publicationsPrimaryID': [
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
		
		response = self.client.get('/tool/test_publicationsPrimaryID_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsPrimaryID_empty_zero_length(self):
		"""Sending string of zero length as 'publicationsPrimaryID'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_empty_zero_length'
		sent_resource['publications'] = {
			'publicationsPrimaryID': ''
		}

		expected_response = {
			'publications': {
				'publicationsPrimaryID': [
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
		
		response = self.client.get('/tool/test_publicationsPrimaryID_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsPrimaryID_invalid(self):
		"""Sending incorrect value as 'publicationsPrimaryID'
		Purpose:
			Sending incorrect value as publicationsPrimaryID
		Sent:
			incorrect value for publicationsPrimaryID
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_invalid'
		sent_resource['publications'] = {
			'publicationsPrimaryID': 'random string here'
		}

		expected_response = {
			'publications': {
				'publicationsPrimaryID': [
					'This is not a valid publication ID: random string here.'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsPrimaryID_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsPrimaryID_array(self):
		"""Sending array as 'publicationsPrimaryID'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_array'
		sent_resource['publications'] = {
			'publicationsPrimaryID': ['a','b','c',['d']]
		}

		expected_response = {
			'publications': {
				'publicationsPrimaryID': [
					"This is not a valid publication ID: [u'a', u'b', u'c', [u'd']]."
				]
			}
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsPrimaryID_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsPrimaryID_dict(self):
		"""Sending dictionary as 'publicationsPrimaryID'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_dict'
		sent_resource['publications'] = {
			'publicationsPrimaryID': {'a':'b','c':[1,2,3]}
		}

		expected_response = {
			'publications': {
				'publicationsPrimaryID': [
					"This is not a valid publication ID: {u'a': u'b', u'c': [1, 2, 3]}."
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsPrimaryID_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_publicationsPrimaryID_number(self):
		"""Sending number as 'publicationsPrimaryID'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_publicationsPrimaryID_number'
		sent_resource['publications'] = {
			'publicationsPrimaryID': 1234567890
		}

		expected_response = {
			'publications': {
				'publicationsPrimaryID': [
					'This is not a valid publication ID: 1234567890.'
				]
			}
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_publicationsPrimaryID_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)
