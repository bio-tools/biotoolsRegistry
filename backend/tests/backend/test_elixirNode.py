# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestElixirNode(BaseTestObject):

	def test_elixirNode_correct_1(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_1'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Denmark'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_1'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_elixirNode_correct_2(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_2'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Czech Republic'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_2'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Czech Republic',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_elixirNode_correct_3(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_3'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Belgium'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_3'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Belgium',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_4(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_4'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'EMBL-EBI'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_4', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_4'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'EMBL-EBI',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_5(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_5'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Estonia'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_5', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_5'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Estonia',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_elixirNode_correct_6(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_6'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Finland'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_6', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_6'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Finland',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_elixirNode_correct_7(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_7'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'France'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_7', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_7'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'France',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_8(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_8'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Greece'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_8', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_8'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Greece',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_9(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_9'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Israel'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_9', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_9'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Israel',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_10(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_10'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Italy'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_10', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_10'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Italy',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_11(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_11'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Netherlands'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_11', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_11'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Netherlands',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_elixirNode_correct_12(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_12'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Norway'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_12', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_12'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Norway',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_13(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_13'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Portugal'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_13', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_13'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Portugal',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_14(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_14'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Slovenia'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_14', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_14'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Slovenia',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_15(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_15'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Spain'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_15', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_15'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Spain',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_16(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_16'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Sweden'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_16', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_16'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Sweden',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_17(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_17'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'Switzerland'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_17', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_17'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Switzerland',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	
	def test_elixirNode_correct_18(self):
		"""Sending one of the allowed values as 'elixirNode'
		Purpose:
			Basic test of successful sending of an allowed value for elixirNode
		Sent:
			Allowed value for elixirNode
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_correct_18'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'UK'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_correct_18', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_correct_18'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'UK',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_elixirNode_empty_none(self):
		"""Sending null/None as 'elixirNode'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_empty_none'
		sent_resource['elixirInfo'] = {
			'elixirNode': None
		}

		expected_response = {
			'elixirInfo': {
				'elixirNode': [
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
		
		response = self.client.get('/tool/test_elixirNode_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirNode_empty_zero_length(self):
		"""Sending string of zero length as 'elixirNode'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_empty_zero_length'
		sent_resource['elixirInfo'] = {
			'elixirNode': ''
		}

		expected_response = {
			'elixirInfo': {
				'elixirNode': [
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
		
		response = self.client.get('/tool/test_elixirNode_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirNode_invalid(self):
		"""Sending incorrect value as 'elixirNode'
		Purpose:
			Sending incorrect value as elixirNode
		Sent:
			incorrect value for elixirNode
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_invalid'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'random string here'
		}

		expected_response = {
			'elixirInfo': {
				'elixirNode': [
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
		
		response = self.client.get('/tool/test_elixirNode_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirNode_array(self):
		"""Sending array as 'elixirNode'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_array'
		sent_resource['elixirInfo'] = {
			'elixirNode': ['a','b','c',['d']]
		}

		expected_response = {
			'elixirInfo': {
				'elixirNode': [
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
		
		response = self.client.get('/tool/test_elixirNode_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirNode_dict(self):
		"""Sending dictionary as 'elixirNode'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_dict'
		sent_resource['elixirInfo'] = {
			'elixirNode': {'a':'b','c':[1,2,3]}
		}

		expected_response = {
			'elixirInfo': {
				'elixirNode': [
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
		
		response = self.client.get('/tool/test_elixirNode_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirNode_number(self):
		"""Sending number as 'elixirNode'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_number'
		sent_resource['elixirInfo'] = {
			'elixirNode': 1234567890
		}

		expected_response = {
			'elixirInfo': {
				'elixirNode': [
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
		
		response = self.client.get('/tool/test_elixirNode_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_elixirNode_case_sensitive(self):
		"""Sending correct value but with wrong case as 'elixirNode'
		Purpose:
			What happens when we send correct value but with incorrect case (denmark instead of Denmark)
		Sent:
			Value with correct string but lowercase (denmark instead of Denmark)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_elixirNode_case_sensitive'
		sent_resource['elixirInfo'] = {
			'elixirNode': 'denmark'
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_elixirNode_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_elixirNode_case_sensitive'
		expected_resource['elixirInfo'] = {
			'elixirNode': 'Denmark',
			'elixirStatus': None
		}

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
