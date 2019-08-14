from rest_framework import status
from elixir.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import emptyInputTool, emptyOutputTool
import json

class TestTopic(BaseTestObject):
	"""General structure for the EDAM tests:
	============================	======	======
									URI 	Term
	============================	======	======
	present, correct				x
											x
									x		x
	present, obsolete 				x
											x
									x		x
	present, incorrect 				x
											x
									x		x
	present, mismatch 				x		x
	2 present, correct 				x		x
	2 present, 1 incorrect 			x		x
	============================	======	======
	It doesn't matter if the term is OK or not (e.g. obsolete) if it doesn't match a correct URI.
	"""
	
	def test_Topic_Pass_URI_only(self):
		"""Sending as 'topic': correct URI
		Purpose:
			Sending correct URI
		Sent:
			Correct URI
		Expected outcome:
			Resource registered - URI resolves to a concept, term filled in
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Topic_Pass_URI_only'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070'
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_Topic_Pass_URI_only', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_Topic_Pass_URI_only'
		expected_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Biology'
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_Topic_Pass_term_only(self):
		"""Sending as 'topic': correct term
		Purpose:
			Sending correct term
		Sent:
			Correct term
		Expected outcome:
			Resource registered - term resolves to a concept, URI filled in
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Topic_Pass_term_only'
		sent_resource['topic'] = [
			{
				'term': 'Biology'
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_Topic_Pass_term_only', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_Topic_Pass_term_only'
		expected_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Biology'
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_Topic_Pass_URI_term(self):
		"""Sending as 'topic': correct URI and term
		Purpose:
			Sending correct URI and term
		Sent:
			Correct URI and term
		Expected outcome:
			Resource registered - URI and term resolves to a concept
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Topic_Pass_URI_term'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Biology'
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_Topic_Pass_URI_term', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_Topic_Pass_URI_term'
		expected_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Biology'
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_Obsolete_Topic_URI(self):
		"""Sending as 'topic': obsolete URI
		Purpose:
			Sending obsolete URI to get an error
		Sent:
			Obsolete URI
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_Topic_URI'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_0748'
			}
		]

		expected_response = {
			'topic': [
				{
					'general_errors': [
						'Invalid URI: http://edamontology.org/topic_0748.'
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
		
		response = self.client.get('/tool/test_Obsolete_Topic_URI')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Obsolete_Topic_term(self):
		"""Sending as 'topic': obsolete term
		Purpose:
			Sending obsolete term to get an error
		Sent:
			Obsolete term
		Expected outcome:
			Error returned, term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_Topic_term'
		sent_resource['topic'] = [
			{
				'term': 'Protein sites and features'
			}
		]

		expected_response = {
			'topic': [
				{
					'general_errors': [
						'Invalid term: Protein sites and features.'
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
		
		response = self.client.get('/tool/test_Obsolete_Topic_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Obsolete_Topic_URI_term(self):
		"""Sending as 'topic': obsolete URI and term
		Purpose:
			Sending obsolete URI and term to get an error
		Sent:
			Obsolete URI and term
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Obsolete_Topic_URI_term'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_0748',
				'term': 'Protein sites and features'
			}
		]

		expected_response = {
			'topic': [
				{
					'general_errors': [
						'Invalid URI: http://edamontology.org/topic_0748.'
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
		
		response = self.client.get('/tool/test_Obsolete_Topic_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_Topic_URI(self):
		"""Sending as 'topic': incorrect URI
		Purpose:
			Sending incorrect URI to get an error
		Sent:
			Obsolete URI
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_Topic_URI'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_invalid'
			}
		]

		expected_response = {
			'topic': [
				{
					'general_errors': [
						'Invalid URI: http://edamontology.org/topic_invalid.'
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
		
		response = self.client.get('/tool/test_incorrect_Topic_URI')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_Topic_term(self):
		"""Sending as 'topic': invalid term
		Purpose:
			Sending invalid term to get an error
		Sent:
			Obsolete term
		Expected outcome:
			Error returned, term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_Topic_term'
		sent_resource['topic'] = [
			{
				'term': 'Incorrect topic'
			}
		]

		expected_response = {
			'topic': [
				{
					'general_errors': [
						'Invalid term: Incorrect topic.'
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
		
		response = self.client.get('/tool/test_incorrect_Topic_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_incorrect_Topic_URI_term(self):
		"""Sending as 'topic': incorrect URI and term
		Purpose:
			Sending incorrect URI and term to get an error
		Sent:
			Obsolete URI and term
		Expected outcome:
			Error returned, URI and term is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_incorrect_Topic_URI_term'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_invalid',
				'term': 'Incorrect topic'
			}
		]

		expected_response = {
			'topic': [
				{
					'general_errors': [
						'Invalid URI: http://edamontology.org/topic_invalid.'
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
		
		response = self.client.get('/tool/test_incorrect_Topic_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_mismatch_correct_Topic_URI_term(self):
		"""Sending as 'topic': mismatched URI and term
		Purpose:
			Sending correct URI with mismatched term
		Sent:
			Correct, but mismatched URI/term pair
		Expected outcome:
			Error returned, term does not match the URI
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_mismatch_correct_Topic_URI_term'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Unicellular eukaryotes'
			}
		]

		expected_response = {
			'topic': [
				{
					'general_errors': [
						'The term does not match the URI: Unicellular eukaryotes, http://edamontology.org/topic_3070.'
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
		
		response = self.client.get('/tool/test_mismatch_correct_Topic_URI_term')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_Topic_Pass_2_topics(self):
		"""Sending as 'topic': 2 objects
		Purpose:
			Sending 2 topic objects to test if saving multiple topics works
		Sent:
			2 correct URI/term pairs
		Expected outcome:
			Resource registered with 2 topics
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Topic_Pass_2_topics'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Biology'
			},
			{
				'uri': 'http://edamontology.org/topic_2821',
				'term': 'Unicellular eukaryotes'
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_Topic_Pass_2_topics', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_Topic_Pass_2_topics'
		expected_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Biology'
			},
			{
				'uri': 'http://edamontology.org/topic_2821',
				'term': 'Unicellular eukaryotes'
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)


	def test_Topic_2_topics_incorrect(self):
		"""Sending as 'topic': 2 objects, one has incorrect URI
		Purpose:
			Sending 2 topics with 1 being incorrect to test if catching error works for multiple objects
		Sent:
			Array of 2 topics, 1 incorrect
		Expected outcome:
			Error returned, URI is invalid
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_Topic_2_topics_incorrect'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Biology'
			},
			{
				'uri': 'http://edamontology.org/invalid',
				'term': 'Unicellular eukaryotes'
			}
		]
		
		expected_response = {
			'topic': [
				{},
				{
					'general_errors': [
						'Invalid URI: http://edamontology.org/invalid.'
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
		
		response = self.client.get('/tool/test_Topic_2_topics_incorrect')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_topic_string(self):
		"""Sending as 'topic': string
		Purpose:
			What happens when we send wrong type as the field (this case - string)
		Sent:
			String as topic
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_topic_string'
		sent_resource['topic'] = 'just a string'

		expected_response = {
			'topic': {
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
		
		response = self.client.get('/tool/test_topic_string')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_topic_dict(self):
		"""Sending dictionary as 'topic'
		Purpose:
			What happens when we send wrong type as the field (this case - dict of mixed types)
		Sent:
			Dictionary with mixed types (strings and arrays)
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_topic_dict'
		sent_resource['topic'] = {'a':'b','c':[1,2,3]}

		expected_response = {
			'topic': {
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
		
		response = self.client.get('/tool/test_topic_dict')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_topic_number(self):
		"""Sending number as 'topic'
		Purpose:
			What happens when we send wrong type as the field (this case - number)
		Sent:
			Number
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_topic_number'
		sent_resource['topic'] = 1234567890
		
		expected_response = {
			'topic': {
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
		
		response = self.client.get('/tool/test_topic_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_topic_array_number(self):
		"""Sending array of numbers as 'topic'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of numbers
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_topic_array_number'
		sent_resource['topic'] = [1]

		expected_response = {
			'topic': [
				{
					'general_errors': [
						'Invalid data. Expected a dictionary, but got int.'
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
		
		response = self.client.get('/tool/test_topic_array_number')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_topic_array_array(self):
		"""Sending array of arrays as 'topic'
		Purpose:
			What happens when we send wrong type as the field (this case - array of numbers)
		Sent:
			Array of arrays of mixed types
		Expected outcome:
			Error informing about incorrect value
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_topic_array_array'
		sent_resource['topic'] = [[2,3],'7']
		
		expected_response = {
			'topic': [
				{
					'general_errors': [
						'Invalid data. Expected a dictionary, but got list.'
					]
				},
				{
					'general_errors': [
						'Invalid data. Expected a dictionary, but got unicode.'
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
		
		response = self.client.get('/tool/test_topic_array_array')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


	def test_topic_extra_fields(self):
		"""Sending array of dicts with extra fields as 'topic'
		Purpose:
			What happens when we send wrong type as the field (this case - add some fields to the object)
		Sent:
			Array of arrays of mixed types
		Expected outcome:
			Resource is registered, extra fields are ignored.
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_topic_extra_fields'
		sent_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'some': 'field'
			}
		]
		response = self.client.post('/tool/', sent_resource, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		response = self.client.get('/tool/test_topic_extra_fields', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_resource = emptyOutputTool()

		expected_resource['id'] = 'test_topic_extra_fields'
		expected_resource['topic'] = [
			{
				'uri': 'http://edamontology.org/topic_3070',
				'term': 'Biology'
			}
		]

		received_resource = json.loads(response.content)
		received_resource['additionDate'] = None
		received_resource['lastUpdate'] = None

		self.assertEqual(expected_resource, received_resource)

	def test_topic_empty_zero_length(self):
		"""Sending empty array as 'topic'
		Purpose:
			What happens when we send empty array
		Sent:
			[]
		Expected outcome:
			Error informing that this field cannot be empty
		"""
		sent_resource = emptyInputTool()
		sent_resource['id'] = 'test_topic_empty_zero_length'
		sent_resource['topic'] = []

		expected_response = {
			'topic': {
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
		
		response = self.client.get('/tool/test_topic_empty_zero_length')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(json.loads(response.content), expected_response)


