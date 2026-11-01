import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.template.loader import render_to_string
from django.test import SimpleTestCase, override_settings

from elixir.templatetags.modern_assets import modern_script
from elixirapp.test_html import HTML_REQUEST


@override_settings(DEBUG=False)
class VueIslandTests(SimpleTestCase):
    def test_full_page_fragment_and_history_restore(self):
        for headers, full in (({}, True), ({'HTTP_HX_REQUEST': 'true'}, False),
                              ({'HTTP_HX_REQUEST': 'true', 'HTTP_HX_HISTORY_RESTORE_REQUEST': 'true'}, True)):
            response = self.client.get('/islands/', **headers, **HTML_REQUEST)
            self.assertEqual(response.status_code, 200)
            self.assertEqual('<!doctype html>' in response.content.decode(), full)
            self.assertContains(response, 'data-vue-island="counter-demo"', count=2)
            self.assertContains(response, 'hx-disable>', count=2)
            self.assertContains(response, '<template id="first-counter-props">')
            self.assertContains(response, '"initial": 3')
            self.assertContains(response, '"initial": 7')
            self.assertIn('HX-Request', response['Vary'])
            self.assertIn('HX-History-Restore-Request', response['Vary'])

    def test_props_and_native_fallback_are_escaped(self):
        label = '</script></template><img src=x onerror=alert(1)> & "text"'
        body = render_to_string('html/fragments/islands.html', {
            'first_counter': {'label': label, 'initial': 3},
            'second_counter': {'label': 'Second', 'initial': 7},
        })
        self.assertNotIn('<img', body)
        self.assertIn(r'\u003C/script\u003E\u003C/template\u003E', body)
        self.assertIn('&lt;/script&gt;&lt;/template&gt;', body)
        self.assertEqual(body.count('</script>'), 2)

    def test_read_only_and_missing_assets_fallback(self):
        self.assertEqual(self.client.post('/islands/', **HTML_REQUEST).status_code, 405)
        self.assertEqual(self.client.head('/islands/', **HTML_REQUEST).content, b'')
        with patch('elixir.templatetags.modern_assets.finders.find', return_value=None):
            response = self.client.get('/islands/', **HTML_REQUEST)
        self.assertContains(response, '<h2>First counter</h2>')
        self.assertNotContains(response, 'type="module"')

    def test_manifest_includes_component_styles(self):
        with TemporaryDirectory() as directory:
            manifest = Path(directory) / 'manifest.json'
            manifest.write_text(json.dumps({'src/main.js': {
                'file': 'assets/main-abc.js', 'css': ['assets/main-def.css'],
            }}))
            with patch('elixir.templatetags.modern_assets.finders.find', return_value=str(manifest)), \
                    override_settings(STATIC_URL='/assets/'):
                self.assertEqual(str(modern_script()),
                                 '<link rel="stylesheet" href="/assets/modern/assets/main-def.css">'
                                 '<script type="module" src="/assets/modern/assets/main-abc.js"></script>')
