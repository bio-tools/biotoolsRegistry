# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestLanguage(BaseTestObject):

	def test_language_correct_1(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_1'
		sent_resource['language'] = ['ActionScript']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_1'
		expected_resource['language'] = ['ActionScript']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_correct_2(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_2'
		sent_resource['language'] = ['Ada']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_2'
		expected_resource['language'] = ['Ada']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_3(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_3'
		sent_resource['language'] = ['AppleScript']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_3'
		expected_resource['language'] = ['AppleScript']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_4(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_4'
		sent_resource['language'] = ['Assembly language']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_4', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_4'
		expected_resource['language'] = ['Assembly language']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_5(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_5'
		sent_resource['language'] = ['Bash']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_5', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_5'
		expected_resource['language'] = ['Bash']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_6(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_6'
		sent_resource['language'] = ['C']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_6', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_6'
		expected_resource['language'] = ['C']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_correct_7(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_7'
		sent_resource['language'] = ['C++']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_7', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_7'
		expected_resource['language'] = ['C++']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_8(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_8'
		sent_resource['language'] = ['C#']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_8', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_8'
		expected_resource['language'] = ['C#']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_9(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_9'
		sent_resource['language'] = ['COBOL']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_9', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_9'
		expected_resource['language'] = ['COBOL']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_10(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_10'
		sent_resource['language'] = ['ColdFusion']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_10', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_10'
		expected_resource['language'] = ['ColdFusion']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_11(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_11'
		sent_resource['language'] = ['D']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_11', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_11'
		expected_resource['language'] = ['D']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_12(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_12'
		sent_resource['language'] = ['Delphi']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_12', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_12'
		expected_resource['language'] = ['Delphi']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_13(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_13'
		sent_resource['language'] = ['Dylan']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_13', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_13'
		expected_resource['language'] = ['Dylan']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_14(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_14'
		sent_resource['language'] = ['Eiffel']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_14', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_14'
		expected_resource['language'] = ['Eiffel']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_15(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_15'
		sent_resource['language'] = ['Forth']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_15', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_15'
		expected_resource['language'] = ['Forth']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_16(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_16'
		sent_resource['language'] = ['Fortran']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_16', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_16'
		expected_resource['language'] = ['Fortran']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_17(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_17'
		sent_resource['language'] = ['Groovy']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_17', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_17'
		expected_resource['language'] = ['Groovy']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_18(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_18'
		sent_resource['language'] = ['Haskell']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_18', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_18'
		expected_resource['language'] = ['Haskell']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_19(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_19'
		sent_resource['language'] = ['Icarus']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_19', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_19'
		expected_resource['language'] = ['Icarus']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_20(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_20'
		sent_resource['language'] = ['Java']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_20', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_20'
		expected_resource['language'] = ['Java']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_21(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_21'
		sent_resource['language'] = ['Javascript']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_21', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_21'
		expected_resource['language'] = ['Javascript']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_22(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_22'
		sent_resource['language'] = ['LabVIEW']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_22', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_22'
		expected_resource['language'] = ['LabVIEW']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_23(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_23'
		sent_resource['language'] = ['Lisp']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_23', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_23'
		expected_resource['language'] = ['Lisp']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_24(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_24'
		sent_resource['language'] = ['Lua']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_24', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_24'
		expected_resource['language'] = ['Lua']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_25(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_25'
		sent_resource['language'] = ['Maple']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_25', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_25'
		expected_resource['language'] = ['Maple']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_26(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_26'
		sent_resource['language'] = ['Mathematica']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_26', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_26'
		expected_resource['language'] = ['Mathematica']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_27(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_27'
		sent_resource['language'] = ['MATLAB language']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_27', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_27'
		expected_resource['language'] = ['MATLAB language']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_28(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_28'
		sent_resource['language'] = ['MLXTRAN']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_28', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_28'
		expected_resource['language'] = ['MLXTRAN']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_29(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_29'
		sent_resource['language'] = ['NMTRAN']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_29', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_29'
		expected_resource['language'] = ['NMTRAN']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_30(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_30'
		sent_resource['language'] = ['Pascal']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_30', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_30'
		expected_resource['language'] = ['Pascal']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_31(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_31'
		sent_resource['language'] = ['Perl']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_31', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_31'
		expected_resource['language'] = ['Perl']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_32(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_32'
		sent_resource['language'] = ['PHP']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_32', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_32'
		expected_resource['language'] = ['PHP']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_33(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_33'
		sent_resource['language'] = ['Prolog']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_33', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_33'
		expected_resource['language'] = ['Prolog']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_34(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_34'
		sent_resource['language'] = ['Python']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_34', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_34'
		expected_resource['language'] = ['Python']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_35(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_35'
		sent_resource['language'] = ['R']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_35', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_35'
		expected_resource['language'] = ['R']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_36(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_36'
		sent_resource['language'] = ['Racket']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_36', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_36'
		expected_resource['language'] = ['Racket']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_37(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_37'
		sent_resource['language'] = ['REXX']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_37', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_37'
		expected_resource['language'] = ['REXX']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_38(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_38'
		sent_resource['language'] = ['Ruby']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_38', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_38'
		expected_resource['language'] = ['Ruby']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_39(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_39'
		sent_resource['language'] = ['SAS']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_39', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_39'
		expected_resource['language'] = ['SAS']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_40(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_40'
		sent_resource['language'] = ['Scala']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_40', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_40'
		expected_resource['language'] = ['Scala']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_41(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_41'
		sent_resource['language'] = ['Scheme']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_41', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_41'
		expected_resource['language'] = ['Scheme']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		

	def test_language_correct_42(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_42'
		sent_resource['language'] = ['Shell']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_42', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_42'
		expected_resource['language'] = ['Shell']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_correct_43(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_43'
		sent_resource['language'] = ['Smalltalk']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_43', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_43'
		expected_resource['language'] = ['Smalltalk']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_correct_44(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_44'
		sent_resource['language'] = ['SQL']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_44', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_44'
		expected_resource['language'] = ['SQL']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_correct_45(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_45'
		sent_resource['language'] = ['Turing']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_45', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_45'
		expected_resource['language'] = ['Turing']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_correct_46(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_46'
		sent_resource['language'] = ['Verilog']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_46', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_46'
		expected_resource['language'] = ['Verilog']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_correct_47(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_47'
		sent_resource['language'] = ['VHDL']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_47', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_47'
		expected_resource['language'] = ['VHDL']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_correct_48(self):
		"""Sending one of the allowed values as 'language'
		Purpose:
			Basic test of successful sending of an allowed value for language
		Sent:
			Allowed value for language
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_correct_48'
		sent_resource['language'] = ['Visual Basic']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_correct_48', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_correct_48'
		expected_resource['language'] = ['Visual Basic']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_empty_none(self):
		"""Sending null/None as 'language'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_empty_none'
		sent_resource['language'] = None

		expected_response = {
			'language': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_language_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_language_empty_zero_length(self):
		"""Sending empty array as 'language'
		Purpose:
			What happens when we send empty array
		Sent:
			[]
		Expected outcome:
			Error informing that this field cannot be empty
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_empty_zero_length'
		sent_resource['language'] = []

		expected_response = {
			'language': {
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
		
		response = self.client.get('/tool/test_language_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_language_invalid(self):
		"""Sending incorrect value as 'language'
		Purpose:
			Sending incorrect value as language
		Sent:
			incorrect value for language
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_invalid'
		sent_resource['language'] = ['random string here']

		expected_response = {
			'language': [
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
		
		response = self.client.get('/tool/test_language_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)

	
	def test_language_string(self):
		"""Sending a string as 'language'
		Purpose:
			What happens when we send a string
		Sent:
			'random string here'
		Expected outcome:
			Error stating incorrect type
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_string'
		sent_resource['language'] = 'random string here'

		expected_response = {
			'language': {
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
		
		response = self.client.get('/tool/test_language_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_language_array(self):
		"""Sending array as 'language'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_array'
		sent_resource['language'] = ['a','b',['d']]

		expected_response = {
			'language': [
				[
					'Invalid value: a.'
				],
				[
					'Invalid value: b.'
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
		
		response = self.client.get('/tool/test_language_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_language_dict(self):
		"""Sending dictionary as 'language'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_dict'
		sent_resource['language'] = {'a':'b','c':[1, 2, 3]}

		expected_response = {
			'language': {
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
		
		response = self.client.get('/tool/test_language_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_language_number(self):
		"""Sending number as 'language'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_number'
		sent_resource['language'] = 1234567890

		expected_response = {
			'language': {
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
		
		response = self.client.get('/tool/test_language_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_language_case_sensitive(self):
		"""Sending correct value but with wrong case as 'language'
		Purpose:
			What happens when we send correct value but with incorrect case (php instead of PHP)
		Sent:
			Value with correct string but lowercase (php instead of PHP)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_case_sensitive'
		sent_resource['language'] = ['php']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_case_sensitive'
		expected_resource['language'] = ['PHP']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)


	def test_language_duplicate(self):
		"""Sending two identical strings as 'language'
		Purpose:
			Checking if the system will remove duplicate elements
		Sent:
			Two identical language strings
		Expected outcome:
			Resource registered without the duplicate string
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_language_duplicate'
		sent_resource['language'] = ['AppleScript', 'AppleScript']
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_language_duplicate', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_language_duplicate'
		expected_resource['language'] = ['AppleScript']

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertItemsEqual(expected_resource, received_resource)
		