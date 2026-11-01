import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client, SimpleTestCase, override_settings

from elixir.templatetags.modern_assets import modern_script
from elixirapp.test_html import HTML_REQUEST


@override_settings(DEBUG=False)
class ProgressiveHtmlTests(SimpleTestCase):
    def test_full_page_and_fragment_share_validated_escaped_state(self):
        for enhanced in (False, True):
            with self.subTest(enhanced=enhanced):
                response = self.client.get('/preview/', {'message': '<b>Hello</b>'},
                                           HTTP_HX_REQUEST=str(enhanced).lower(), **HTML_REQUEST)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'html/fragments/preview.html')
                self.assertContains(response, '&lt;b&gt;Hello&lt;/b&gt;')
                self.assertContains(response, 'id="message-preview"', count=1)
                self.assertContains(response, 'hx-push-url="true"')
                self.assertEqual('<!doctype html>' in response.content.decode(), not enhanced)
                self.assertEqual(response.context['preview_message'], '<b>Hello</b>')
                self.assertIn('HX-Request', response['Vary'])
                self.assertIn('HX-History-Restore-Request', response['Vary'])

    def test_history_restore_always_returns_a_complete_page(self):
        response = self.client.get('/preview/', {'message': 'Previous'}, HTTP_HX_REQUEST='true',
                                   HTTP_HX_HISTORY_RESTORE_REQUEST='true', **HTML_REQUEST)
        self.assertContains(response, '<!doctype html>')
        self.assertContains(response, 'Previous')

    def test_default_state_and_invalid_inputs(self):
        self.assertContains(self.client.get('/preview/', **HTML_REQUEST), 'Welcome to bio.tools.')
        for value in ('', 'x' * 121):
            for enhanced in ('true', 'false'):
                response = self.client.get('/preview/', {'message': value},
                                           HTTP_HX_REQUEST=enhanced, **HTML_REQUEST)
                self.assertEqual(response.status_code, 400)
                self.assertIn('message', response.context['form'].errors)
                self.assertContains(response, 'errorlist', status_code=400)

    def test_preview_is_read_only_and_supports_head(self):
        self.assertEqual(self.client.post('/preview/', **HTML_REQUEST).status_code, 405)
        response = self.client.head('/preview/', HTTP_HX_REQUEST='true', **HTML_REQUEST)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    def test_hx_header_does_not_bypass_csrf_on_existing_session_form(self):
        client = Client(enforce_csrf_checks=True)
        token = client.get('/', **HTML_REQUEST).cookies[settings.CSRF_COOKIE_NAME].value
        response = client.post('/', HTTP_HX_REQUEST='true', **HTML_REQUEST)
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(client.get('/', **HTML_REQUEST), 'Session check complete.')
        response = client.post('/', {'csrfmiddlewaretoken': token}, HTTP_HX_REQUEST='true', **HTML_REQUEST)
        self.assertEqual(response.status_code, 302)
        self.assertContains(client.get('/', **HTML_REQUEST), 'Session check complete.')


class ModernAssetTests(SimpleTestCase):
    def test_manifest_resolves_hashed_entry_with_static_prefix(self):
        with TemporaryDirectory() as directory:
            manifest = Path(directory) / 'manifest.json'
            manifest.write_text(json.dumps({'src/main.js': {'file': 'assets/main-test123.js'}}))
            with patch('elixir.templatetags.modern_assets.finders.find', return_value=str(manifest)), \
                    override_settings(STATIC_URL='/assets/'):
                self.assertEqual(str(modern_script()),
                                 '<script type="module" src="/assets/modern/assets/main-test123.js"></script>')

    def test_missing_build_keeps_native_fallback_available(self):
        with patch('elixir.templatetags.modern_assets.finders.find', return_value=None):
            self.assertEqual(modern_script(), '')
            response = self.client.get('/preview/', {'message': 'Native'}, **HTML_REQUEST)
        self.assertContains(response, '<!doctype html>')
        self.assertContains(response, 'Native')
        self.assertNotContains(response, '<script')

    def test_built_entry_is_discoverable_when_present(self):
        manifest = finders.find('modern/manifest.json')
        if not manifest:
            self.skipTest('Run npm ci && npm run build in frontend-modern to check built assets.')
        with open(manifest) as source:
            entry = json.load(source)['src/main.js']['file']
        self.assertRegex(entry, r'^assets/main-[\w-]+\.js$')
        self.assertTrue(Path(finders.find('modern/' + entry)).is_file())
        self.assertIn(entry, str(modern_script()))
