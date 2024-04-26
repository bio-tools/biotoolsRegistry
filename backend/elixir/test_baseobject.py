from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework.authtoken.models import Token
from elixir.views import Ontology, User
from django.conf import settings
import json, os
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as ESExceptions

"""
IMPORTANT: When writing tests, set 'additionUpdate' and 'lastUpdate' to None! (or figure out a way to calculate the timestamps that the database will generate)
"""

class BaseTestObject(APITestCase):

	# initial setup of the test environment (loading the Ontology from file, etc)
	def setUp(self):

		settings.ELASTIC_SEARCH_INDEX = 'test'
		self.maxDiff = None
		self.factory = APIRequestFactory()
		self.client = APIClient()
		self.user = User.objects.create_user('test_user', password='test_user_password', email='dupa@example.com')
		self.user.save()
		token = Token.objects.create(user=self.user)
		token.save()
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		self.client.login(username='test_user', password='test_user_password')

		es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
		try:
			resp = es.indices.delete(index=settings.ELASTIC_SEARCH_INDEX)
		except ESExceptions.TransportError as TE:
			if TE.status_code == 404:
				do_nothing = True
			else:
				raise TE
		mapping = {
			"tool": {
				"properties": {
					"accessibility": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"additionDate": {
						"type": "date",
						"format": "strict_date_optional_time||epoch_millis"
					},
					"collection": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"contact": {
						"properties": {
							"contactEmail": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"contactName": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"contactTel": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"contactURL": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"cost": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"credit": {
						"properties": {
							"creditComment": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"creditEmail": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"creditGridId": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"creditName": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"creditOrcidId": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"creditTypeEntity": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"creditTypeRole": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"creditURL": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"description": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"documentation": {
						"properties": {
							"documentationComment": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"documentationType": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"documentationUrl": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"download": {
						"properties": {
							"downloadComment": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"downloadType": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"downloadUrl": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"editPermission": {
						"properties": {
							"type": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"elixirInfo": {
						"properties": {
							"elixirNode": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"elixirStatus": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"function": {
						"properties": {
							"functionComment": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"functionHandle": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"input": {
								"properties": {
									"dataFormat": {
										"properties": {
											"term": {
												"type": "string",
												"fields": {
													"raw": {
														"type": "string",
														"index": "not_analyzed"
													}
												}
											},
											"uri": {
												"type": "string",
												"fields": {
													"raw": {
														"type": "string",
														"index": "not_analyzed"
													}
												}
											}
										}
									},
									"dataHandle": {
										"type": "string",
										"fields": {
											"raw": {
												"type": "string",
												"index": "not_analyzed"
											}
										}
									},
									"dataType": {
										"properties": {
											"term": {
												"type": "string",
												"fields": {
													"raw": {
														"type": "string",
														"index": "not_analyzed"
													}
												}
											},
											"uri": {
												"type": "string",
												"fields": {
													"raw": {
														"type": "string",
														"index": "not_analyzed"
													}
												}
											}
										}
									}
								}
							},
							"operation": {
								"properties": {
									"term": {
										"type": "string",
										"fields": {
											"raw": {
												"type": "string",
												"index": "not_analyzed"
											}
										}
									},
									"uri": {
										"type": "string",
										"fields": {
											"raw": {
												"type": "string",
												"index": "not_analyzed"
											}
										}
									}
								}
							},
							"output": {
								"properties": {
									"dataFormat": {
										"properties": {
											"term": {
												"type": "string",
												"fields": {
													"raw": {
														"type": "string",
														"index": "not_analyzed"
													}
												}
											},
											"uri": {
												"type": "string",
												"fields": {
													"raw": {
														"type": "string",
														"index": "not_analyzed"
													}
												}
											}
										}
									},
									"dataHandle": {
										"type": "string",
										"fields": {
											"raw": {
												"type": "string",
												"index": "not_analyzed"
											}
										}
									},
									"dataType": {
										"properties": {
											"term": {
												"type": "string",
												"fields": {
													"raw": {
														"type": "string",
														"index": "not_analyzed"
													}
												}
											},
											"uri": {
												"type": "string",
												"fields": {
													"raw": {
														"type": "string",
														"index": "not_analyzed"
													}
												}
											}
										}
									}
								}
							}
						}
					},
					"homepage": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"id": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"language": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"lastUpdate": {
						"type": "date",
						"format": "strict_date_optional_time||epoch_millis"
					},
					"latest": {
						"type": "long"
					},
					"license": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"link": {
						"properties": {
							"linkComment": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"linkType": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"linkUrl": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"maturity": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"mirror": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"name": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"operatingSystem": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"owner": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"publication": {
						"properties": {
							"publicationDoi": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"publicationPmcid": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"publicationPmid": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"publicationType": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"toolType": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"topic": {
						"properties": {
							"term": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"uri": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"uses": {
						"properties": {
							"usesHomepage": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"usesName": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							},
							"usesVersion": {
								"type": "string",
								"fields": {
									"raw": {
										"type": "string",
										"index": "not_analyzed"
									}
								}
							}
						}
					},
					"version": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"versionId": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					}
				}
			}
		}
	
		es.indices.create(settings.ELASTIC_SEARCH_INDEX)
		es.indices.put_mapping(index=settings.ELASTIC_SEARCH_INDEX, doc_type='tool', body=mapping)
		path_data = '/elixir/application/backend/data'
		path_edam = path_data + '/edam/json/current'
		
		with open(path_edam + '/EDAM_Topic.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='EDAM_Topic', data=json.dumps(o))
		with open(path_edam + '/flat_EDAM_Topic.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='flat_EDAM_Topic', data=json.dumps(o))
		
		with open(path_edam + '/EDAM_Format.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='EDAM_Format', data=json.dumps(o))
		with open(path_edam + '/flat_EDAM_Format.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='flat_EDAM_Format', data=json.dumps(o))
		
		with open(path_edam + '/EDAM_Data.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='EDAM_Data', data=json.dumps(o))
		with open(path_edam + '/flat_EDAM_Data.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='flat_EDAM_Data', data=json.dumps(o))
		
		with open(path_edam + '/EDAM_Operation.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='EDAM_Operation', data=json.dumps(o))
		with open(path_edam + '/flat_EDAM_Operation.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='flat_EDAM_Operation', data=json.dumps(o))
		
		with open(path_edam + '/EDAM_obsolete.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='EDAM_obsolete', data=json.dumps(o))
		with open(path_edam + '/flat_EDAM_obsolete.json') as f:
			o = json.load(f)
			Ontology.objects.create(name='flat_EDAM_obsolete', data=json.dumps(o))
		

	def tearDown(self):
		es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
		try:
			resp = es.indices.delete(index='test')
		except ESExceptions.TransportError as TE:
			if TE.status_code == 404:
				do_nothing = True
			else:
				raise TE
		settings.ELASTIC_SEARCH_INDEX = 'elixir'
		
