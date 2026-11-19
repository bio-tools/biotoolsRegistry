from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from lxml import html

from elixirapp.management_pages import DomainForm
from elixirapp.public_pages import domains


@override_settings(ROOT_URLCONF='elixirapp.canonical_editor_urls')
class DomainFormattingTests(SimpleTestCase):
    def test_form_preserves_description_html(self):
        description = '<p>See <strong>our tools</strong> and <a href="https://example.org">documentation</a>.</p>'
        form = DomainForm({'domain': 'example', 'description': description})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.payload()['description'], description)
        self.assertIn('HTML', form.fields['description'].help_text)

    @patch('elixirapp.public_pages.public_domains')
    def test_directory_displays_safe_html_and_removes_executable_content(self, read):
        read.return_value = [{'domain': 'example', 'description':
            '<p>Hello <strong>world</strong> <a href="https://example.org" onclick="alert(1)">link</a>'
            '<a href="jav&#x61;script:alert(1)">bad link</a><script>alert(1)</script>'
            '<svg onload="alert(2)"></svg><img src=x onerror="alert(3)"></p>', 'collection': [], 'tag': []}]
        request = RequestFactory().get('/domains')
        request.canonical = True
        request.user = SimpleNamespace(is_authenticated=False)
        response = domains(request, {})
        self.assertEqual(response.status_code, 200)
        document = html.fromstring(response.content)
        description = document.xpath('//details[contains(@class, "domain-description")]')[0]
        self.assertEqual(description.xpath('.//strong/text()'), ['world'])
        self.assertEqual(description.xpath('.//a/@href'), ['https://example.org'])
        self.assertFalse(description.xpath('.//script|.//svg|.//img|.//*[@onclick or @onload or @onerror]'))

    @patch('elixirapp.public_pages.public_domains', return_value=[])
    def test_sign_out_is_inside_account_menu(self, _read):
        request = RequestFactory().get('/domains')
        request.canonical = True
        request.user = SimpleNamespace(is_authenticated=True, username='tester', pk=1)
        response = domains(request, {})
        document = html.fromstring(response.content)
        buttons = document.xpath('//details[contains(@class, "account-menu")]//form[@method="post"]//button[normalize-space()="Sign out"]')
        self.assertEqual(len(buttons), 1)
