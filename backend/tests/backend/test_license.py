# -*- coding: UTF-8 -*-
from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestLicense(BaseTestObject):

	def test_license_correct_1(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_1'
		sent_resource['license'] = 'Apache License 2.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_1', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_1'
		expected_resource['license'] = 'Apache License 2.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_license_correct_2(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_2'
		sent_resource['license'] = 'Artistic License 2.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_2', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_2'
		expected_resource['license'] = 'Artistic License 2.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_3(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_3'
		sent_resource['license'] = 'MIT License'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_3', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_3'
		expected_resource['license'] = 'MIT License'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_4(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_4'
		sent_resource['license'] = 'GNU General Public License v3'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_4', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_4'
		expected_resource['license'] = 'GNU General Public License v3'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_5(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_5'
		sent_resource['license'] = 'GNU Lesser General Public License v2.1'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_5', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_5'
		expected_resource['license'] = 'GNU Lesser General Public License v2.1'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_6(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_6'
		sent_resource['license'] = 'GNU General Public License v2'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_6', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_6'
		expected_resource['license'] = 'GNU General Public License v2'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_license_correct_7(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_7'
		sent_resource['license'] = 'GNU Affero General Public License v3'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_7', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_7'
		expected_resource['license'] = 'GNU Affero General Public License v3'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_8(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_8'
		sent_resource['license'] = 'BSD 3-Clause License (Revised)'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_8', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_8'
		expected_resource['license'] = 'BSD 3-Clause License (Revised)'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_9(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_9'
		sent_resource['license'] = 'BSD 2-Clause License'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_9', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_9'
		expected_resource['license'] = 'BSD 2-Clause License'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_10(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_10'
		sent_resource['license'] = 'Creative Commons Attribution NonCommerical NoDerivs'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_10', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_10'
		expected_resource['license'] = 'Creative Commons Attribution NonCommerical NoDerivs'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_11(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_11'
		sent_resource['license'] = 'Microsoft Public License'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_11', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_11'
		expected_resource['license'] = 'Microsoft Public License'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_12(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_12'
		sent_resource['license'] = 'Mozilla Public License 2.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_12', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_12'
		expected_resource['license'] = 'Mozilla Public License 2.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_13(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_13'
		sent_resource['license'] = 'Creative Commons Attribution NoDerivs'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_13', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_13'
		expected_resource['license'] = 'Creative Commons Attribution NoDerivs'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_14(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_14'
		sent_resource['license'] = 'Eclipse Public License 1.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_14', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_14'
		expected_resource['license'] = 'Eclipse Public License 1.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_15(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_15'
		sent_resource['license'] = 'Microsoft Reciprocal License'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_15', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_15'
		expected_resource['license'] = 'Microsoft Reciprocal License'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_16(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_16'
		sent_resource['license'] = 'PHP License 3.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_16', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_16'
		expected_resource['license'] = 'PHP License 3.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_17(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_17'
		sent_resource['license'] = 'Creative Commons Attribution 3.0 Unported'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_17', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_17'
		expected_resource['license'] = 'Creative Commons Attribution 3.0 Unported'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_18(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_18'
		sent_resource['license'] = 'Creative Commons Attribution Share Alike'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_18', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_18'
		expected_resource['license'] = 'Creative Commons Attribution Share Alike'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_19(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_19'
		sent_resource['license'] = 'Creative Commons Attribution NonCommercial'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_19', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_19'
		expected_resource['license'] = 'Creative Commons Attribution NonCommercial'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_20(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_20'
		sent_resource['license'] = 'Creative Commons Attribution NonCommercial ShareAlike'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_20', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_20'
		expected_resource['license'] = 'Creative Commons Attribution NonCommercial ShareAlike'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_21(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_21'
		sent_resource['license'] = 'Apple Public Source License 2.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_21', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_21'
		expected_resource['license'] = 'Apple Public Source License 2.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_22(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_22'
		sent_resource['license'] = 'ISC License'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_22', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_22'
		expected_resource['license'] = 'ISC License'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_23(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_23'
		sent_resource['license'] = 'IBM Public License'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_23', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_23'
		expected_resource['license'] = 'IBM Public License'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_24(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_24'
		sent_resource['license'] = 'GNU Free Documentation License v1.3'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_24', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_24'
		expected_resource['license'] = 'GNU Free Documentation License v1.3'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_25(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_25'
		sent_resource['license'] = 'Common Public Attribution License Version 1.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_25', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_25'
		expected_resource['license'] = 'Common Public Attribution License Version 1.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_26(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_26'
		sent_resource['license'] = 'European Union Public License 1.1'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_26', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_26'
		expected_resource['license'] = 'European Union Public License 1.1'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_27(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_27'
		sent_resource['license'] = 'ODC Open Database License'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_27', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_27'
		expected_resource['license'] = 'ODC Open Database License'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_28(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_28'
		sent_resource['license'] = 'Simple Public License 2.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_28', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_28'
		expected_resource['license'] = 'Simple Public License 2.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_29(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_29'
		sent_resource['license'] = 'Creative Commons Attribution-NonCommercial 2.0 Generic'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_29', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_29'
		expected_resource['license'] = 'Creative Commons Attribution-NonCommercial 2.0 Generic'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_30(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_30'
		sent_resource['license'] = 'Creative Commons CC0 1.0 Universal'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_30', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_30'
		expected_resource['license'] = 'Creative Commons CC0 1.0 Universal'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_31(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_31'
		sent_resource['license'] = 'Microsoft Shared Source Community License'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_31', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_31'
		expected_resource['license'] = 'Microsoft Shared Source Community License'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_32(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_32'
		sent_resource['license'] = 'Mozilla Public License 1.1'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_32', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_32'
		expected_resource['license'] = 'Mozilla Public License 1.1'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_33(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_33'
		sent_resource['license'] = 'Educational Community License Version 2.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_33', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_33'
		expected_resource['license'] = 'Educational Community License Version 2.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_34(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_34'
		sent_resource['license'] = 'Creative Commons Attribution 4.0 International'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_34', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_34'
		expected_resource['license'] = 'Creative Commons Attribution 4.0 International'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_35(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_35'
		sent_resource['license'] = 'Open Software Licence 3.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_35', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_35'
		expected_resource['license'] = 'Open Software Licence 3.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_36(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_36'
		sent_resource['license'] = 'Common Public License 1.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_36', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_36'
		expected_resource['license'] = 'Common Public License 1.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_37(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_37'
		sent_resource['license'] = 'CeCILL v2'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_37', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_37'
		expected_resource['license'] = 'CeCILL v2'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_38(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_38'
		sent_resource['license'] = 'Adaptive Public License 1.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_38', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_38'
		expected_resource['license'] = 'Adaptive Public License 1.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_39(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_39'
		sent_resource['license'] = 'Non-Profit Open Software License 3.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_39', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_39'
		expected_resource['license'] = 'Non-Profit Open Software License 3.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_40(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_40'
		sent_resource['license'] = 'Reciprocal Public License 1.5'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_40', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_40'
		expected_resource['license'] = 'Reciprocal Public License 1.5'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_41(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_41'
		sent_resource['license'] = 'Open Public License v1.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_41', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_41'
		expected_resource['license'] = 'Open Public License v1.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		

	def test_license_correct_42(self):
		"""Sending one of the allowed values as 'license'
		Purpose:
			Basic test of successful sending of an allowed value for license
		Sent:
			Allowed value for license
		Expected outcome:
			Resource registered with the sent value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_correct_42'
		sent_resource['license'] = 'ODC Public Domain Dedication and License 1.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_correct_42', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_correct_42'
		expected_resource['license'] = 'ODC Public Domain Dedication and License 1.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_license_empty_none(self):
		"""Sending null/None as 'license'
		Purpose:
			What happens when we send None
		Sent:
			None
		Expected outcome:
			Error informing that this field cannot be null/None
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_empty_none'
		sent_resource['license'] = None

		expected_response = {
			'license': [
				'This field may not be null.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_license_empty_none')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_license_empty_zero_length(self):
		"""Sending string of zero length as 'license'
		Purpose:
			What happens when we send empty string (zero length)
		Sent:
			''
		Expected outcome:
			Error informing that this field cannot be blank
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_empty_zero_length'
		sent_resource['license'] = ''

		expected_response = {
			'license': [
				'This field may not be blank.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_license_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_license_invalid(self):
		"""Sending incorrect value as 'license'
		Purpose:
			Sending incorrect value as license
		Sent:
			incorrect value for license
		Expected outcome:
			Error stating incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_invalid'
		sent_resource['license'] = 'random string here'

		expected_response = {
			'license': [
				'Invalid value: random string here.'
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_license_invalid')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_license_array(self):
		"""Sending array as 'license'
		Purpose:
			What happens when we send wrong type as the field (this case - array of strings and arrays)
		Sent:
			Array with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_array'
		sent_resource['license'] = ['a','b','c',['d']]

		expected_response = {
			'license': [
				"Invalid value: [u'a', u'b', u'c', [u'd']]."
			]
		}

		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_license_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_license_dict(self):
		"""Sending dictionary as 'license'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_dict'
		sent_resource['license'] = {'a':'b','c':[1,2,3]}

		expected_response = {
			'license': [
				"Invalid value: {u'a': u'b', u'c': [1, 2, 3]}."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_license_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_license_number(self):
		"""Sending number as 'license'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_number'
		sent_resource['license'] = 1234567890

		expected_response = {
			'license': [
				"Invalid value: 1234567890."
			]
		}
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(json.loads(response.content), expected_response)

		expected_response = {
			'detail': 'Not found.'
		}
		
		response = self.client.get('/tool/test_license_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_license_case_sensitive(self):
		"""Sending correct value but with wrong case as 'license'
		Purpose:
			What happens when we send correct value but with incorrect case (apache license 2.0 instead of Apache License 2.0)
		Sent:
			Value with correct string but lowercase (apache license 2.0 instead of Apache License 2.0)
		Expected outcome:
			Resource registered with correct case
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_license_case_sensitive'
		sent_resource['license'] = 'apache license 2.0'
		
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_license_case_sensitive', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_license_case_sensitive'
		expected_resource['license'] = 'Apache License 2.0'

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)
		