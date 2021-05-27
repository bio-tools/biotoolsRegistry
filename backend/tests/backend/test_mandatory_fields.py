from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestMandatoryFields(BaseTestObject):
	
	def test_missing_topic(self):
		"""Sending resource with missing Topic
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing Topic
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_topic'
		del sent_resource['topic']

		expected_response = {
			'topic': [
				'This field is required.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_missing_topic')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)

	def test_missing_name(self):
		"""Sending resource with missing name
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing name
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_name'
		del sent_resource['name']

		expected_response = {
			'name': [
				'This field is required.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_missing_name')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_missing_homepage(self):
		"""Sending resource with missing homepage
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing homepage
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_homepage'
		del sent_resource['homepage']

		expected_response = {
			'homepage': [
				'This field is required.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_missing_homepage')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_missing_resourceType(self):
		"""Sending resource with missing resourceType
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing resourceType
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_resourceType'
		del sent_resource['resourceType']

		expected_response = {
			'resourceType': [
				'This field is required.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_missing_resourceType')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_missing_interface(self):
		"""Sending resource with missing interface
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing interface
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_interface'
		del sent_resource['interface']

		expected_response = {
			'interface': [
				'This field is required.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_missing_interface')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_missing_interfaceType(self):
		"""Sending resource with missing interfaceType
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing interfaceType
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_interfaceType'
		del sent_resource['interface'][0]['interfaceType']

		expected_response = {
			'interface': [
				{
					'interfaceType': [
						'This field is required.'
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
		
		response = self.client.get('/tool/test_missing_interfaceType')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)

	
	def test_missing_description(self):
		"""Sending resource with missing description
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing description
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_description'
		del sent_resource['description']

		expected_response = {
			'description': [
				'This field is required.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_missing_description')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_missing_function(self):
		"""Sending resource with missing function
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing function
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_function'
		del sent_resource['function']

		expected_response = {
			'function': [
				'This field is required.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_missing_function')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_missing_operation(self):
		"""Sending resource with missing operation
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing operation
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_operation'
		del sent_resource['function'][0]['operation']

		expected_response = {
			'function': [
				{
					'operation': [
						'This field is required.'
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
		
		response = self.client.get('/tool/test_missing_operation')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_missing_contact(self):
		"""Sending resource with missing contact
		Purpose:
			Test mandatory field checker
		Sent:
			Basic Resource with missing contact
		Expected outcome:
			Error informing about missing mandatory field
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_missing_contact'
		del sent_resource['contact']

		expected_response = {
			'contact': [
				'This field is required.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_missing_contact')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)
