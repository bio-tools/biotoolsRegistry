"""Full supported-key characterization and native/enhanced search parity."""
import json
import os
from pathlib import Path
from unittest import skipUnless
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import uuid4

from django.conf import settings
from django.http import QueryDict
from django.test import SimpleTestCase, override_settings
from elasticsearch import Elasticsearch

from elixir.queries import ToolSearchResult, search_tools
from elixir.search import construct_es_query
from elixir.search_settings import search_struct
from elixirapp.search_workspace import FILTERS, parse_search, filter_groups
from elixirapp.test_html import HTML_REQUEST
from elixir.resource_ui import resource_descriptor
from elixirapp.search_workspace import summary


FIXTURE = json.loads((Path(__file__).parent / 'tests/data/SearchParity.json').read_text())


class SearchParityTests(SimpleTestCase):
    def test_filter_hierarchy_covers_every_key_once_and_follows_schema_labels(self):
        descriptor = resource_descriptor()
        groups = filter_groups(descriptor)
        nodes = {}

        def visit(group):
            nodes[group['id']] = group
            return group['keys'] + [key for child in group['children'] for key in visit(child)]

        keys = [key for group in groups for key in visit(group)]
        self.assertCountEqual(keys, FILTERS)
        self.assertLessEqual(len(groups), 10)
        self.assertIn('inputDataTypeID', nodes['function.input.data']['keys'])
        self.assertIn('inputID', nodes['function.input']['keys'])
        self.assertIn('dataTypeID', nodes['function']['keys'])
        self.assertIn('creditName', nodes['credit']['keys'])
        self.assertEqual(nodes['registry']['keys'], ['domain'])
        descriptor['contract']['fields']['function']['label'] = 'Changed schema label'
        self.assertEqual(next(node for node in filter_groups(descriptor) if node['id'] == 'function')['label'], 'Changed schema label')

    def test_comparison_includes_only_approved_public_fields(self):
        record = {**FIXTURE['resource'], 'editPermission': {'authors': ['private-person']},
                  'credit': [{'name': 'Visible', 'unapproved': 'secret-value'}]}
        data = summary(record, descriptor=resource_descriptor())['comparison']
        self.assertEqual(data['homepage'], record['homepage'])
        self.assertIn('Visible', data['credit'])
        self.assertNotIn('editPermission', data)
        self.assertNotIn('secret-value', json.dumps(data))

    def test_function_columns_follow_public_schema_children(self):
        descriptor = resource_descriptor()
        record = {**FIXTURE['resource'], 'function': [{'operation': [{'term': 'Align'}],
                    'input': [{'data': {'term': 'Sequence'}}], 'output': [{'data': {'term': 'Alignment'}}]}]}
        data = summary(record, descriptor=descriptor)['comparison']
        self.assertIn('Align', data['function.operation'])
        self.assertIn('Sequence', data['function.input'])
        self.assertIn('Alignment', data['function.output'])
        descriptor['contract']['fields']['function']['item']['fields']['input']['public'] = False
        self.assertNotIn('function.input', summary(record, descriptor=descriptor)['comparison'])

    def test_every_backend_key_has_a_characterized_fixture_and_ui_capability(self):
        self.assertEqual(set(FIXTURE['filters']), set(search_struct))
        self.assertEqual(set(FILTERS), set(search_struct) | {'domain'})
        for key, value in FIXTURE['filters'].items():
            query = QueryDict(urlencode({key: '"' + value + '"'}))
            self.assertEqual(construct_es_query(parse_search(query))['query'], construct_es_query(query)['query'])

    def test_duplicates_empty_values_and_encoded_constraints(self):
        state = parse_search(QueryDict('q=first&q=last&topicID=old&topicID=topic_0121&domain=a&domain=b&page=2&page=1'))
        self.assertEqual((state['q'], state['topicID'], state['domain'], state['page']), ('last', 'topic_0121', 'b', 1))
        self.assertNotIn('domain', parse_search(QueryDict('domain=')))
        self.assertEqual(parse_search(QueryDict('collectionID=%22A+%26+B+%2B+collection%22'))['collectionID'], '"A & B + collection"')

    def test_native_results_errors_and_pagination_keep_constraints(self):
        result = ToolSearchResult([FIXTURE['resource']], 21, 2, 10, 1, 1.5)
        with patch('elixirapp.search_workspace.search_tools', return_value=result) as search:
            response = self.client.get('/search/?domain=managed&topicID=topic_0121&per_page=10&page=2', **HTML_REQUEST)
        self.assertContains(response, 'data-tool-id="parity-alpha"')
        self.assertContains(response, 'domain=managed&amp;topicID=topic_0121&amp;per_page=10&amp;page=3')
        self.assertNotContains(response, '_legacy')
        self.assertEqual(search.call_args.args[0]['domain'], 'managed')
        self.assertContains(response, 'data-filter-group="topic" open')
        self.assertContains(response, 'data-filter-group="function.input.data"')
        self.assertEqual(response.content.count(b'name="inputDataTypeID"'), 1)
        for query in ('unknown=1', 'page=0', 'topic=%00', 'advanced=bad', 'topic=!!!', 'q=%22%22'):
            with patch('elixirapp.search_workspace.search_tools') as search:
                response = self.client.get('/search/?' + query, **HTML_REQUEST)
            self.assertEqual(response.status_code, 400)
            self.assertContains(response, 'role="alert"', status_code=400)
            search.assert_not_called()
        with patch('elixirapp.search_workspace.search_tools', side_effect=TimeoutError), self.assertLogs('elixirapp.search_workspace', level='ERROR'):
            response = self.client.get('/search/?domain=managed', **HTML_REQUEST)
        self.assertContains(response, 'Search is temporarily unavailable', status_code=503)
        self.assertContains(response, '>Retry</a>', status_code=503)
        self.assertNotContains(response, 'No tools found', status_code=503)

    def test_missing_and_partial_domain_membership_never_broaden_workspace(self):
        empty = {'hits': {'total': {'value': 0}, 'hits': []}}
        with patch('elixir.queries.es.search', side_effect=[empty, empty]) as search:
            search_tools({'domain': 'missing'}, page=1, per_page=10, workspace=True)
        self.assertIn({'match_none': {}}, search.call_args.kwargs['body']['query']['bool']['must'])
        with patch('elixir.queries.es.search', return_value={**empty, 'timed_out': True}) as search:
            with self.assertRaises(TimeoutError):
                search_tools({'domain': 'partial'}, page=1, per_page=10, workspace=True)
            self.assertEqual(search.call_count, 1)


@skipUnless(os.environ.get('BIOTOOLS_TEST_QUERY_ES') == '1', 'Requires disposable Elasticsearch')
class LiveSearchParityTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
        cls.addClassCleanup(cls.es.close)
        cls.index = 'search-parity-' + uuid4().hex
        cls.domains = cls.index + '-domains'
        # Copy the deployed mapping, not a permissive synthetic text mapping.
        source = settings.ELASTIC_SEARCH_INDEX
        mapping = cls.es.indices.get_mapping(index=source)[source]['mappings']
        analysis = cls.es.indices.get_settings(index=source)[source]['settings']['index'].get('analysis', {})
        cls.es.indices.create(index=cls.index, body={'mappings': mapping, 'settings': {'analysis': analysis}})
        cls.addClassCleanup(cls.es.indices.delete, index=cls.index)
        cls.es.indices.create(index=cls.domains, body={'mappings': {'properties': {'domain': {
            'type': 'text', 'fields': {'raw': {'type': 'keyword'}}}}}})
        cls.addClassCleanup(cls.es.indices.delete, index=cls.domains)
        override = override_settings(ELASTIC_SEARCH_INDEX=cls.index, ELASTIC_SEARCH_DOMAIN_INDEX=cls.domains)
        override.enable()
        cls.addClassCleanup(override.disable)
        cls.es.index(index=cls.index, id='parity-alpha', body=FIXTURE['resource'])
        cls.es.index(index=cls.index, id='parity-other', body={
            'biotoolsID': 'parity-other', 'name': 'Unrelated', 'description': 'Unrelated resource.',
            'additionDate': '2026-01-01', 'lastUpdate': '2026-01-02'})
        cls.es.index(index=cls.domains, id='managed', body={'domain': 'managed', 'resources': [
            {'biotoolsID': 'PARITY-ALPHA'}, {'biotoolsID': 'parity-alpha'}]})
        cls.es.index(index=cls.domains, id='empty', body={'domain': 'empty', 'resources': []})
        cls.es.indices.refresh(index=cls.index + ',' + cls.domains)

    def test_every_functional_filter_matches_the_public_query_engine(self):
        for key, value in FIXTURE['filters'].items():
            with self.subTest(key=key):
                params = {key: '"' + value + '"', 'sort': 'name', 'ord': 'asc'}
                legacy = search_tools(params, page=1, per_page=10)
                response = self.client.get('/search/data/', params, **HTML_REQUEST)
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(legacy.count, 1, (key, legacy.items))
                self.assertEqual(response.json()['count'], legacy.count)
                self.assertEqual([item['id'] for item in response.json()['items']], ['parity-alpha'])

    def test_native_and_enhanced_domain_intersection_duplicates_and_empty_results(self):
        for query, expected in (
                ('domain=managed', 1), ('domain=managed&name=unmatchablefixture', 0),
                ('domain=empty', 0), ('domain=missing', 0),
                ('topicID=nonexistent&topicID=%22topic_0121%22&domain=managed', 1),
                ('collectionID=%22A+%26+B+%2B+collection%22', 1)):
            with self.subTest(query=query):
                data = self.client.get('/search/data/?' + query, **HTML_REQUEST)
                page = self.client.get('/search/?' + query, **HTML_REQUEST)
                self.assertEqual(data.status_code, 200, data.content)
                self.assertEqual(page.status_code, 200, page.content)
                self.assertEqual(data.json()['count'], expected)
                self.assertEqual(page.context['search_result']['count'], expected)
                self.assertEqual(page.context['search_result']['items'], data.json()['items'])

    def test_comparison_uses_the_same_filtered_bounded_result_set(self):
        response = self.client.get('/search/data/?domain=managed&view=table', **HTML_REQUEST)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['count'], 1)
        self.assertIn('Sequence alignment', response.json()['items'][0]['comparison']['function'])
        page = self.client.get('/search/?domain=managed&view=table', **HTML_REQUEST)
        self.assertContains(page, 'Tool results table')
        self.assertContains(page, 'Sequence alignment')
