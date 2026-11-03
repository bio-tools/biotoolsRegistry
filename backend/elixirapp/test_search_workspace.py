import json
import os
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.http import QueryDict
from django.test import SimpleTestCase, override_settings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
from rest_framework.test import APIClient

from elixir.queries import SEARCH_FACETS, ToolSearchResult, search_tools
from elixirapp.search_workspace import parse_search
from elixirapp.test_html import HTML_REQUEST


class SearchWorkspaceTests(SimpleTestCase):
    def test_option_lookup_limits_fields_and_public_domains(self):
        for query in ('field=owner&q=ab', 'field=creditName&q=x%00', 'field=creditName&q=' + 'a' * 81):
            self.assertEqual(self.client.get('/search/options/?' + query, **HTML_REQUEST).status_code, 400)
        with patch('elixirapp.search_workspace.Domain.objects') as domains:
            domains.filter.return_value.values_list.return_value.distinct.return_value.order_by.return_value = [('public', 'Public domain')]
            response = self.client.get('/search/options/?field=domain', **HTML_REQUEST)
            self.assertEqual(response.json()['items'], [{'value': 'public', 'label': 'Public domain'}])
            domains.filter.assert_called_once_with(visibility=1, is_private=False)
        with patch('elixirapp.search_workspace.Credit.objects') as credits:
            self.assertEqual(self.client.get('/search/options/?field=creditName&q=a', **HTML_REQUEST).json()['items'], [])
            credits.filter.assert_not_called()
            credits.filter.return_value.exclude.return_value.values_list.return_value.distinct.return_value.order_by.return_value = ['Anna']
            response = self.client.get('/search/options/?field=creditName&q=an', **HTML_REQUEST)
            self.assertEqual(response.json()['items'], [{'value': 'Anna', 'label': 'Anna'}])
            credits.filter.assert_called_once_with(resource__visibility=1, name__icontains='an')
        with patch('elixirapp.search_workspace.CollectionID.objects') as collections:
            collections.filter.return_value.exclude.return_value.values_list.return_value.distinct.return_value.order_by.return_value = ['3D-BioInfo']
            response = self.client.get('/search/options/?field=collectionID&q=3D', **HTML_REQUEST)
            self.assertEqual(response.json()['items'], [{'value': '3D-BioInfo', 'label': '3D-BioInfo'}])
            collections.filter.assert_called_once_with(resource__visibility=1, name__icontains='3D')

    def test_validation_is_strict_and_separate_from_legacy(self):
        for query in ('page=0', 'page=-1', 'page=1.5', 'page=nan', 'page=10001',
                      'per_page=0', 'per_page=101', 'per_page=bad', 'page=101&per_page=100',
                      'sort=unknown', 'ord=up', 'unknown=x', 'topic=%5C',
                      'topic=%00', 'q=' + 'x' * 257):
            with self.subTest(query=query), patch('elixirapp.search_workspace.search_tools') as search:
                response = self.client.get('/search/data/?' + query, **HTML_REQUEST)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()['error']['code'], 'invalid_search')
                search.assert_not_called()
        for size in (10, 25, 50, 100):
            self.assertEqual(parse_search(QueryDict(f'per_page={size}'))['per_page'], size)

    def test_page_safe_configuration_and_no_htmx_in_workspace(self):
        with patch('elixirapp.search_workspace.search_tools', return_value=ToolSearchResult([], 0, 1, 50, 1, 1)):
            response = self.client.get('/search/?q=%3Cscript%3E', **HTML_REQUEST)
        self.assertContains(response, 'data-vue-island="search-workspace"')
        self.assertContains(response, 'data-vue-props="search-config" hx-disable')
        self.assertContains(response, '<template id="search-config">')
        self.assertNotContains(response, 'hx-target')
        self.assertEqual(self.client.post('/search/data/', **HTML_REQUEST).status_code, 405)

    def test_compact_response_and_backend_errors(self):
        item = {'biotoolsID': 'example', 'name': '<script>Example</script>', 'description': 'x' * 1000,
                'toolType': ['Command-line tool'], 'publication': [{'secret': 'not-in-summary'}]}
        result = ToolSearchResult([item], 21, 2, 10, 1, 3.25, {
            'toolType': {'buckets': [{'key': 'Command-line tool', 'doc_count': 21}]}})
        with patch('elixirapp.search_workspace.search_tools', return_value=result) as search:
            response = self.client.get('/search/data/?page=2&per_page=10', **HTML_REQUEST)
        body = response.json()
        self.assertEqual(body['pagination'], {'page': 2, 'perPage': 10, 'pages': 3,
                         'previous': 1, 'next': 3, 'limited': False})
        self.assertEqual(len(body['items'][0]['description']), 400)
        self.assertNotIn('publication', body['items'][0])
        self.assertIn('/tool/example/', body['items'][0]['url'])
        self.assertEqual(body['facets']['toolType']['values'][0]['count'], 21)
        self.assertEqual(response['Server-Timing'], 'search;dur=3.25')
        self.assertTrue(search.call_args.kwargs['workspace'])
        for failure in (TimeoutError(), ConnectionError('N/A', 'offline', None)):
            with patch('elixirapp.search_workspace.search_tools', side_effect=failure), \
                    self.assertLogs('elixirapp.search_workspace', level='ERROR'):
                response = self.client.get('/search/data/', **HTML_REQUEST)
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()['error']['code'], 'search_unavailable')


@skipUnless(os.environ.get('BIOTOOLS_TEST_QUERY_ES') == '1', 'Requires disposable Elasticsearch')
class LiveWorkspaceTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
        cls.addClassCleanup(cls.es.close)
        cls.index = 'workspace-contract-' + uuid4().hex
        raw = {'type': 'text', 'analyzer': 'whole', 'fielddata': True,
               'fields': {'raw': {'type': 'keyword'}, 'keyword': {'type': 'keyword'}}}
        cls.es.indices.create(index=cls.index, body={
            'settings': {'number_of_shards': 2, 'number_of_replicas': 0,
                         'analysis': {'analyzer': {'whole': {'tokenizer': 'keyword', 'filter': 'lowercase'}}}},
            'mappings': {'dynamic_templates': [{'strings': {'match_mapping_type': 'string', 'mapping': raw}}],
                         'properties': {'description': {'type': 'text', 'analyzer': 'english'},
                                        'additionDate': {'type': 'date'}, 'lastUpdate': {'type': 'date'},
                                        'publication': {'properties': {'metadata': {'properties': {
                                            'date': {'type': 'date'}, 'citationCount': {'type': 'long'}}}}}}}})
        cls.addClassCleanup(cls.es.indices.delete, index=cls.index)
        override = override_settings(ELASTIC_SEARCH_INDEX=cls.index)
        override.enable()
        cls.addClassCleanup(override.disable)
        for i in range(125):
            doc = {'biotoolsID': f'workspace-{i:03}', 'name': f'Workspace {i:03}',
                   'description': 'Sequence alignment fixture.',
                   'toolType': ['Command-line tool' if i % 2 else 'Web application'],
                   'topic': [{'term': 'Sequence analysis'}],
                   'function': [{'operation': [{'term': 'Alignment'}],
                                 'input': [{'data': {'term': 'Sequence'}, 'format': [{'term': 'Sequence'}, {'term': 'FASTA'}]}],
                                 'output': [{'data': {'term': 'Alignment'}, 'format': [{'term': 'ClustalW'}]}]}],
                   'language': ['Python'], 'accessibility': 'Open access', 'cost': 'Free of charge',
                   'license': 'MIT', 'credit': [{'name': 'Example Team'}], 'collectionID': ['Test collection'],
                   'publication': [{'metadata': {'date': f'2026-03-{i % 28 + 1:02}', 'citationCount': i}}],
                   'additionDate': '2026-01-01', 'lastUpdate': f'2026-02-{i % 28 + 1:02}'}
            cls.es.index(index=cls.index, id=doc['biotoolsID'], body=doc)
        cls.es.indices.refresh(index=cls.index)

    def test_parity_for_every_primary_filter_and_order(self):
        samples = {'toolType': 'Command-line tool', 'topic': 'Sequence analysis', 'operation': 'Alignment',
                   'input': 'FASTA', 'output': 'ClustalW', 'language': 'Python', 'accessibility': 'Open access',
                   'cost': 'Free of charge', 'license': 'MIT', 'credit': 'Example Team',
                   'collectionID': 'Test collection', 'name': 'Workspace 010'}
        queries = [{}, {'q': 'unmatchable'}, {'q': '"Workspace 010"'},
                   *[{key: f'"{value}"'} for key, value in samples.items()],
                   *[{'sort': sort, 'ord': order} for sort in ('name', 'score', 'lastUpdate', 'additionDate', 'citationCount', 'citationDate')
                     for order in ('asc', 'desc')]]
        for params in queries:
            with self.subTest(params=params):
                # Give both callers a deterministic primary sort for tied fixture dates.
                params.setdefault('sort', 'name')
                legacy = search_tools(params, page=1, per_page=50)
                response = self.client.get('/search/data/', params, **HTML_REQUEST)
                self.assertEqual(response.status_code, 200, response.content)
                body = response.json()
                self.assertEqual(body['count'], legacy.count)
                if params['sort'] in ('name', 'citationCount'):
                    self.assertEqual([item['id'] for item in body['items']], [item['biotoolsID'] for item in legacy.items])

    def test_exact_facets_bounds_dates_and_pages(self):
        with patch('elixir.queries.es.search', wraps=self.es.search) as calls:
            response = self.client.get('/search/data/?per_page=10&sort=name&ord=asc', **HTML_REQUEST)
        body = response.json()
        self.assertEqual(calls.call_count, 1)
        self.assertEqual(body['count'], 125)
        self.assertEqual(len(body['items']), 10)
        self.assertEqual(body['items'][0]['id'], 'workspace-000')
        self.assertEqual(body['items'][0]['added'], '2026-01-01')
        self.assertEqual(body['pagination']['pages'], 13)
        self.assertEqual(set(body['facets']), set(SEARCH_FACETS))
        inputs = {item['value']: item['count'] for item in body['facets']['input']['values']}
        self.assertEqual(inputs, {'FASTA': 125, 'Sequence': 125})
        self.assertEqual(len(body['facets']['name']['values']), 30)
        self.assertTrue(body['facets']['name']['truncated'])
        for size in (10, 25, 50, 100):
            result = self.client.get(f'/search/data/?per_page={size}', **HTML_REQUEST).json()
            self.assertEqual(len(result['items']), size)
            self.assertEqual(result['candidates'], {'scope': 'candidate', 'size': size, 'limit': 100, 'complete': False})
        last = self.client.get('/search/data/?per_page=10&page=13&sort=name&ord=asc', **HTML_REQUEST).json()
        self.assertEqual(len(last['items']), 5)
        self.assertIsNone(last['pagination']['next'])
        self.assertEqual(self.client.get('/search/data/?per_page=10&page=14', **HTML_REQUEST).status_code, 400)
        filtered = self.client.get('/search/data/', {'toolType': '"Command-line tool"'}, **HTML_REQUEST).json()
        self.assertEqual(filtered['count'], 62)
        self.assertEqual(filtered['facets']['input']['values'][0]['count'], 62)
        # Public DTO still has full source fields and its original envelope.
        with patch('elixir.elixir_logging.SearchLogger.commit'):
            public = APIClient().get('/t/?per_page=10', HTTP_ACCEPT='application/json').json()
        self.assertEqual(set(public), {'list', 'count', 'next', 'previous'})
        self.assertIn('function', public['list'][0])

    def test_advanced_promotion_recomputes_pages_and_bounds(self):
        condition = {'scope': 'server', 'type': 'categorical', 'field': 'toolType', 'values': ['Command-line tool']}
        for page, size in ((1, 10), (7, 2)):
            response = self.client.get('/search/data/', {'advanced': json.dumps([condition]),
                                       'page': page, 'per_page': 10}, **HTML_REQUEST)
            body = response.json()
            self.assertEqual(body['count'], 62)
            self.assertEqual(body['pagination']['pages'], 7)
            self.assertEqual(len(body['items']), size)
            self.assertFalse(body['candidates']['complete'])
            self.assertEqual(body['facets']['toolType']['values'], [{'value': 'Command-line tool', 'count': 62}])

    def test_performance_sample(self):
        measurements = []
        advanced = json.dumps([{'scope': 'server', 'type': 'categorical', 'field': 'toolType',
                                'values': ['Command-line tool']}])
        for params in ({}, {'q': 'sequence'}, {'toolType': '"Command-line tool"'}, {'q': 'unmatchable'},
                       {'per_page': 100}, {'per_page': 100, 'advanced': advanced}):
            sizes, durations = [], []
            for _ in range(3):
                with patch('elixir.queries.es.search', wraps=self.es.search) as calls:
                    response = self.client.get('/search/data/', params, **HTML_REQUEST)
                self.assertEqual(calls.call_count, 1)
                self.assertEqual(response.status_code, 200)
                self.assertLessEqual(len(response.json()['items']), 100)
                sizes.append(len(response.content))
                durations.append(float(response['Server-Timing'].split('=')[1]))
            measurements.append({'params': params, 'bytes': max(sizes), 'median_ms': sorted(durations)[1]})
        print('WORKSPACE_MEASUREMENTS ' + json.dumps(measurements))
