"""Opt-in Elasticsearch contract checks; only touch a unique temporary index."""
import os
from types import SimpleNamespace
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.test import SimpleTestCase, override_settings
from elasticsearch import Elasticsearch
from rest_framework.test import APIClient


@skipUnless(os.environ.get('BIOTOOLS_TEST_QUERY_ES') == '1', 'Requires disposable Elasticsearch')
class LiveSearchContracts(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
        cls.addClassCleanup(cls.es.close)
        index = 'query-contract-' + uuid4().hex
        # Same analyzers and field types as es_regenerate for the exercised fields.
        text_field = {'type': 'text', 'analyzer': 'not_analyzed_case_insensitive',
                      'fielddata': True, 'fields': {'raw': {'type': 'keyword'}}}
        cls.es.indices.create(index=index, body={
            'settings': {'number_of_shards': 1, 'number_of_replicas': 0,
                         'analysis': {'analyzer': {'not_analyzed_case_insensitive': {
                             'tokenizer': 'keyword', 'filter': 'lowercase'}}}},
            'mappings': {'properties': {
                'name': text_field, 'biotoolsID': text_field, 'toolType': text_field,
                'description': {'type': 'text', 'analyzer': 'english', 'fielddata': True},
                'lastUpdate': {'type': 'date'}, 'additionDate': {'type': 'date'}}}})
        cls.addClassCleanup(cls.es.indices.delete, index=index)
        override = override_settings(ELASTIC_SEARCH_INDEX=index)
        override.enable()
        cls.addClassCleanup(override.disable)
        cls.docs = []
        for identifier, name, tool_type, day in (
                ('alpha', 'Alpha aligner', 'Command-line tool', '01'),
                ('beta', 'Beta aligner', 'Command-line tool', '02'),
                ('gamma', 'Gamma viewer', 'Web application', '03')):
            doc = {'biotoolsID': identifier, 'name': name, 'description': 'Sequence analysis.',
                   'toolType': [tool_type], 'lastUpdate': '2026-01-' + day,
                   'additionDate': '2026-01-' + day}
            cls.es.index(index=index, id=identifier, body=doc)
            cls.docs.append(doc)
        cls.es.indices.refresh(index=index)

    def test_real_text_filter_order_pages_and_empty_results(self):
        client = APIClient()
        with patch('elixir.elixir_logging.SearchLogger.commit'):
            for params, ids, count, next_page, previous in (
                    ({}, ['gamma', 'beta', 'alpha'], 3, None, None),
                    ({'q': 'aligner', 'sort': 'name', 'ord': 'asc', 'per_page': 1},
                     ['alpha'], 2, '?page=2', None),
                    ({'q': 'aligner', 'sort': 'name', 'ord': 'asc', 'per_page': 1, 'page': 2},
                     ['beta'], 2, None, '?page=1'),
                    ({'q': 'sequence', 'toolType': '"Command-line tool"', 'sort': 'name'},
                     ['beta', 'alpha'], 2, None, None),
                    ({'q': '"Alpha aligner"'}, ['alpha'], 1, None, None),
                    ({'q': 'unmatchablefixture'}, [], 0, None, None)):
                with self.subTest(params=params):
                    response = client.get('/t/', params, HTTP_ACCEPT='application/json')
                    self.assertEqual(response.status_code, 200)
                    docs = {doc['biotoolsID']: doc for doc in self.docs}
                    self.assertEqual(response.json(), {
                        'list': [docs[identifier] for identifier in ids], 'count': count,
                        'next': next_page, 'previous': previous})
            response = client.get('/t/?page=10', HTTP_ACCEPT='application/json')
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {'detail': 'Invalid page. That page contains no results.'})

    def test_capitalization_does_not_change_relevance(self):
        from elixir.search import construct_es_query
        results = []
        for query in ('Alpha', 'alpha', 'ALPHA'):
            body = construct_es_query({'q': query, 'sort': 'score', 'ord': 'desc'})
            hits = self.es.search(index=settings.ELASTIC_SEARCH_INDEX, body=body)['hits']['hits']
            results.append([(hit['_id'], hit['_score']) for hit in hits])
        self.assertTrue(results[0])
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0], results[2])

    def test_boolean_queries_against_index(self):
        client = APIClient()
        with patch('elixir.elixir_logging.SearchLogger.commit'):
            for query, expected in (
                    ('name:alpha OR name:gamma', {'alpha', 'gamma'}),
                    ('aligner AND NOT name:beta', {'alpha'}),
                    ('name:alpha OR name:beta AND name:gamma', {'alpha'}),
                    ('(name:alpha OR name:beta) AND aligner', {'alpha', 'beta'}),
                    ('name:"Alpha aligner"', {'alpha'})):
                with self.subTest(query=query):
                    response = client.get('/t/', {'qmode': 'boolean', 'q': query}, HTTP_ACCEPT='application/json')
                    self.assertEqual(response.status_code, 200, response.content)
                    self.assertEqual({item['biotoolsID'] for item in response.json()['list']}, expected)

    def test_updated_after_is_strict_timezone_aware_and_preserved_in_pagination(self):
        client = APIClient()
        with patch('elixir.elixir_logging.SearchLogger.commit'):
            for value in ('2026-01-02T00:00:00Z', '2026-01-02T01:00:00+01:00'):
                response = client.get('/t/', {'updatedAfter': value}, HTTP_ACCEPT='application/json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual([item['biotoolsID'] for item in response.json()['list']], ['gamma'])
            response = client.get('/t/', {'updatedAfter': '2025-12-31T00:00:00Z', 'per_page': 1}, HTTP_ACCEPT='application/json')
            self.assertIn('updatedAfter=', response.json()['next'])
            self.assertIn('per_page=1', response.json()['next'])
            next_response = client.get('/t/' + response.json()['next'], HTTP_ACCEPT='application/json')
            self.assertEqual([item['biotoolsID'] for item in next_response.json()['list']], ['beta'])
            for value in ('', '2026-01-02', '2026-01-02T00:00:00', 'not-a-date'):
                self.assertEqual(client.get('/t/', {'updatedAfter': value}, HTTP_ACCEPT='application/json').status_code, 400)

    def test_edam_any_and_narrower_match_real_indexed_uris(self):
        base = 'http://edamontology.org/'
        child = {'data': {'uri': base + 'topic_0080'}, 'children': []}
        parent = {'data': {'uri': base + 'topic_0091'}, 'children': [child]}
        other = {'data': {'uri': base + 'topic_3071'}, 'children': []}
        vocabulary = SimpleNamespace(current={item['data']['uri']: item for item in (parent, child, other)})
        documents = {'edam-one': [child], 'edam-both': [child, other]}
        try:
            for identifier, terms in documents.items():
                self.es.index(index=settings.ELASTIC_SEARCH_INDEX, id=identifier, body={
                    'biotoolsID': identifier, 'name': identifier, 'topic': [{'uri': term['data']['uri']} for term in terms],
                    'lastUpdate': '2026-01-04'})
            self.es.indices.refresh(index=settings.ELASTIC_SEARCH_INDEX)
            client = APIClient()
            with patch('elixir.edam_lookup.EdamVocabulary', return_value=vocabulary), patch('elixir.elixir_logging.SearchLogger.commit'):
                cases = [({'topicID': '"topic_0080" "topic_3071"', 'edamMatch': 'any'}, {'edam-one', 'edam-both'}),
                         ({'topicID': '"topic_0091"', 'edamExpand': 'narrower'}, {'edam-one', 'edam-both'}),
                         ({'topicID': '"topic_0091" "topic_3071"', 'edamExpand': 'narrower'}, {'edam-both'})]
                for params, expected in cases:
                    response = client.get('/t/', params, HTTP_ACCEPT='application/json')
                    self.assertEqual(response.status_code, 200, response.content)
                    self.assertEqual({item['biotoolsID'] for item in response.json()['list']}, expected)
        finally:
            for identifier in documents:
                self.es.delete(index=settings.ELASTIC_SEARCH_INDEX, id=identifier, ignore=[404])
            self.es.indices.refresh(index=settings.ELASTIC_SEARCH_INDEX)
