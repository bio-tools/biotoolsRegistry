"""Public contracts frozen before extracting the develop query services."""
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connection
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from rest_framework.test import APIClient

from elixir.models import Domain, EditPermission, Resource
from elixir.queries import get_tool, search_tools, InvalidQuery, SearchPageNotFound, ToolNotFound


def hits(items, count=None):
    return {'took': 3, 'hits': {'total': {'value': len(items) if count is None else count},
                              'hits': [{'_source': item} for item in items]}}


class ToolReadContracts(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('query-owner')
        cls.other = User.objects.create_user('query-other')
        cls.tool = Resource.objects.create(
            biotoolsID='QueryTool', biotoolsCURIE='biotools:QueryTool', name='Query Tool',
            description='A deterministic query fixture.', homepage='https://example.org/tool',
            owner=cls.owner, editPermission=EditPermission.objects.create(type='private'))
        Resource.objects.create(
            biotoolsID='hidden-tool', owner=cls.owner, visibility=0,
            editPermission=EditPermission.objects.create(type='public'))

    def setUp(self):
        self.client = APIClient()

    def test_detail_aliases_case_and_public_representation(self):
        expected = {
            'name', 'description', 'homepage', 'biotoolsID', 'biotoolsCURIE', 'version',
            'otherID', 'relation', 'function', 'toolType', 'topic', 'operatingSystem',
            'language', 'license', 'collectionID', 'maturity', 'cost', 'accessibility',
            'elixirPlatform', 'elixirNode', 'elixirCommunity', 'link', 'download',
            'documentation', 'publication', 'credit', 'owner', 'additionDate',
            'lastUpdate', 'editPermission', 'validated', 'homepage_status',
            'elixir_badge', 'confidence_flag',
        }
        baseline = None
        for path in ('/t/QueryTool', '/tool/querytool/', '/biotools:QUERYTOOL', '/QueryTool?format=json'):
            with self.subTest(path=path), CaptureQueriesContext(connection) as queries:
                response = self.client.get(path, HTTP_ACCEPT='application/json')
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(set(data), expected)
                self.assertEqual(data['biotoolsID'], 'QueryTool')
                self.assertEqual(data['owner'], 'query-owner')
                self.assertEqual(data['editPermission'], {'type': 'private', 'authors': []})
                self.assertEqual(data['function'], [])
                self.assertNotIn('visibility', data)
                if baseline is None:
                    baseline = data
                self.assertEqual(data, baseline)
            lookups = [q for q in queries if 'FROM `elixir_resource`' in q['sql']]
            self.assertEqual(len(lookups), 1)

    def test_dot_suffix_is_part_of_identifier_in_develop(self):
        response = self.client.get('/QueryTool.json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)

    def test_shared_lookup_returns_model_with_one_query_and_domain_not_found(self):
        with self.assertNumQueries(1):
            tool = get_tool('biotools:QUERYTOOL')
        self.assertIsInstance(tool, Resource)
        self.assertEqual(tool.pk, self.tool.pk)
        for identifier in ('hidden-tool', 'missing-tool'):
            with self.assertNumQueries(1), self.assertRaises(ToolNotFound):
                get_tool(identifier)

    def test_missing_and_hidden_are_identical_even_for_owner(self):
        for user in (None, self.owner, self.other):
            self.client.force_authenticate(user)
            for identifier in ('missing-tool', 'hidden-tool'):
                response = self.client.get('/t/' + identifier, HTTP_ACCEPT='application/json')
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json(), {'detail': 'Not found.'})

    def test_private_edit_permission_does_not_hide_reads_or_allow_other_writers(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/t/QueryTool').status_code, 200)
        self.assertEqual(self.client.put('/t/QueryTool', {}, format='json').status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.put('/t/QueryTool', {}, format='json').status_code, 401)


class DomainReadContracts(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('domain-owner')
        cls.editor = User.objects.create_user('domain-editor')
        cls.other = User.objects.create_user('domain-other')
        cls.admin = User.objects.create_user('domain-admin', is_superuser=True)
        cls.domain = Domain.objects.create(name='managed', owner=cls.owner, is_private=True)
        cls.domain.editors.add(cls.editor, cls.owner)
        Domain.objects.create(name='hidden', owner=cls.owner, visibility=0)

    def test_owner_editor_and_public_listing_representations(self):
        client = APIClient()
        for user, expected in (
                (None, [{'name': 'managed', 'resourcesCount': 0}]),
                (self.admin, [{'name': 'managed', 'resourcesCount': 0}]),
                (self.other, []),
                (self.owner, [{'name': 'managed', 'resourcesCount': 0,
                               'isOwner': True, 'isEditor': True}]),
                (self.editor, [{'name': 'managed', 'resourcesCount': 0,
                                'isOwner': False, 'isEditor': True}])):
            with self.subTest(user=user):
                client.force_authenticate(user)
                response = client.get('/d/', HTTP_ACCEPT='application/json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected)


class SearchReadContracts(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.search = self.enterContext(patch.object(Elasticsearch, 'search'))
        self.logger = self.enterContext(patch('elixir.elixir_logging.SearchLogger.commit'))
        self.items = [{'biotoolsID': 'beta', 'name': 'Beta', 'extraIndexField': ['kept']},
                      {'biotoolsID': 'alpha', 'name': 'Alpha', 'function': []}]
        self.search.return_value = hits(self.items, 5)

    def test_text_filter_order_and_pagination(self):
        response = self.client.get('/t/', {
            'q': 'sequence "alignment tool"', 'toolType': '"Command-line tool"',
            'sort': 'name', 'ord': 'asc', 'page': '2', 'per_page': '2'},
            HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 5, 'next': '?page=3',
                                          'previous': '?page=1', 'list': self.items})
        self.search.assert_called_once()
        self.logger.assert_called_once()
        body = self.search.call_args.kwargs['body']
        self.assertEqual((body['size'], body['from']), (2, 2))
        self.assertEqual(body['sort'], {'name': {'order': 'asc'}})
        self.assertTrue(body['track_total_hits'])
        clauses = body['query']['bool']['must']
        self.assertEqual(len(clauses), 3)
        self.assertIn({'match_phrase': {'name': {'query': 'alignment tool', 'boost': 10.0}}},
                      clauses[0]['dis_max']['queries'])
        self.assertIn({'match': {'biotoolsID': {'query': 'sequence', 'boost': 40.0}}},
                      clauses[1]['dis_max']['queries'])
        self.assertEqual(clauses[2], {'bool': {'should': [
            {'match_phrase': {'toolType': 'Command-line tool'}}]}})

    def test_defaults_caps_invalid_size_and_sort_aliases(self):
        for params, size, sort in (
                ({}, 50, 'lastUpdate'), ({'per_page': 'bad'}, 50, 'lastUpdate'),
                ({'per_page': '1000'}, 100, 'lastUpdate'),
                ({'sort': 'unknown'}, 50, 'lastUpdate'),
                ({'sort': 'score'}, 50, '_score'),
                ({'sort': 'citationCount'}, 50, 'publication.metadata.citationCount'),
                ({'sort': 'citationDate'}, 50, 'publication.metadata.date')):
            with self.subTest(params=params):
                response = self.client.get('/tool/', params, HTTP_ACCEPT='application/json')
                self.assertEqual(response.status_code, 200)
                body = self.search.call_args.kwargs['body']
                self.assertEqual((body['size'], body['from']), (size, 0))
                self.assertEqual(body['sort'], {sort: {'order': 'desc'}})
                self.assertIsNone(response.json()['previous'])

    def test_empty_results_and_out_of_range_page(self):
        for count, code, expected in (
                (0, 200, {'count': 0, 'next': None, 'previous': '?page=1', 'list': []}),
                (3, 404, {'detail': 'Invalid page. That page contains no results.'})):
            self.search.return_value = hits([], count)
            response = self.client.get('/t/?page=2', HTTP_ACCEPT='application/json')
            self.assertEqual(response.status_code, code)
            self.assertEqual(response.json(), expected)

    def test_malformed_page_and_zero_size_keep_legacy_outcomes(self):
        with self.assertRaises(ValueError):
            self.client.get('/t/?page=bad', HTTP_ACCEPT='application/json')
        self.search.assert_not_called()
        self.search.return_value = hits([], 3)
        response = self.client.get('/t/?per_page=0', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.search.call_args.kwargs['body']['size'], 0)

    def test_domain_filter_uses_two_requests_and_lowercase_ids(self):
        self.search.side_effect = [hits([{'resources': [{'biotoolsID': 'ALPHA'},
                                                       {'biotoolsID': 'Alpha'}]}]),
                                   hits(self.items[:1])]
        response = self.client.get('/t/?domain=managed', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.search.call_count, 2)
        domain, tools = self.search.call_args_list
        self.assertEqual(domain.kwargs['index'], 'domains')
        self.assertEqual(domain.kwargs['body']['query']['bool']['must'],
                         [{'match_phrase': {'domain.raw': {'query': 'managed'}}}])
        self.assertEqual(set(tools.kwargs['body']['query']['bool']['must'][-1]
                             ['terms']['biotoolsID']), {'alpha'})

    def test_missing_domain_is_unfiltered_but_empty_domain_has_empty_terms(self):
        for domain_result, expected in ((hits([]), []),
                                        (hits([{'resources': []}]), [{'terms': {'biotoolsID': []}}])):
            self.search.side_effect = [domain_result, hits([])]
            response = self.client.get('/t/?domain=missing', HTTP_ACCEPT='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.search.call_args.kwargs['body']['query']['bool']['must'], expected)


class SharedSearchContracts(SimpleTestCase):
    def test_plain_mapping_and_querydict_return_results_without_database_or_logging(self):
        for params in ({'q': 'last', 'page': 90, 'per_page': 1},
                       QueryDict('q=first&q=last&page=90&per_page=1')):
            original = params.copy()
            with patch.object(Elasticsearch, 'search', return_value=hits([{'name': 'Raw'}])) as search, \
                    patch('elixir.queries.perf_counter', side_effect=[100, 100.005]), \
                    patch('elixir.elixir_logging.SearchLogger.commit') as logger:
                result = search_tools(params, page=1, per_page=500)
                self.assertEqual(result.items, [{'name': 'Raw'}])
                self.assertEqual((result.count, result.page, result.per_page), (1, 1, 100))
                self.assertEqual(result.backend_requests, 1)
                self.assertAlmostEqual(result.elapsed_ms, 5)
                self.assertEqual(params, original)
                search.assert_called_once()
                logger.assert_not_called()
                self.assertIn('last', str(search.call_args.kwargs['body']))
                self.assertNotIn('first', str(search.call_args.kwargs['body']))

    def test_domain_search_reports_both_requests(self):
        with patch.object(Elasticsearch, 'search', side_effect=[hits([]), hits([])]) as search:
            result = search_tools({'domain': 'missing'}, page=1, per_page=10)
        self.assertEqual(result.backend_requests, 2)
        self.assertEqual(search.call_count, 2)

    def test_domain_errors_and_backend_failures_are_not_empty_successes(self):
        with patch.object(Elasticsearch, 'search') as search:
            with self.assertRaises(InvalidQuery):
                search_tools({}, page='bad', per_page=10)
            search.assert_not_called()
            search.return_value = hits([], 10)
            with self.assertRaises(SearchPageNotFound):
                search_tools({}, page=9, per_page=10)
            error = TransportError(503, 'test backend unavailable')
            search.side_effect = error
            with self.assertRaises(TransportError) as raised:
                search_tools({}, page=1, per_page=10)
            self.assertIs(raised.exception, error)
