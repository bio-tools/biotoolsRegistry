import json
from unittest.mock import MagicMock, patch

import requests
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client, SimpleTestCase, TestCase, override_settings

from elixir.models import Resource
from elixir.resource_ui import resource_descriptor
from elixir.serializers import ResourceSerializer
from elixirapp.github_bridge import MAX_RESPONSE, fetch, repository, suggestions
from elixirapp.test_resource_editor_contract import FIXTURES


class BridgeContractTests(SimpleTestCase):
    def test_exact_repository_urls(self):
        for value in ('https://github.com/bio-tools/registry', 'https://github.com/bio-tools/registry.git/'):
            self.assertEqual(repository(value), ('bio-tools', 'registry'))
        for value in ('https://github.com.evil.test/user/repo', 'https://user@github.com/user/repo',
                      'https://github.com:443/user/repo', 'http://github.com/user/repo',
                      'https://github.com/user/repo/tree/main', 'https://github.com/user/repo?token=x',
                      'https://github.com/user/%2e%2e', 'https://github.com/user/..', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                repository(value)

    def test_unknown_protected_nested_and_incompatible_suggestions_are_explained(self):
        accepted, rejected = suggestions({'name': 'Suggested name', 'biotoolsID': 'hijacked', 'owner': 'stranger',
            'unknown': 'value', 'editPermission': {'type': 'public'}, 'license': 'invented-license',
            'publication': [{'doi': '10.1093/bioinformatics/btv111', 'metadata': {'title': 'Forged'}}],
            'otherID': [{'value': 'biotools:replacement', 'type': 'Primary'}], 'description': ['bad type']}, resource_descriptor())
        self.assertEqual(accepted, {'name': 'Suggested name'})
        self.assertEqual(len(rejected), 8)

    @override_settings(GITHUB_BRIDGE_URL='http://bridge:8000/github-to-biotools')
    def test_service_object_string_size_redirect_and_json_boundaries(self):
        for raw in ({'name': 'Suggested'}, json.dumps({'name': 'Suggested'})):
            response = MagicMock(status_code=201)
            response.__enter__.return_value = response
            response.iter_content.return_value = [json.dumps(raw).encode()]
            with patch('elixirapp.github_bridge.requests.post', return_value=response) as post:
                self.assertEqual(fetch({'owner': 'bio-tools', 'repo': 'registry'}), {'name': 'Suggested'})
                self.assertFalse(post.call_args.kwargs['allow_redirects'])
                self.assertEqual(post.call_args.kwargs['timeout'], (5, 45))
        for status, content in ((302, b'{}'), (200, b'[]'), (200, b'{'), (200, b'x' * (MAX_RESPONSE + 1))):
            response = MagicMock(status_code=status)
            response.__enter__.return_value = response
            response.iter_content.return_value = [content]
            with patch('elixirapp.github_bridge.requests.post', return_value=response), self.assertRaises(ValueError):
                fetch({})


@override_settings(GITHUB_BRIDGE_URL='http://bridge:8000/github-to-biotools')
class BridgeTransportTests(TestCase):
    def setUp(self):
        cache.clear()
        self.owner = User.objects.create_user('bridge-owner')
        self.other = User.objects.create_user('bridge-other')
        serializer = ResourceSerializer(data=FIXTURES['minimal'])
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.resource = serializer.save(owner=self.owner)
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)
        self.client.get('/register', **{'biotools.canonical': True})
        self.body = {'url': 'https://github.com/bio-tools/registry', 'schemaRevision': resource_descriptor()['revision']}
        self.provider = self.enterContext(patch('elixirapp.github_bridge.fetch', return_value={'name': 'Suggestion', 'owner': 'bad'}))

    def post(self, body=None, csrf=True):
        headers = {'HTTP_X_CSRFTOKEN': self.client.cookies['csrftoken'].value} if csrf else {}
        return self.client.post('/github-to-biotools', self.body if body is None else body, content_type='application/json',
                               HTTP_ACCEPT='application/json', **headers, **{'biotools.canonical': True})

    def test_import_never_writes_and_uses_verified_service_parameter(self):
        count = Resource.objects.count()
        self.body['biotoolsID'] = self.resource.biotoolsID
        response = self.post()
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['suggestions'], {'name': 'Suggestion'})
        self.assertEqual(response.json()['rejected'][0]['path'], 'owner')
        self.provider.assert_called_once_with({'owner': 'bio-tools', 'repo': 'registry', 'biotools_id': self.resource.biotoolsID})
        self.assertEqual(Resource.objects.count(), count)
        self.resource.refresh_from_db()
        self.assertNotEqual(self.resource.name, 'Suggestion')
        self.assertEqual(self.post().status_code, 429)

    def test_session_csrf_permissions_schema_and_url_are_enforced_before_provider_call(self):
        self.assertEqual(self.post(csrf=False).status_code, 403)
        self.assertEqual(self.post({**self.body, 'schemaRevision': 'old'}).status_code, 409)
        self.assertEqual(self.post({**self.body, 'url': 'https://evil.test/user/repo'}).status_code, 400)
        self.client.force_login(self.other)
        self.assertEqual(self.post({**self.body, 'biotoolsID': self.resource.biotoolsID}).status_code, 403)
        self.client.logout()
        self.assertEqual(self.post(csrf=False).status_code, 401)
        self.provider.assert_not_called()

    def test_disabled_busy_timeout_and_invalid_response(self):
        with override_settings(GITHUB_BRIDGE_URL=''):
            self.assertEqual(self.post().status_code, 503)
        with patch('elixirapp.github_bridge.slots') as slots:
            slots.acquire.return_value = False
            self.assertEqual(self.post().status_code, 429)
        self.provider.assert_not_called()
        for error, status in ((requests.Timeout(), 504), (ValueError(), 502)):
            cache.clear()
            self.provider.side_effect = error
            self.assertEqual(self.post().status_code, status)
