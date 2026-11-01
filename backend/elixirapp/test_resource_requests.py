from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connection
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from elixir.models import Resource, ResourceRequest
from elixir.serializers import ResourceSerializer, ResourceUpdateSerializer
from elixirapp.resource_editor import normalized, can_edit
from elixirapp.test_html import HTML_REQUEST
from elixirapp.test_resource_editor_contract import FIXTURES


@override_settings(GITHUB_ECOSYSTEM_ON=False)
class ResourceRequestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('request-owner', 'owner@example.org')
        cls.sender = User.objects.create_user('request-sender', 'sender@example.org')
        cls.other = User.objects.create_user('request-other', 'other@example.org')
        cls.admin = User.objects.create_user('request-admin', is_superuser=True)

    def setUp(self):
        self.es = self.enterContext(patch('elixir.view.resource.es'))
        self.es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'request-test'}]}}
        self.notify = self.enterContext(patch('elixir.view.resource.notify_resource_request'))
        serializer = ResourceSerializer(data=FIXTURES['minimal'])
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.resource = serializer.save(owner=self.owner)
        self.client = Client(enforce_csrf_checks=True)
        self.url = '/requests/tool/' + self.resource.biotoolsID + '/'

    def login(self, user):
        self.client.force_login(user)
        self.client.get('/requests/', **HTML_REQUEST)

    def post(self, url, data):
        return self.client.post(url, data, HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST)

    def create(self, kind='editing'):
        self.login(self.sender)
        response = self.post(self.url, {'type': kind})
        self.assertEqual(response.status_code, 302, response.content)
        return ResourceRequest.objects.latest('pk')

    def conclude(self, item, accept='true'):
        return self.post('/requests/conclude/', {'requestId': item.requestId, 'accept': accept})

    def test_session_forms_grant_rights_and_show_completed_results(self):
        item = self.create()
        self.notify.assert_called_once()
        self.assertContains(self.client.get('/requests/', **HTML_REQUEST), 'Pending')
        self.login(self.owner)
        self.assertContains(self.client.get('/requests/', **HTML_REQUEST), self.sender.email)
        self.assertEqual(self.conclude(item).status_code, 302)
        self.resource.refresh_from_db()
        self.assertTrue(can_edit(self.sender, self.resource))
        self.es.index.assert_called_once()
        self.assertNotContains(self.client.get('/requests/', **HTML_REQUEST), self.sender.email)
        self.assertContains(self.client.get('/requests/?completed=1', **HTML_REQUEST), 'Accepted')
        self.conclude(item, 'false')
        item.refresh_from_db()
        self.assertTrue(item.accepted)

    def test_ownership_transfer_moves_pending_requests_and_revokes_old_owner(self):
        transfer = self.create('ownership')
        pending = self.create('editing')
        self.login(self.owner)
        self.conclude(transfer)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.owner, self.sender)
        self.assertFalse(can_edit(self.owner, self.resource))
        self.assertNotContains(self.client.get('/requests/', **HTML_REQUEST), 'Accept</button>')
        self.conclude(pending)
        pending.refresh_from_db()
        self.assertFalse(pending.completed)
        self.login(self.sender)
        self.assertContains(self.client.get('/requests/', **HTML_REQUEST), 'Accept</button>')
        self.conclude(pending, 'false')
        pending.refresh_from_db()
        self.assertTrue(pending.completed)
        self.assertFalse(pending.accepted)

    def test_requests_follow_current_resource_after_replacement(self):
        item = self.create('ownership')
        self.login(self.owner)
        url = '/editor/tool/' + self.resource.biotoolsID + '/'
        config = self.client.get(url, **HTML_REQUEST).context['editor_config']
        payload = normalized(config['resource'], ResourceUpdateSerializer())
        payload['name'] = 'Updated before request decision'
        response = self.client.post(url + 'save/', {'resource': payload, 'revision': config['revision'],
                                    'schemaRevision': config['schemaRevision']},
                                    content_type='application/json', HTTP_ACCEPT='application/json',
                                    HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST)
        self.assertEqual(response.status_code, 200, response.content)
        self.conclude(item)
        current = Resource.objects.get(biotoolsID=self.resource.biotoolsID, visibility=1)
        self.assertEqual(current.owner, self.sender)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.owner, self.owner)
        item.refresh_from_db()
        self.assertEqual(item.resource_id, current.pk)

    def test_unauthorized_invalid_csrf_expiry_and_api_token_guards(self):
        item = self.create('ownership')
        self.login(self.other)
        self.conclude(item)
        item.refresh_from_db()
        self.assertFalse(item.completed)
        self.login(self.owner)
        self.assertEqual(self.client.post('/requests/conclude/', {'requestId': item.requestId, 'accept': 'true'},
                                         **HTML_REQUEST).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get('/requests/', **HTML_REQUEST).status_code, 302)
        self.assertEqual(self.client.post('/requests/conclude/', HTTP_ACCEPT='application/json',
                                         **HTML_REQUEST).status_code, 401)
        api = APIClient()
        self.assertEqual(api.get('/request').status_code, 401)
        token = Token.objects.create(user=self.owner)
        api.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = api.post('/request/conclude', {'requestId': item.requestId, 'accept': 'invalid'}, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        item.refresh_from_db()
        self.assertFalse(item.completed)
        self.assertEqual(api.post('/request/conclude', {'requestId': [], 'accept': True}, format='json').status_code, 400)
        self.assertEqual(api.put('/request', [], format='json').status_code, 400)

    def test_admin_decline_public_access_and_index_failure_rollback(self):
        item = self.create()
        self.login(self.admin)
        self.es.index.side_effect = RuntimeError('offline')
        self.conclude(item)
        item.refresh_from_db()
        self.resource.refresh_from_db()
        self.assertFalse(item.completed)
        self.assertFalse(can_edit(self.sender, self.resource))
        self.es.index.side_effect = None
        self.resource.editPermission.type = 'public'
        self.resource.editPermission.save()
        self.conclude(item)
        self.resource.editPermission.refresh_from_db()
        self.assertEqual(self.resource.editPermission.type, 'public')
        self.assertTrue(can_edit(self.other, self.resource))

    def test_invalid_request_has_no_side_effects(self):
        self.login(self.sender)
        self.assertEqual(self.post(self.url, {'type': 'invalid'}).status_code, 400)
        self.assertEqual(self.post('/requests/tool/absent/', {'type': 'editing'}).status_code, 404)
        self.assertFalse(ResourceRequest.objects.exists())
        self.notify.assert_not_called()

    def test_api_replacement_rechecks_ownership_after_locking(self):
        stale = self.resource
        payload = normalized(ResourceSerializer(stale).data, ResourceUpdateSerializer())
        Resource.objects.filter(pk=stale.pk).update(owner=self.sender)
        api = APIClient()
        api.force_authenticate(user=self.owner)
        with patch('elixir.view.resource.get_tool', return_value=stale), CaptureQueriesContext(connection) as queries:
            response = api.put('/t/' + stale.biotoolsID, payload, format='json')
        self.assertEqual(response.status_code, 403, response.data)
        self.assertTrue(any('FOR UPDATE' in query['sql'] for query in queries))
        self.assertEqual(Resource.objects.get(pk=stale.pk).owner, self.sender)
        self.assertEqual(Resource.objects.filter(biotoolsID=stale.biotoolsID).count(), 1)
        self.es.index.assert_not_called()
