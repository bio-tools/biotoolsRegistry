import json
import uuid

from django.contrib.auth.models import User
from django.test import Client, TestCase

from elixir.models import EditPermission, Resource, ResourceDraft


class ResourceDraftTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('draft-owner')
        self.other = User.objects.create_user('draft-other')
        self.client.force_login(self.owner)
        self.headers = {'biotools.canonical': True, 'HTTP_X_BIOTOOLS_USER': str(self.owner.pk)}
        self.id = uuid.uuid4()
        self.body = {'id': str(self.id), 'target': '', 'recordRevision': '', 'resource': {'name': 'Unfinished', 'topic': []}}

    def post(self, body=None):
        return self.client.post('/_resource-drafts/', json.dumps(body or self.body), content_type='application/json', **self.headers)

    def test_private_incomplete_draft_round_trip_and_stale_writes(self):
        self.assertEqual(self.post().status_code, 201)
        self.assertEqual(self.post().status_code, 200)
        self.assertEqual(Resource.objects.count(), 0)
        self.assertEqual(ResourceDraft.objects.count(), 1)
        item = self.client.get(f'/_resource-drafts/{self.id}/', **self.headers).json()
        self.assertEqual(item['resource'], self.body['resource'])
        self.assertEqual(len(self.client.get('/_resource-drafts/?target=', **self.headers).json()['items']), 1)
        body = {**self.body, 'resource': {'name': 'Revised'}}
        kwargs = {**self.headers, 'HTTP_IF_MATCH': item['revision']}
        response = self.client.put(f'/_resource-drafts/{self.id}/', json.dumps(body), content_type='application/json', **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.put(f'/_resource-drafts/{self.id}/', json.dumps(body), content_type='application/json', **kwargs).status_code, 409)
        self.assertEqual(self.client.delete(f'/_resource-drafts/{self.id}/', **kwargs).status_code, 409)
        self.assertEqual(self.client.delete(f'/_resource-drafts/{self.id}/', **{**kwargs, 'HTTP_IF_MATCH': response.json()['revision']}).status_code, 200)

    def test_another_account_cannot_read_or_modify_a_draft(self):
        self.post()
        self.client.force_login(self.other)
        headers = {'biotools.canonical': True, 'HTTP_X_BIOTOOLS_USER': str(self.other.pk)}
        self.assertEqual(self.client.get('/_resource-drafts/', **headers).json()['items'], [])
        self.assertEqual(self.client.get(f'/_resource-drafts/{self.id}/', **headers).status_code, 404)
        self.assertEqual(self.client.delete(f'/_resource-drafts/{self.id}/', **headers).status_code, 404)
        self.assertEqual(self.client.get('/_resource-drafts/', **self.headers).status_code, 409)
        self.client.logout()
        self.assertEqual(self.client.get(f'/_resource-drafts/{self.id}/', HTTP_ACCEPT='application/json', **headers).status_code, 401)

    def test_mutations_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        response = client.post('/_resource-drafts/', json.dumps(self.body), content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, 403)

    def test_cannot_create_an_edit_draft_for_someone_elses_record(self):
        Resource.objects.create(biotoolsID='private-editor-test', biotoolsCURIE='biotools:private-editor-test',
            name='Private editor test', description='Test record', homepage='https://example.org', owner=self.owner,
            editPermission=EditPermission.objects.create(type='private'))
        self.client.force_login(self.other)
        headers = {'biotools.canonical': True, 'HTTP_X_BIOTOOLS_USER': str(self.other.pk)}
        body = {**self.body, 'target': 'private-editor-test', 'recordRevision': 'a' * 64}
        response = self.client.post('/_resource-drafts/', json.dumps(body), content_type='application/json', **headers)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ResourceDraft.objects.exists())
