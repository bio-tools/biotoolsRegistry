"""Opt-in Elasticsearch contract checks; only touch a unique temporary index."""
import os
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
