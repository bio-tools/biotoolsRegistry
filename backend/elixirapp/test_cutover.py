from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase, RequestFactory, override_settings
from django.urls import get_script_prefix, set_script_prefix

from elixirapp import canonical_wsgi, dev_wsgi
from elixirapp.html import RESERVED, canonical_family
from elixirapp.search_workspace import summary
from elixirapp.tests.detail_fixtures import create_detail_fixture
from elixir.serializers import ResourceSerializer, ResourceUpdateSerializer
from elixirapp.resource_editor import normalized
from elixirapp.test_resource_editor_contract import FIXTURES


@override_settings(DEBUG=False)
class CutoverTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_detail_fixture(User.objects.create_user('detail-owner'))

    def setUp(self):
        self.addCleanup(set_script_prefix, get_script_prefix())
        set_script_prefix('')

    def get(self, path, **kwargs):
        return self.client.get(path, **{'biotools.canonical': True, **kwargs})

    def test_canonical_detail_headers_links_and_legacy_management(self):
        for agent in ('Browser', 'Googlebot'):
            with self.assertLogs('biotools.routes', level='INFO') as logs:
                response = self.get('/detail-demo', HTTP_USER_AGENT=agent)
            self.assertContains(response, '<h1>Sequence Workbench (demo)</h1>')
            self.assertContains(response, 'href="/detail-demo/manage"')
            self.assertNotContains(response, '_legacy=1')
            self.assertContains(response, 'href="/detail-demo/edit"')
            self.assertContains(response, 'href="/migration-fixture"')
            self.assertNotContains(response, 'Migration preview')
            self.assertContains(response, 'name="robots" content="index, follow"')
            self.assertEqual(response['X-Biotools-Route'], 'django-detail')
            self.assertEqual(response['X-Robots-Tag'], 'index, follow')
            self.assertIn('no-store', response['Cache-Control'])
            self.assertIn('route;dur=', response['Server-Timing'])
            self.assertIn('route=detail method=GET status=200 duration_ms=', logs.output[0])

    def test_aliases_and_case_preserve_queries_without_permanent_redirects(self):
        for path in ('/tool/detail-demo', '/t/detail-demo/', '/biotools:detail-demo', '/DETAIL-DEMO/'):
            response = self.get(path + '?tab=functions')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], '/detail-demo?tab=functions')
            self.assertEqual(self.get(response['Location']).status_code, 200)
        self.assertEqual(self.get('/missing-cutover')['X-Robots-Tag'], 'noindex, follow')
        self.assertEqual(self.get('/missing-cutover').status_code, 404)

    @patch('elixirapp.search_workspace.search_tools')
    def test_search_links_data_endpoint_and_legacy_filter_compatibility(self, search):
        from elixir.queries import ToolSearchResult
        search.return_value = ToolSearchResult([], 0, 1, 50, 1, 1)
        response = self.get('/t?q=sequence')
        self.assertContains(response, '/_search/data/')
        self.assertContains(response, '/_edam/terms/')
        self.assertEqual(response['X-Robots-Tag'], 'noindex, follow')
        response = self.get('/t/?q=sequence')
        self.assertEqual(response['Location'], '/t?q=sequence')
        response = self.get('/t?domain=proteomics&topicID=topic_0080&topicID=topic_0121')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(search.call_args.args[0]['topicID'], 'topic_0121')
        self.assertEqual(search.call_args.args[0]['domain'], 'proteomics')
        self.assertNotContains(response, '_legacy=1')
        response = self.get('/_search/data/?unsupported=1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error']['code'], 'invalid_search')

    def test_native_route_boundaries(self):
        for path in ('/api/t/detail-demo', '/api/schema/', '/static/app.css'):
            self.assertIsNone(canonical_family(path))
        for path, family in (('/', 'public'), ('/detail-demo', 'detail'), ('/t', 'search'),
                             ('/detail-demo/edit', 'editor'), ('/orcid/callback/', 'accounts'),
                             ('/workflows', 'management')):
            self.assertEqual(canonical_family(path), family)
        self.assertEqual(self.get('/detail-demo?_legacy=1').status_code, 200)
        self.assertEqual(summary({'biotoolsID': 'detail-demo', 'name': 'Demo'}, canonical=True)['url'], '/detail-demo')

    @patch('elixirapp.search_workspace.search_tools')
    def test_wsgi_entries_preserve_root_urls_and_api_header_isolation(self, search):
        from elixir.queries import ToolSearchResult
        search.return_value = ToolSearchResult([], 0, 1, 50, 1, 1)
        for app, path, extra in (
                (dev_wsgi.application, '/t', {}),
                (canonical_wsgi.application, '', {'SCRIPT_NAME': '/t', 'REQUEST_URI': '/t'})):
            environ = RequestFactory().get(path or '/', **extra).environ
            headers = []
            response = app(environ, lambda status, values: headers.append((status, values)))
            try:
                body = b''.join(response).decode()
            finally:
                response.close()
            self.assertEqual(headers[0][0], '200 OK')
            self.assertIn('/_edam/terms/', body)
            self.assertNotIn('/t/_migration', body)
        response = self.client.get('/env/', HTTP_BIOTOOLS_CANONICAL='true', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('X-Biotools-Route', response)

    def test_native_development_dispatch_keeps_api_and_html_mounts_separate(self):
        with patch.object(dev_wsgi.wsgi, 'application') as api, \
                patch.object(dev_wsgi.html_wsgi, 'application') as html, \
                patch.object(dev_wsgi.canonical_wsgi, 'application') as canonical:
            for path, target, expected in (('/api/t', api, '/t'),
                                           ('/_migration/html/auth/session/', html, '/auth/session/'),
                                           ('/unknown/path', canonical, '/unknown/path')):
                environ = {'PATH_INFO': path}
                dev_wsgi.application(environ, None)
                target.assert_called_once_with(environ, None)
                self.assertEqual(environ['PATH_INFO'], expected)
                target.reset_mock()


@override_settings(DEBUG=False, GITHUB_ECOSYSTEM_ON=False)
class EditorCutoverTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('canonical-owner')
        create_detail_fixture(cls.owner)
        serializer = ResourceSerializer(data={**FIXTURES['minimal'], 'biotoolsID': 'canonical-edit'})
        assert serializer.is_valid(), serializer.errors
        serializer.save(owner=cls.owner)

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.addCleanup(set_script_prefix, get_script_prefix())
        set_script_prefix('')
        self.es = self.enterContext(patch('elixir.view.resource.es'))
        self.es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'canonical-test'}]}}

    def get(self, path):
        return self.client.get(path, **{'biotools.canonical': True})

    def post(self, path, body, csrf=True):
        headers = {'HTTP_X_CSRFTOKEN': self.client.cookies['csrftoken'].value} if csrf else {}
        return self.client.post(path, body, content_type='application/json', HTTP_ACCEPT='application/json',
                                **{'biotools.canonical': True}, **headers)

    def test_native_editor_route_boundaries(self):
        for path in ('/register', '/register/', '/register/save/', '/detail-demo/edit', '/detail-demo/edit/', '/detail-demo/edit/save/'):
            self.assertEqual(canonical_family(path), 'editor')
        for path in ('/requests', '/requests/', '/requests/conclude/', '/requests/tool/detail-demo/'):
            self.assertEqual(canonical_family(path), 'requests')
        for path in ('/api/edit', '/static/edit'):
            self.assertIsNone(canonical_family(path))
        for path in ('/login', '/profile', '/signup', '/reset-password', '/orcid/callback/'):
            self.assertEqual(canonical_family(path), 'accounts')

    def test_canonical_urls_headers_and_fallback(self):
        self.client.force_login(self.owner)
        for path in ('/detail-demo/edit', '/detail-demo/edit/'):
            response = self.get(path)
            self.assertEqual(response.status_code, 200)
            config = response.context['editor_config']
            self.assertEqual(config['endpoint'], '/detail-demo/edit/save/')
            self.assertEqual(config['editUrl'], '/detail-demo/edit')
            self.assertEqual(config['detailUrl'], '/detail-demo')
            self.assertEqual(config['edamEndpoint'], '/_edam/terms/')
            self.assertEqual(response['X-Biotools-Route'], 'django-editor')
            self.assertEqual(response['X-Robots-Tag'], 'noindex, follow')
            self.assertIn('no-store', response['Cache-Control'])
            self.assertIn('Cookie', response['Vary'])
            self.assertNotContains(response, 'href="/detail-demo/edit?_legacy=1"')
            self.assertContains(response, 'Export stored JSON')
            self.assertNotContains(response, 'Migration preview')
        self.assertEqual(self.get('/register').context['editor_config']['endpoint'], '/register/save/')
        self.assertEqual(self.get('/requests')['X-Biotools-Route'], 'django-requests')
        self.assertContains(self.get('/requests/tool/detail-demo/'), 'href="/detail-demo"')
        self.assertContains(self.get('/detail-demo'), 'href="/requests/tool/detail-demo/"')
        self.assertEqual(self.get('/absent-editor/edit').status_code, 404)

    def test_anonymous_navigation_and_expired_json_mutation(self):
        for path in ('/register', '/detail-demo/edit', '/requests'):
            response = self.get(path)
            destination = urlsplit(response['Location'])
            self.assertEqual(destination.path, '/login')
            self.assertEqual(parse_qs(destination.query)['next'], [path])
        response = self.post('/detail-demo/edit/save/', {}, csrf=False)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error']['code'], 'authentication_required')

    def test_canonical_mutation_csrf_and_stale_revision(self):
        self.client.force_login(self.owner)
        config = self.get('/canonical-edit/edit').context['editor_config']
        body = {'resource': normalized(config['resource'], ResourceUpdateSerializer()), 'revision': config['revision'],
                'schemaRevision': config['schemaRevision']}
        body['resource']['name'] = 'Canonical editor saved'
        self.assertEqual(self.post(config['endpoint'], body, csrf=False).status_code, 403)
        response = self.post(config['endpoint'], body)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['editUrl'], '/canonical-edit/edit')
        self.assertEqual(response.json()['edamEndpoint'], '/_edam/terms/')
        self.assertEqual(self.post(config['endpoint'], body).status_code, 409)
        self.es.index.assert_called_once()
        self.client.force_login(User.objects.create_user('canonical-outsider'))
        self.assertEqual(self.get('/detail-demo/edit').status_code, 403)
        self.assertEqual(self.post(config['endpoint'], body).status_code, 403)

    def test_root_wsgi_editor_redirects_and_api_isolation(self):
        self.client.force_login(self.owner)
        response = self.client.get('/rest-auth/user/', HTTP_ACCEPT='application/json', HTTP_BIOTOOLS_CANONICAL='true')
        self.assertEqual(response.status_code, 401)
        self.assertNotIn('X-Biotools-Route', response)
        for app, path, extra in (
                (dev_wsgi.application, '/register', {}),
                (canonical_wsgi.application, '/', {'SCRIPT_NAME': '/register', 'REQUEST_URI': '/register'})):
            headers = []
            response = app(RequestFactory().get(path, **extra).environ,
                           lambda status, values: headers.append((status, dict(values))))
            try:
                b''.join(response)
            finally:
                response.close()
            self.assertEqual(headers[0][0], '302 Found')
            self.assertTrue(headers[0][1]['Location'].startswith('/login'))
