from django.core.management.base import BaseCommand, CommandError
from elasticsearch import Elasticsearch
from elixir.models import *
from elixir.serializers import *
import random, time
from multiprocessing import Pool, cpu_count
from rest_framework.renderers import JSONRenderer

def parallel_function(x):
	resource = ResourceSerializer(Resource.objects.get(id=x[0]), many=False).data
	return JSONRenderer().render(resource)

class Command(BaseCommand):
	help = 'Regenerate the Elasticsearch index'

	def handle(self, *args, **options):
		self.stdout.write('Regenerating the ES')
		es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
		resourceList = Resource.objects.filter(visibility=1)
		self.stdout.write('--------------------\nid\t:\tname\n--------------------')
		# if sending with curl you need to wrap the object below -> {"mappings": object}
		mapping_subdomains = {
			"subdomains": {
				"properties": {
					"domain": {
						"type": "string",
						"fields": {
							"raw": {
								"type": "string",
								"index": "not_analyzed"
							}
						}
					},
					"resources": {
						"properties": {
							"textId": {
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
			}
		}
	
		es.indices.create('elixir', ignore=400)
		time.sleep(3)

		# ADD SETTINGS
		settings = {
			"analysis": {
				"analyzer": {
					"not_analyzed_case_insensitive":{
						"tokenizer":"keyword",
						"filter":"lowercase"
					}
				}
			},
			"index": {
				"max_result_window": 50000
			}
		}
		es.indices.close (index='elixir')
		es.indices.put_settings (index='elixir', body=settings)
		es.indices.open (index='elixir')

		# ADD MAPPING
		mapping = {
			"tool" : {
				"properties" : {
					"collectionID" : {
						"type" : "text",
						"analyzer": "not_analyzed_case_insensitive",
						"fielddata": True,
						"fields": {
							"raw": { 
								"type":  "keyword"
							}
						}
					},
					"description" : {
						"type" : "text",
						"analyzer": "english",
						"fielddata": True
					},
					"homepage" : {
						"type" : "text",
						"analyzer": "not_analyzed_case_insensitive",
						"fielddata": True
					},
					"name" : {
						"type" : "text",
						"analyzer": "not_analyzed_case_insensitive",
						"fielddata": True,
						"fields": {
							"raw": { 
								"type":  "keyword"
							}
						}
					},
					"topic" : {
						"properties" : {
							"term" : {
								"type" : "text",
								"analyzer": "english",
								"fielddata": True,
								"fields": {
									"raw": { 
										"type":  "keyword"
									}
								}
							}
						}
					},
					"function": {
						"properties": {
							"comment": {
								"type": "text",
								"analyzer": "english",
								"fielddata": True
							},
							"input": {
								"properties": {
									"data": {
										"properties": {
											"term": {
												"type": "text",
												"analyzer": "english",
												"fielddata": True,
												"fields": {
													"raw": { 
														"type" : "text",
														"analyzer": "not_analyzed_case_insensitive",
														"fielddata": True
													}
												}
											}
										}
									},
									"format": {
										"properties": {
											"term": {
												"type": "text",
												"analyzer": "english",
												"fielddata": True,
												"fields": {
													"raw": { 
														"type" : "text",
														"analyzer": "not_analyzed_case_insensitive",
														"fielddata": True
													}
												}
											}
										}
									}
								}
							},
							"output": {
								"properties": {
									"data": {
										"properties": {
											"term": {
												"type": "text",
												"analyzer": "english",
												"fielddata": True,
												"fields": {
													"raw": { 
														"type" : "text",
														"analyzer": "not_analyzed_case_insensitive",
														"fielddata": True
													}
												}
											}
										}
									},
									"format": {
										"properties": {
											"term": {
												"type": "text",
												"analyzer": "english",
												"fielddata": True,
												"fields": {
													"raw": { 
														"type" : "text",
														"analyzer": "not_analyzed_case_insensitive",
														"fielddata": True
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
										"type": "text",
										"analyzer": "english",
										"fielddata": True,
										"fields": {
											"raw": { 
												"type":  "keyword"
											}
										}
									}
								}
							}
						}
					},
					"contact" : {
						"properties" : {
							"name" : {
								"type" : "text",
								"analyzer": "english",
								"fielddata": True
							}
						}
					},
					"credit" : {
						"properties" : {
							"comment" : {
								"type" : "text",
								"analyzer": "english",
								"fielddata": True
							},
							"name" : {
								"type" : "text",
								"analyzer": "english",
								"fielddata": True,
								"fields": {
									"raw": { 
										"type" : "text",
										"analyzer": "not_analyzed_case_insensitive",
										"fielddata": True
									}
								}
							}
						}
					},
					"documentation" : {
						"properties" : {
							"comment" : {
								"type" : "text",
								"analyzer": "english",
								"fielddata": True
							}
						}
					},
					"id" : {
						"type" : "text",
						"analyzer": "not_analyzed_case_insensitive",
						"fielddata": True
					},
					"language" : {
						"type" : "text",
						"fielddata": True,
						"analyzer": "not_analyzed_case_insensitive"
					},
					"license" : {
						"type" : "text",
						"analyzer": "not_analyzed_case_insensitive",
						"fielddata": True
					},
					"operatingSystem" : {
						"type" : "text",
						"analyzer": "not_analyzed_case_insensitive",
						"fielddata": True
					},
					"toolType" : {
						"type" : "text",
						"analyzer": "not_analyzed_case_insensitive",
						"fielddata": True
					},
					"version" : {
						"type" : "text",
						"fielddata": True,
						"analyzer": "not_analyzed_case_insensitive"
					},
					"versionId" : {
						"type" : "text",
						"fielddata": True,
						"analyzer": "not_analyzed_case_insensitive"
					},
					"maturity" : {
						"type" : "text",
						"fielddata": True,
						"analyzer": "not_analyzed_case_insensitive"
					},
					"cost" : {
						"type" : "text",
						"fielddata": True,
						"analyzer": "not_analyzed_case_insensitive"
					},
					"owner" : {
						"type" : "text",
						"fielddata": True,
						"analyzer": "not_analyzed_case_insensitive"
					}
				}
			}
		}
		es.indices.put_mapping(index='elixir', doc_type='tool', body=mapping)

		es.indices.create('domains')
		es.indices.put_mapping(index='domains', doc_type='subdomains', body=mapping_subdomains)

		rl_id = Resource.objects.filter(visibility=1).values_list('id')
		pool = Pool(processes=cpu_count())
		
		res = pool.map_async(parallel_function, rl_id)
		results = res.get(timeout=10000)
		for el in results:
			es.index(index='elixir', doc_type='tool', body=el)

		# for resourceItem in resourceList:
		# 	resource = ResourceSerializer(resourceItem, many=False).data
		# 	self.stdout.write('%s\t:\t%s' % (resource['id'], resource['name']))
		# 	es.index(index='elixir', doc_type='tool', body=resource)


		for domain in Domain.objects.all():
			es.index(index='domains', doc_type='subdomains', body={'domain':domain.name, 'title': domain.title, 'sub_title': domain.sub_title, 'description': domain.description, 'resources': map(lambda x: {'textId': x.textId, 'versionId': x.versionId, 'name': x.name, 'version': x.version}, domain.domainresource_set.all())})
			self.stdout.write('%s'%(domain.name))
