import json
from unittest.mock import MagicMock, patch

import requests
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client, SimpleTestCase, TestCase, override_settings

from elixir.models import Resource
from elixir.resource_ui import resource_descriptor
from elixir.serializers import ResourceSerializer
from elixirapp.pub2tools import fetch, publication, webpage
from elixirapp.test_resource_editor_contract import FIXTURES


class PublicationInputTests(SimpleTestCase):
    def test_supported_identifiers_and_canonical_links(self):
        for value, expected in (
            ('10.1093/nar/gkad347', {'doi': '10.1093/nar/gkad347'}),
            ('https://doi.org/10.1093/nar/gkad347', {'doi': '10.1093/nar/gkad347'}),
            ('PMID: 37144459', {'pmid': '37144459'}),
            ('https://pubmed.ncbi.nlm.nih.gov/37144459/', {'pmid': '37144459'}),
            ('pmc10320099', {'pmcid': 'PMC10320099'}),
            ('https://pmc.ncbi.nlm.nih.gov/articles/PMC10320099/', {'pmcid': 'PMC10320099'}),
            ('https://europepmc.org/articles/PMC10320099', {'pmcid': 'PMC10320099'}),
        ):
            with self.subTest(value=value):
                self.assertEqual(publication(value), expected)
        for value in ('', None, 'example.org', 'https://example.org/article', 'http://doi.org/10.1234/example',
                      'https://doi.org.evil.example/10.1234/example', 'https://user@doi.org/10.1234/example',
                      'https://doi.org:bad/10.1234/example', '10.1234/invalid value'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                publication(value)

    def test_document_must_be_a_public_https_url(self):
        self.assertIsNone(webpage(''))
        self.assertEqual(webpage('https://example.org/guide?version=1'), 'https://example.org/guide?version=1')
        for value in ('http://example.org', 'https://localhost', 'https://service.local/file',
                      'https://127.0.0.1/data', 'https://127.1/', 'https://0x7f.1/', 'https://10.1.2.3', 'https://[::1]/',
                      'https://user@example.org/', 'https://example.org:8443/', 'https://example.org/#part'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                webpage(value)

    @override_settings(PUB2TOOLS_URL='https://provider.example/api')
    def test_provider_response_limits_and_tool_envelope(self):
        for status, raw in ((200, {'success': True, 'tool': {'name': 'Example'}}),):
            response = MagicMock(status_code=status)
            response.__enter__.return_value = response
            response.iter_content.return_value = [json.dumps(raw).encode()]
            with patch('elixirapp.pub2tools.requests.post', return_value=response) as post:
                self.assertEqual(fetch({'publicationIds': [{'pmid': '123'}]}), {'name': 'Example'})
                self.assertFalse(post.call_args.kwargs['allow_redirects'])
                self.assertEqual(post.call_args.kwargs['timeout'], (5, 180))
        for status, body in ((302, b'{}'), (200, b'[]'), (200, b'{'),
                             (200, b'{"success":false}'), (200, b'x' * (512 * 1024 + 1))):
            response = MagicMock(status_code=status)
            response.__enter__.return_value = response
            response.iter_content.return_value = [body]
            with patch('elixirapp.pub2tools.requests.post', return_value=response), self.assertRaises(ValueError):
                fetch({})


@override_settings(PUB2TOOLS_URL='https://provider.example/api')
class PublicationImportTests(TestCase):
    def setUp(self):
        cache.clear()
        self.owner = User.objects.create_user('publication-owner')
        self.other = User.objects.create_user('publication-other')
        serializer = ResourceSerializer(data=FIXTURES['minimal'])
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.resource = serializer.save(owner=self.owner)
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)
        self.client.get('/register', **{'biotools.canonical': True})
        self.body = {'publication': 'https://doi.org/10.1093/nar/gkad347',
                     'documentUrl': 'https://example.org/guide', 'schemaRevision': resource_descriptor()['revision']}
        self.provider = self.enterContext(patch('elixirapp.pub2tools.fetch', return_value={
            'name': 'Publication suggestion', 'biotoolsID': 'protected', 'owner': 'other',
            'publication': [{'doi': '10.1093/nar/gkad347', 'metadata': {'title': 'Provider title'}}]}))

    def post(self, body=None, csrf=True):
        headers = {'HTTP_X_CSRFTOKEN': self.client.cookies['csrftoken'].value} if csrf else {}
        return self.client.post('/pub2tools-import', self.body if body is None else body,
                                content_type='application/json', HTTP_ACCEPT='application/json',
                                **headers, **{'biotools.canonical': True})

    def test_import_is_review_only_and_uses_provider_contract(self):
        self.body['biotoolsID'] = self.resource.biotoolsID
        before = Resource.objects.count()
        result = self.post()
        self.assertEqual(result.status_code, 200, result.content)
        self.assertEqual(result.json()['suggestions'], {'name': 'Publication suggestion',
            'publication': [{'doi': '10.1093/nar/gkad347'}]})
        self.provider.assert_called_once_with({'publicationIds': [{'doi': '10.1093/nar/gkad347'}],
                                               'webpageUrls': ['https://example.org/guide']})
        self.assertEqual(Resource.objects.count(), before)
        self.resource.refresh_from_db()
        self.assertNotEqual(self.resource.name, 'Publication suggestion')
        self.assertEqual(self.post().status_code, 429)

    def test_auth_csrf_schema_and_input_fail_before_provider_call(self):
        self.assertEqual(self.post(csrf=False).status_code, 403)
        self.assertEqual(self.post({**self.body, 'schemaRevision': 'stale'}).status_code, 409)
        self.assertEqual(self.post({**self.body, 'publication': 'https://example.org/article'}).status_code, 400)
        self.assertEqual(self.post({**self.body, 'documentUrl': 'https://127.0.0.1/'}).status_code, 400)
        self.client.force_login(self.other)
        self.assertEqual(self.post({**self.body, 'biotoolsID': self.resource.biotoolsID}).status_code, 403)
        self.client.logout()
        self.assertEqual(self.post(csrf=False).status_code, 401)
        self.provider.assert_not_called()

    def test_disabled_busy_and_provider_failures_leave_the_draft_alone(self):
        with override_settings(PUB2TOOLS_URL=''):
            self.assertEqual(self.post().status_code, 503)
        with patch('elixirapp.pub2tools.slots') as active:
            active.acquire.return_value = False
            self.assertEqual(self.post().status_code, 429)
        for error, status in ((requests.Timeout(), 504), (ValueError(), 502)):
            cache.clear()
            self.provider.side_effect = error
            self.assertEqual(self.post().status_code, status)
