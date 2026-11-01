from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from elasticsearch.exceptions import TransportError
from rest_framework.test import APIClient

from elixir.models import Domain, DomainNameLock, Resource, Workflow, WorkflowAnnotation
from elixir.serializers import ResourceSerializer, DomainSerializer
from elixirapp.html import canonical_family
from elixirapp.management_pages import domain_initial
from elixirapp.test_resource_editor_contract import FIXTURES
from elixirapp.workflows import annotation_box

CANONICAL = {'biotools.canonical': True}


@override_settings(GITHUB_ECOSYSTEM_ON=False)
class ManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('management-owner')
        cls.editor = User.objects.create_user('management-editor')
        cls.other = User.objects.create_user('management-other')
        cls.admin = User.objects.create_user('admin', is_superuser=True)
        serializer = ResourceSerializer(data={**deepcopy(FIXTURES['minimal']), 'biotoolsID': 'management-tool'})
        assert serializer.is_valid(), serializer.errors
        cls.resource = serializer.save(owner=cls.owner)
        cls.domain = Domain.objects.create(name='management-domain', title='Original', owner=cls.owner)
        cls.domain.editors.add(cls.editor)

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)
        self.es = self.enterContext(patch('elixir.view.resource.es'))
        self.enterContext(patch('elixir.view.domain.es', self.es))
        self.es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'management-tool'}]}}

    def load(self, path):
        return self.client.get(path, **CANONICAL)

    def post(self, path, data, csrf=True):
        headers = {'HTTP_X_CSRFTOKEN': self.client.cookies['csrftoken'].value} if csrf else {}
        return self.client.post(path, {key: '' if value is None else value for key, value in data.items()}, **headers, **CANONICAL)

    def record_body(self):
        response = self.load('/management-tool/manage')
        return {'revision': response.context['form']['revision'].value(), 'action': 'disown', 'confirm': 'on'}

    def test_record_confirmation_csrf_and_no_get_mutation(self):
        body = self.record_body()
        self.es.index.assert_not_called()
        self.assertEqual(self.post('/management-tool/manage', body, csrf=False).status_code, 403)
        self.assertEqual(self.post('/management-tool/manage', {**body, 'confirm': ''}).status_code, 400)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.owner, self.owner)

    def test_disown_updates_index_and_rejects_duplicate(self):
        body = self.record_body()
        self.assertEqual(self.post('/management-tool/manage', body).status_code, 302)
        current = Resource.objects.get(pk=self.resource.pk)
        self.assertEqual(current.owner, self.admin)
        self.assertEqual(self.es.index.call_args.kwargs['body']['owner'], 'admin')
        self.assertEqual(self.post('/management-tool/manage', body).status_code, 409)
        self.assertEqual(self.es.index.call_count, 1)

    def test_public_edit_access_cannot_disown_in_browser_or_token_api(self):
        self.resource.editPermission.type = 'public'
        self.resource.editPermission.save()
        self.client.force_login(self.other)
        body = self.record_body()
        self.assertEqual(self.post('/management-tool/manage', body).status_code, 403)
        api = APIClient()
        api.force_authenticate(self.other)
        response = api.post('/management-tool/disown', {}, format='json')
        self.assertEqual(response.status_code, 403)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.owner, self.owner)
        self.es.index.assert_not_called()

    def test_owner_change_after_load_and_hidden_record(self):
        body = self.record_body()
        Resource.objects.filter(pk=self.resource.pk).update(owner=self.other)
        self.assertEqual(self.post('/management-tool/manage', body).status_code, 409)
        Resource.objects.filter(pk=self.resource.pk).update(visibility=0)
        self.assertEqual(self.load('/management-tool/manage').status_code, 404)
        self.es.index.assert_not_called()

    def test_only_superuser_can_remove_and_index_failure_rolls_back(self):
        body = {**self.record_body(), 'action': 'delete'}
        self.assertEqual(self.post('/management-tool/manage', body).status_code, 403)
        self.client.force_login(self.admin)
        body = {**self.record_body(), 'action': 'delete'}
        self.es.delete.side_effect = TransportError(503, 'offline')
        self.assertEqual(self.post('/management-tool/manage', body).status_code, 503)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 1)
        self.es.delete.side_effect = None
        with patch('elixir.view.resource.notify_admins') as notify, self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.post('/management-tool/manage', body).status_code, 302)
        notify.assert_called_once()
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 0)
        self.assertEqual(self.load('/management-tool').status_code, 404)

    def test_disown_index_failure_retains_ownership(self):
        body = self.record_body()
        self.es.index.side_effect = TransportError(503, 'offline')
        self.assertEqual(self.post('/management-tool/manage', body).status_code, 503)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.owner, self.owner)

    def domain_body(self, user=None):
        if user:
            self.client.force_login(user)
        self.load('/edit-domain/management-domain')
        return {**domain_initial(Domain.objects.get(name='management-domain', visibility=1)), 'action': 'save'}

    def test_domain_aliases_and_owner_editor_membership_round_trip(self):
        for path in ('/domain-manager', '/subdomain', '/edit-domain/', '/edit-subdomain/',
                     '/edit-domain/management-domain', '/edit-subdomain/management-domain'):
            self.assertEqual(self.load(path).status_code, 200)
        body = self.domain_body()
        body.update(resources='management-tool\nmanagement-tool', editors='management-editor\nmanagement-editor', title='Changed')
        self.assertEqual(self.post('/edit-domain/management-domain', body).status_code, 302)
        current = Domain.objects.get(name='management-domain', visibility=1)
        self.assertEqual(current.resource.count(), 1)
        self.assertEqual(current.editors.count(), 1)
        self.assertEqual(current.owner, self.owner)
        self.assertEqual(self.es.index.call_args.kwargs['body']['resources'][0]['biotoolsID'], 'management-tool')
        self.assertEqual(self.post('/edit-domain/management-domain', body).status_code, 409)

    def test_domain_csrf_unknown_members_and_failed_index_retain_draft(self):
        body = self.domain_body()
        self.assertEqual(self.post('/edit-domain/management-domain', body, csrf=False).status_code, 403)
        body['resources'] = 'missing-tool'
        response = self.post('/edit-domain/management-domain', body)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'missing-tool', status_code=400)
        body['resources'] = 'management-tool'
        self.es.index.side_effect = TransportError(503, 'offline')
        self.assertEqual(self.post('/edit-domain/management-domain', body).status_code, 503)
        self.assertEqual(Domain.objects.filter(name='management-domain').count(), 1)
        self.assertEqual(Domain.objects.get(pk=self.domain.pk).visibility, 1)

    def test_domain_create_unknown_editor_and_duplicate_name(self):
        self.load('/edit-domain/')
        data = {'domain': 'new-domain', 'title': 'New', 'editors': 'missing-user'}
        self.assertEqual(self.post('/edit-domain/', data).status_code, 400)
        data['editors'] = 'management-editor'
        self.assertEqual(self.post('/edit-domain/', data).status_code, 302)
        self.assertEqual(self.post('/edit-domain/', data).status_code, 400)
        self.assertEqual(Domain.objects.filter(name='new-domain', visibility=1).count(), 1)

    def test_failed_domain_creation_rolls_back_lock_and_can_be_retried(self):
        self.load('/edit-domain/')
        data = {'domain': 'retry-domain', 'title': 'Preserved draft'}
        self.es.index.side_effect = TransportError(503, 'offline')
        response = self.post('/edit-domain/', data)
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, 'Preserved draft', status_code=503)
        self.assertFalse(Domain.objects.filter(name='retry-domain').exists())
        self.assertFalse(DomainNameLock.objects.filter(name='retry-domain').exists())
        self.es.index.side_effect = None
        self.assertEqual(self.post('/edit-domain/', data).status_code, 302)
        self.assertTrue(DomainNameLock.objects.filter(name='retry-domain').exists())

    def test_deleted_domain_name_can_be_reused_without_duplicate_active_rows(self):
        self.load('/edit-domain/')
        data = {'domain': 'reusable-domain', 'title': 'First version'}
        self.assertEqual(self.post('/edit-domain/', data).status_code, 302)
        self.load('/edit-domain/reusable-domain')
        current = Domain.objects.get(name='reusable-domain', visibility=1)
        self.assertEqual(self.post('/edit-domain/reusable-domain', {
            **domain_initial(current), 'action': 'delete', 'confirm_delete': 'on',
        }).status_code, 302)
        self.assertEqual(self.post('/edit-domain/', {**data, 'title': 'Second version'}).status_code, 302)
        self.assertEqual(Domain.objects.filter(name='reusable-domain', visibility=1).count(), 1)
        self.assertEqual(Domain.objects.filter(name='reusable-domain').count(), 2)
        self.assertEqual(DomainNameLock.objects.filter(name='reusable-domain').count(), 1)

    def test_domain_editor_cannot_change_editors_or_delete_via_api(self):
        api = APIClient()
        api.force_authenticate(self.editor)
        data = dict(DomainSerializer(self.domain).data)
        data['editors'] = ['management-other']
        self.assertEqual(api.put('/d/management-domain', data, format='json').status_code, 403)
        self.assertEqual(api.delete('/d/management-domain').status_code, 403)
        data['editors'] = ['management-editor']
        data['title'] = 'Editor change'
        self.assertEqual(api.put('/d/management-domain', data, format='json').status_code, 200)
        api.force_authenticate(self.other)
        self.assertEqual(api.put('/d/management-domain', data, format='json').status_code, 403)

    def test_domain_permission_revocation_and_protected_deletion(self):
        body = self.domain_body(self.editor)
        self.domain.editors.clear()
        self.assertEqual(self.post('/edit-domain/management-domain', body).status_code, 403)
        self.client.force_login(self.owner)
        body = self.domain_body()
        body['action'] = 'delete'
        self.assertEqual(self.post('/edit-domain/management-domain', body).status_code, 400)
        body['confirm_delete'] = 'on'
        self.assertEqual(self.post('/edit-domain/management-domain', body).status_code, 302)
        self.assertEqual(self.load('/edit-domain/management-domain').status_code, 404)
        protected = Domain.objects.create(name='covid-19', owner=self.owner)
        self.load('/edit-domain/covid-19')
        body = {**domain_initial(protected), 'action': 'delete', 'confirm_delete': 'on'}
        self.assertEqual(self.post('/edit-domain/covid-19', body).status_code, 403)

    def test_management_rollback_and_api_isolation(self):
        for path in ('/domain-manager', '/edit-domain/', '/edit-subdomain/', '/edit-domain/example', '/workflows', '/management-tool/manage'):
            self.assertEqual(canonical_family(path), 'management')
        self.assertIsNone(canonical_family('/api/d/example'))

    def test_workflow_filter_scaling_unsafe_links_and_native_details(self):
        workflow = Workflow.objects.create(biotoolsID='example-workflow', description='RNA analysis',
            image='workflows/example.png', image_width=1000, image_height=500)
        WorkflowAnnotation.objects.create(workflow=workflow, startX=100, startY=50, endX=400, endY=200,
            title='Alignment', description='Align reads', edam_term='Sequence alignment', url='javascript:alert(1)')
        with patch.object(workflow.image.storage, 'exists', return_value=True):
            response = self.load('/workflows?q=alignment')
        self.assertContains(response, 'left:10.0000%;top:10.0000%;width:30.0000%;height:30.0000%')
        self.assertContains(response, 'Inspect Alignment')
        self.assertNotContains(response, 'href="javascript:')
        self.assertContains(self.load('/workflows?q=not-found'), 'No matching workflows.')
        self.assertContains(self.load('/workflows'), 'workflow image is unavailable')
        invalid = SimpleNamespace(startX=float('nan'), startY=0, endX=50, endY=50)
        self.assertIsNone(annotation_box(invalid, 100, 100))

    def test_workflow_data_failure_is_not_an_empty_success(self):
        from django.db import DatabaseError
        with patch('elixirapp.workflows.Workflow.objects.all', side_effect=DatabaseError('offline')), self.assertLogs('elixirapp.workflows'):
            self.assertContains(self.load('/workflows'), 'could not be loaded', status_code=503)

    def test_management_identifiers_are_reserved_for_new_records(self):
        for identifier in ('domain-manager', 'edit-domain', 'edit-subdomain', 'workflows'):
            serializer = ResourceSerializer(data={**deepcopy(FIXTURES['minimal']), 'biotoolsID': identifier})
            self.assertFalse(serializer.is_valid(), identifier)
