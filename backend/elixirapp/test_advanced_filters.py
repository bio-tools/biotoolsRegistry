import json
import os
from pathlib import Path
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from elasticsearch import Elasticsearch

from elixir.advanced_filters import filter_values, parse_filters
from elixirapp.test_html import HTML_REQUEST
from elixirapp.test_edam import seed_ontology


FIXTURE = json.loads((Path(__file__).parent / 'tests/data/AdvancedSearch.json').read_text())


@override_settings(SEARCH_WORKSPACE_SCORES=[FIXTURE['score']])
class AdvancedValidationTests(SimpleTestCase):
    def test_rejects_untrusted_fields_operators_bounds_and_score_versions(self):
        base = {'scope': 'server', 'type': 'range', 'field': 'added', 'min': '2026-01-01'}
        invalid = [None, {}, [None], [1], 'expression',
                   [dict(base, field='_id')], [dict(base, scope='candidate')],
                   [dict(base, type='script')], [dict(base, operator='eval')],
                   [dict(base, min='2026-02-30')], [dict(base, min='0000-01-01')],
                   [dict(base, min='9999-12-31')], [dict(base, min=1)], [dict(base, max='2025-01-01')],
                   [dict(base, field=[])], [dict(base, type=[])], [base] * 9,
                   [{'scope': 'server', 'type': 'boolean', 'field': 'hasPublication', 'value': 1}],
                   [{'scope': 'server', 'type': 'categorical', 'field': 'toolType', 'values': []}],
                   [{'scope': 'server', 'type': 'ontology', 'field': 'topic', 'values': ['javascript:alert(1)']}],
                   [{'scope': 'server', 'type': 'score', 'field': 'fixtureQuality', 'version': 'old', 'min': 0.5}],
                   [{'scope': 'server', 'type': 'score', 'field': 'fixtureQuality', 'version': 'fixture-v1', 'min': True}],
                   [{'scope': 'server', 'type': 'score', 'field': 'fixtureQuality', 'version': 'fixture-v1', 'min': 2}],
                   [{'scope': 'server', 'type': 'score', 'field': 'undeclared', 'version': 'v1', 'min': 0}]]
        for raw in [*[json.dumps(value) for value in invalid], '[', ' ' * 4097, '[' * 1100]:
            with self.subTest(raw=raw[:150]), patch('elixirapp.search_workspace.search_tools') as search:
                response = self.client.get('/search/data/', {'advanced': raw}, **HTML_REQUEST)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(response.json()['error']['field'], 'advanced')
                search.assert_not_called()

    def test_fixture_contract_and_canonical_values(self):
        for case in FIXTURE['cases']:
            self.assertEqual(parse_filters(json.dumps([case['filter']]))[0], case['filter'])
        condition = {'scope': 'server', 'type': 'categorical', 'field': 'toolType', 'values': ['B', 'A', 'B']}
        self.assertEqual(parse_filters(json.dumps([condition]))[0]['values'], ['A', 'B'])
        with override_settings(SEARCH_WORKSPACE_SCORES=[]):
            with self.assertRaises(ValueError):
                parse_filters(json.dumps([FIXTURE['cases'][-1]['filter']]))
        # Presentation truncation must not change local filtering semantics.
        self.assertEqual(len(filter_values(FIXTURE['items'][3])['toolType']), 5)


@skipUnless(os.environ.get('BIOTOOLS_TEST_QUERY_ES') == '1', 'Requires disposable Elasticsearch')
class LiveAdvancedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_ontology()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
        cls.addClassCleanup(cls.es.close)
        cls.index = 'advanced-contract-' + uuid4().hex
        raw = {'type': 'text', 'fielddata': True,
               'fields': {'raw': {'type': 'keyword'}, 'keyword': {'type': 'keyword'}}}
        cls.es.indices.create(index=cls.index, body={
            'settings': {'number_of_shards': 2, 'number_of_replicas': 0},
            'mappings': {'dynamic_templates': [{'strings': {'match_mapping_type': 'string', 'mapping': raw}}],
                         'properties': {'additionDate': {'type': 'date'}, 'lastUpdate': {'type': 'date'},
                                        'fixtureQualityV1': {'type': 'double'}}}})
        cls.addClassCleanup(cls.es.indices.delete, index=cls.index)
        override = override_settings(ELASTIC_SEARCH_INDEX=cls.index, SEARCH_WORKSPACE_SCORES=[FIXTURE['score']])
        override.enable()
        cls.addClassCleanup(override.disable)
        for item in FIXTURE['items']:
            cls.es.index(index=cls.index, id=item['biotoolsID'], body={**item, 'name': item['biotoolsID'],
                         'description': 'Advanced filtering fixture', 'lastUpdate': '2026-02-01'})
        cls.es.indices.refresh(index=cls.index)

    def test_server_and_local_shared_fixture_equivalence(self):
        for case in FIXTURE['cases']:
            with self.subTest(condition=case['filter']), patch('elixir.queries.es.search', wraps=self.es.search) as calls:
                response = self.client.get('/search/data/', {'advanced': json.dumps([case['filter']]),
                                           'sort': 'name', 'ord': 'asc'}, **HTML_REQUEST)
                self.assertEqual(response.status_code, 200, response.content)
                body = response.json()
                self.assertEqual([item['id'] for item in body['items']], case['ids'])
                self.assertEqual(body['count'], len(case['ids']))
                self.assertEqual(body['candidates'], {'scope': 'candidate', 'size': len(case['ids']), 'limit': 100, 'complete': True})
                self.assertEqual(body['scores'][0]['version'], 'fixture-v1')
                self.assertNotIn('field', body['scores'][0])
                self.assertEqual(calls.call_count, 1)
                for item in body['items']:
                    source = next(source for source in FIXTURE['items'] if source['biotoolsID'] == item['id'])
                    self.assertEqual(item['filterValues'], filter_values(source))

    def test_conjunction_facets_empty_results_and_public_api_isolation(self):
        filters = [FIXTURE['cases'][0]['filter'], FIXTURE['cases'][2]['filter']]
        params = {'advanced': json.dumps(filters), 'sort': 'name', 'ord': 'asc'}
        body = self.client.get('/search/data/', params, **HTML_REQUEST).json()
        self.assertEqual(body['count'], 2)
        self.assertEqual(body['pagination']['pages'], 1)
        self.assertIsNone(body['pagination']['next'])
        self.assertEqual(body['facets']['toolType']['values'], [
            {'value': 'Command-line tool', 'count': 1}, {'value': 'Web application', 'count': 1}])
        params['advanced'] = json.dumps(filters + [FIXTURE['cases'][1]['filter']])
        empty = self.client.get('/search/data/', params, **HTML_REQUEST).json()
        self.assertEqual(empty['count'], 0)
        self.assertEqual(empty['facets']['toolType']['values'], [])
        from elixir.queries import search_tools
        public = search_tools({}, page=1, per_page=10)
        self.assertEqual(public.count, 6)
        self.assertIn('publication', public.items[0])
