from pathlib import Path
from unittest.mock import patch
import shlex

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client, RequestFactory, SimpleTestCase, override_settings
from django.urls import get_script_prefix, resolve, set_script_prefix

from elixirapp import dev_wsgi, html, html_urls, html_wsgi, wsgi


HTML_REQUEST = {'biotools.html': True}
HTML_MOUNT = '/_migration/html'


@override_settings(DEBUG=False)
class HtmlShellTests(SimpleTestCase):
    def test_production_can_hide_preview_demos_without_disabling_helpers(self):
        with override_settings(MIGRATION_PREVIEW_DEMOS=False):
            for path in ('/', '/preview/', '/preview', '/islands/', '/islands', '/edam/', '/edam'):
                self.assertEqual(self.client.get(path, **HTML_REQUEST).status_code, 404, path)
            self.assertEqual(self.client.get('/edam/terms/?scope=unknown', **HTML_REQUEST).status_code, 400)
            self.assertEqual(self.client.get('/auth/session/', **HTML_REQUEST).status_code, 302)
            self.assertEqual(self.client.get('/editor/new/', **HTML_REQUEST).status_code, 302)
        with override_settings(MIGRATION_PREVIEW_DEMOS=True):
            self.assertEqual(self.client.get('/', **HTML_REQUEST).status_code, 200)
            self.assertEqual(self.client.get('/islands/', **HTML_REQUEST).status_code, 200)

    def test_complete_page_and_context_without_javascript(self):
        response = self.client.get('/', **HTML_REQUEST)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        self.assertTemplateUsed(response, 'html/index.html')
        self.assertTemplateUsed(response, 'html/base.html')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.context['request'].urlconf, 'elixirapp.html_urls')
        for element in ('<!doctype html>', '<header', '<nav', '<main', '<footer',
                        'method="get" action="/t"', 'name="csrfmiddlewaretoken"'):
            self.assertContains(response, element)
        for dependency in ('ng-app', 'ng-controller', '/dist/', 'hx-'):
            self.assertNotContains(response, dependency)

    def test_refresh_returns_the_same_page(self):
        for _ in range(2):
            response = self.client.get('/', **HTML_REQUEST)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'html/index.html')

    def test_post_requires_csrf_and_messages_survive_redirect_once(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/', **HTML_REQUEST)
        token = response.cookies[settings.CSRF_COOKIE_NAME].value
        self.assertEqual(client.post('/', **HTML_REQUEST).status_code, 403)
        response = client.post('/', {'csrfmiddlewaretoken': token}, **HTML_REQUEST)
        self.assertEqual(response.status_code, 302)
        response = client.get(response['Location'], **HTML_REQUEST)
        self.assertContains(response, 'Session check complete.')
        self.assertContains(response, 'role="status"')
        self.assertNotContains(client.get('/', **HTML_REQUEST), 'Session check complete.')

    def test_unsupported_methods_are_rejected(self):
        self.assertEqual(self.client.delete('/', **HTML_REQUEST).status_code, 405)

    @override_settings(CSRF_TRUSTED_ORIGINS=['https://localhost:8443'])
    def test_proxy_origin_requires_an_explicit_trust_entry_and_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        token = client.get('/', **HTML_REQUEST).cookies[settings.CSRF_COOKIE_NAME].value
        for origin, data, expected in (
                ('https://localhost:8443', {'csrfmiddlewaretoken': token}, 302),
                ('https://localhost:8443', {}, 403),
                ('https://untrusted.invalid', {'csrfmiddlewaretoken': token}, 403)):
            response = client.post('/', data, HTTP_ORIGIN=origin, **HTML_REQUEST)
            self.assertEqual(response.status_code, expected)

    def test_missing_html_route_returns_scoped_404(self):
        response = self.client.get('/does-not-exist/', **HTML_REQUEST)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'html/404.html')
        self.assertContains(response, '<h1>Page not found</h1>', status_code=404)

    def test_exception_returns_scoped_500_without_request_context(self):
        client = Client(raise_request_exception=False)
        with patch('elixirapp.html.render', side_effect=RuntimeError('private details')), \
                patch('elixirapp.html.render_to_string', wraps=html.render_to_string) as renderer:
            response = client.get('/', **HTML_REQUEST)
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, 'html/500.html')
        self.assertContains(response, '<h1>Server error</h1>', status_code=500)
        self.assertNotContains(response, 'private details', status_code=500)
        renderer.assert_called_once_with('html/500.html')

    def test_namespaced_url_and_handlers(self):
        match = resolve('/', urlconf=html_urls)
        self.assertEqual(match.view_name, 'html:index')
        self.assertIs(match.func, html.index)
        self.assertIs(html_urls.handler404, html.page_not_found)
        self.assertIs(html_urls.handler500, html.server_error)

    def test_static_assets_are_found_outside_the_legacy_build(self):
        for name in ('shell.css', 'biotools-white.svg'):
            path = finders.find('html/' + name)
            self.assertIsNotNone(path)
            self.assertTrue(Path(path).is_file())


@override_settings(DEBUG=False)
class RouteIsolationTests(SimpleTestCase):
    def setUp(self):
        self.addCleanup(set_script_prefix, get_script_prefix())

    def wsgi_response(self, application, path, mount, **extra):
        environ = RequestFactory().get(path, SCRIPT_NAME=mount, **extra).environ
        headers = []
        response = application(environ, lambda status, values: headers.append((status, values)))
        try:
            body = b''.join(response).decode('utf-8')
        finally:
            response.close()
        return headers[0][0], body

    def test_html_mount_preserves_reverse_urls(self):
        status, body = self.wsgi_response(html_wsgi.application, '/', HTML_MOUNT)
        self.assertEqual(status, '200 OK')
        self.assertIn('method="post" action="/_migration/html/"', body)
        self.assertIn('href="/static/html/shell.css"', body)

    def test_api_wsgi_stays_api_even_with_a_spoofed_header(self):
        self.wsgi_response(html_wsgi.application, '/', HTML_MOUNT)
        status, body = self.wsgi_response(wsgi.application, '/env/', '/api',
                                          HTTP_ACCEPT='application/json', HTTP_BIOTOOLS_HTML='true')
        self.assertEqual(status, '200 OK')
        self.assertIn(body, ('"Development"', '"Production"'))

    def test_runserver_dispatch_matches_wsgi_mounts(self):
        status, body = self.wsgi_response(dev_wsgi.application, '/_migration/html/', '')
        self.assertEqual(status, '200 OK')
        self.assertIn('action="/_migration/html/"', body)
        status, body = self.wsgi_response(dev_wsgi.application, '/api/env/', '',
                                          HTTP_BIOTOOLS_HTML='true')
        self.assertEqual(status, '200 OK')
        self.assertIn(body, ('"Development"', '"Production"'))

    def test_runserver_fragment_history_errors_and_api_isolation(self):
        for headers, complete in (({'HTTP_HX_REQUEST': 'true'}, False),
                                  ({'HTTP_HX_REQUEST': 'true',
                                    'HTTP_HX_HISTORY_RESTORE_REQUEST': 'true'}, True)):
            status, body = self.wsgi_response(dev_wsgi.application,
                                              '/_migration/html/preview/', '', **headers)
            self.assertEqual(status, '200 OK')
            self.assertEqual('<!doctype html>' in body, complete)
            self.assertIn('/_migration/html/preview/', body)
        status, body = self.wsgi_response(dev_wsgi.application, '/_migration/html/missing/', '')
        self.assertEqual(status, '404 Not Found')
        self.assertIn('<h1>Page not found</h1>', body)
        status, body = self.wsgi_response(dev_wsgi.application, '/api/_migration/html/', '')
        self.assertEqual(status, '404 Not Found')
        self.assertNotIn('Session check', body)

    def test_existing_api_urls_keep_their_views(self):
        cases = {
            '/t/': 'ResourceList',
            '/tool/': 'ResourceList',
            '/t/signalp': 'ResourceDetail',
            '/signalp': 'ResourceDetail',
            '/d/': 'DomainView',
            '/env/': 'Environment',
            '/rest-auth/login/': 'LoginView',
            '/rest-auth/orcid/': 'OrcidLogin',
            '/rest-auth/orcid/connect/': 'OrcidConnect',
            '/rest-auth/socialaccounts/': 'SocialAccountListView',
            '/rest-auth/socialaccounts/1/disconnect/': 'SocialAccountDisconnectView',
            '/rest-auth/password/reset/confirm/uid/token/': 'PasswordResetConfirmView',
            '/schema/': 'SpectacularAPIView',
        }
        for path, name in cases.items():
            with self.subTest(path=path):
                match = resolve(path, urlconf='elixirapp.urls')
                self.assertEqual(match.func.view_class.__name__, name)

    def test_proxy_mounts_do_not_claim_legacy_routes(self):
        config = (Path(settings.BASE_DIR) / 'runtime/apache-native.conf').read_text()
        aliases = {}
        for line in config.splitlines():
            parts = shlex.split(line, comments=True)
            if parts and parts[0] == 'WSGIScriptAlias':
                aliases[parts[1]] = parts[2]
        self.assertEqual(aliases, {
            '/api': '/elixir/application/backend/elixirapp/wsgi.py',
            HTML_MOUNT: '/elixir/application/backend/elixirapp/html_wsgi.py',
        })
        self.assertIn('DocumentRoot /elixir/application/frontend', config)
        self.assertIn('canonical_wsgi.py [H=wsgi-script,L]', config)
        for path in ('/', '/t', '/signalp', '/signalp/edit', '/register', '/communities',
                     '/_migration', '/_migration/htmlish', '/about'):
            with self.subTest(path=path):
                self.assertFalse(any(path == mount or path.startswith(mount + '/') for mount in aliases))

    def test_http_header_does_not_choose_html_urlconf(self):
        request = RequestFactory().get('/', HTTP_BIOTOOLS_HTML='true')
        html.HtmlRoutingMiddleware(lambda request: None)(request)
        self.assertFalse(hasattr(request, 'urlconf'))
