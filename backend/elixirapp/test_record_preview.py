import json
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve

from elixir.resource_ui import resource_descriptor
from elixirapp.record_preview import preview


@override_settings(ROOT_URLCONF='elixirapp.canonical_editor_urls')
class RecordPreviewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.descriptor = resource_descriptor()
        self.draft = {
            'biotoolsID': 'draft-id', 'name': 'Unsaved name', 'homepage': 'https://example.org',
            'description': 'An unsaved description.',
            'topic': [{'uri': 'http://edamontology.org/topic_0003', 'term': 'Example topic'}],
            'function': [{'operation': [{'uri': 'http://edamontology.org/operation_0004', 'term': 'Example operation'}]}],
            'publication': [{'doi': '10.1234/example', 'metadata': {'title': 'Example publication', 'abstract': 'Example abstract'}}],
            'editPermission': {'type': 'private', 'authors': []},
        }

    def request(self, resource=None, revision=None, user=None):
        request = self.factory.post('/register/record-preview/', data=json.dumps({
            'resource': resource if resource is not None else self.draft,
            'schemaRevision': revision or self.descriptor['revision'],
        }), content_type='application/json', HTTP_ACCEPT='application/json')
        request.user = user or SimpleNamespace(is_authenticated=True, username='editor')
        request.canonical = True
        return request

    def test_renders_public_detail_from_unsaved_values_without_writes(self):
        response = preview(self.request())
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        for text in ('Unsaved name', 'An unsaved description.', 'Example topic', 'Example operation', 'Example publication'):
            self.assertIn(text, body)
        self.assertNotIn('editPermission', body)
        self.assertNotIn('badge.dimensions.ai', body)

    def test_canonical_preview_routes_reach_the_preview_view(self):
        self.assertIs(resolve('/register/record-preview/').func, preview)
        self.assertIs(resolve('/draft-id/edit/record-preview/').func, preview)

    @override_settings(ROOT_URLCONF='elixirapp.html_urls')
    def test_legacy_preview_routes_reach_the_preview_view(self):
        self.assertIs(resolve('/editor/new/record-preview/').func, preview)
        self.assertIs(resolve('/editor/tool/draft-id/record-preview/').func, preview)

    def test_requires_authentication_and_existing_record_permission(self):
        self.assertEqual(preview(self.request(user=AnonymousUser())).status_code, 401)
        with patch('elixirapp.record_preview.existing', side_effect=PermissionDenied):
            with self.assertRaises(PermissionDenied):
                preview(self.request(), identifier='draft-id')

    def test_rejects_invalid_shapes_and_schema_revisions(self):
        self.assertEqual(preview(self.request(resource={'topic': 'not a list'})).status_code, 400)
        self.assertEqual(preview(self.request(revision='old')).status_code, 409)

    def test_escapes_draft_content(self):
        response = preview(self.request(resource={'name': '<script>alert(1)</script>', 'description': '', 'homepage': ''}))
        self.assertNotIn(b'<script>alert(1)</script>', response.content)
        self.assertIn(b'&lt;script&gt;', response.content)
