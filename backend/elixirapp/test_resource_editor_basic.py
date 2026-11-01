from copy import deepcopy
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

from elixir.models import Domain, DomainResource, OtherID, PublicationMetadata, Resource
from elixir.serializers import ResourceSerializer, ResourceUpdateSerializer
from elixir.resource_ui import resource_descriptor, SchemaUnavailable
from elixirapp.resource_editor import normalized, unrelated
from elixirapp.test_edam import seed_ontology
from elixirapp.test_html import HTML_REQUEST
from elixirapp.test_resource_editor_contract import FIXTURES


@override_settings(GITHUB_ECOSYSTEM_ON=False)
class BasicEditorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_ontology()
        cls.owner = User.objects.create_user('contract-owner')
        cls.author = User.objects.create_user('contract-author')
        cls.other = User.objects.create_user('unrelated-user')
        cls.admin = User.objects.create_user('editor-admin', is_superuser=True)
        serializer = ResourceSerializer(data={**FIXTURES['minimal'], 'biotoolsID': 'contract-related'})
        assert serializer.is_valid(), serializer.errors
        serializer.save(owner=cls.owner)

    def setUp(self):
        self.es = self.enterContext(patch('elixir.view.resource.es'))
        self.es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'editor-test'}]}}
        self.enterContext(patch('elixir.signals.update_publication'))
        serializer = ResourceSerializer(data=deepcopy(FIXTURES['rich']))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.resource = serializer.save(owner=self.owner)
        self.url = '/editor/tool/contract-rich/'
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)

    def load(self):
        response = self.client.get(self.url, **HTML_REQUEST)
        self.assertEqual(response.status_code, 200)
        config = response.context['editor_config']
        return {'resource': normalized(config['resource'], ResourceUpdateSerializer()), 'revision': config['revision'],
                'schemaRevision': config['schemaRevision']}

    def save(self, body, url=None, **kwargs):
        if isinstance(body, dict) and 'revision' in body:
            body.setdefault('schemaRevision', resource_descriptor()['revision'])
        return self.client.post(url or self.url + 'save/', body, content_type='application/json',
            HTTP_ACCEPT='application/json', HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST, **kwargs)

    def test_schema_conflict_and_unavailable_metadata_never_mutate_the_record(self):
        body = self.load()
        body['resource']['name'] = 'Uncommitted draft'
        body['schemaRevision'] = 'old-schema'
        self.assertEqual(self.save(body).status_code, 409)
        body['schemaRevision'] = None
        self.assertEqual(self.save(body).status_code, 409)
        with patch('elixirapp.resource_editor.resource_descriptor', side_effect=SchemaUnavailable('Unavailable')):
            page = self.client.get(self.url, **HTML_REQUEST)
            self.assertIsNone(page.context['editor_config']['schema'])
            self.assertEqual(page.context['editor_config']['resource']['name'], self.resource.name)
            self.assertIn('no-store', page.headers['Cache-Control'])
            self.assertEqual(self.save(body).status_code, 503)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 1)
        self.es.index.assert_not_called()

    def test_validation_only_checks_schema_permissions_and_preservation_without_writes(self):
        body = self.load()
        count = Resource.objects.count()
        response = self.save(body, url=self.url + 'validate/')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()['valid'])
        self.assertEqual(Resource.objects.count(), count)
        self.es.index.assert_not_called()
        body['resource']['homepage'] = 'not-a-url'
        self.assertEqual(self.save(body, url=self.url + 'validate/').status_code, 400)
        body = self.load()
        body['resource']['owner'] = 'somebody-else'
        self.assertEqual(self.save(body, url=self.url + 'validate/').status_code, 400)
        body = self.load()
        body['schemaRevision'] = 'stale'
        self.assertEqual(self.save(body, url=self.url + 'validate/').status_code, 409)
        body = self.load()
        self.client.force_login(self.other)
        self.assertEqual(self.save(body, url=self.url + 'validate/').status_code, 403)
        self.es.index.assert_not_called()

    def test_missing_schema_revision_cannot_bypass_the_version_check(self):
        body = self.load()
        del body['schemaRevision']
        response = self.client.post(self.url + 'save/', body, content_type='application/json',
            HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST)
        self.assertEqual(response.status_code, 400)
        self.es.index.assert_not_called()

    def test_repeated_save_keeps_version_timestamp_index_and_revision(self):
        first = self.save(self.load())
        self.assertEqual(first.status_code, 200, first.content)
        self.assertFalse(first.json()['no_changes'])  # Establish a hash for older records.
        body = self.load()
        count = Resource.objects.count()
        self.es.reset_mock()
        second = self.save(body)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertTrue(second.json()['no_changes'])
        self.assertEqual(second.json()['revision'], body['revision'])
        self.assertEqual(second.json()['resource']['lastUpdate'], body['resource']['lastUpdate'])
        self.assertEqual(Resource.objects.count(), count)
        self.es.index.assert_not_called()
        body['resource']['name'] = 'A meaningful change'
        changed = self.save(body)
        self.assertEqual(changed.status_code, 200, changed.content)
        self.assertFalse(changed.json()['no_changes'])
        self.assertEqual(Resource.objects.count(), count + 1)

    def test_unchanged_save_still_checks_validation_permissions_and_staleness(self):
        self.assertEqual(self.save(self.load()).status_code, 200)
        body = self.load()
        invalid = deepcopy(body)
        invalid['resource']['homepage'] = ''
        self.assertEqual(self.save(invalid).status_code, 400)
        stale = deepcopy(body)
        stale['revision'] = 'stale'
        self.assertEqual(self.save(stale).status_code, 409)
        self.client.force_login(self.other)
        self.assertEqual(self.save(body).status_code, 403)

    def test_public_api_unchanged_response_and_permission_changes(self):
        from rest_framework.test import APIRequestFactory, force_authenticate
        from elixir.view.resource import ResourceDetail
        payload = self.load()['resource']
        def put(value):
            request = APIRequestFactory().put('/t/contract-rich', deepcopy(value), format='json')
            force_authenticate(request, user=self.owner)
            return ResourceDetail.as_view()(request, biotoolsID=self.resource.biotoolsID)
        self.assertEqual(put(payload).status_code, 200)
        self.es.reset_mock()
        response = put(payload)
        self.assertEqual(response.data, {'no_changes': True, 'detail': 'No changes detected.'})
        self.es.index.assert_not_called()
        payload['editPermission'] = {'type': 'public', 'authors': []}
        response = put(payload)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['editPermission']['type'], 'public')
        self.es.index.assert_called_once()

    def test_rich_basic_edit_preserves_all_unrelated_metadata_and_relationships(self):
        domain = Domain.objects.create(name='editor-domain', owner=self.owner)
        DomainResource.objects.create(domain=domain, biotoolsID=self.resource.biotoolsID, name=self.resource.name)
        before = ResourceSerializer(self.resource).data
        body = self.load()
        body['resource']['name'] = 'New basic name'
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        after = response.json()['resource']
        self.assertEqual(after['name'], 'New basic name')
        self.assertEqual(unrelated(after), unrelated(before))
        self.assertEqual(domain.resource.count(), 1)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 0)
        self.assertNotEqual(response.json()['revision'], body['revision'])
        self.es.index.assert_called_once()
        self.assertEqual(self.es.index.call_args.kwargs['refresh'], 'wait_for')

    def test_authorized_create_readback_and_unique_id_validation(self):
        self.client.get('/editor/new/', **HTML_REQUEST)
        body = {'resource': {**FIXTURES['minimal'], 'biotoolsID': 'new-basic', 'toolType': ['Web application']}, 'revision': None}
        response = self.save(body, '/editor/new/save/')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(self.es.index.call_args.kwargs['refresh'], 'wait_for')
        self.assertEqual(response.json()['resource']['owner'], self.owner.username)
        self.assertEqual(response.json()['resource']['editPermission']['type'], 'private')
        self.assertEqual(response.json()['editUrl'], '/editor/tool/new-basic/')
        rejected = self.save(body, '/editor/new/save/')
        self.assertEqual(rejected.status_code, 400)
        self.assertIn('biotoolsID', rejected.json())
        self.assertEqual(Resource.objects.filter(biotoolsID='new-basic', visibility=1).count(), 1)

    def test_server_enforces_owner_group_public_superuser_and_anonymous_access(self):
        for user in (self.owner, self.author, self.admin):
            self.client.force_login(user)
            body = self.load()
            body['resource']['description'] = 'Authorized basic description update.'
            self.assertEqual(self.save(body).status_code, 200)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.url, **HTML_REQUEST).status_code, 403)
        self.assertEqual(self.save(body).status_code, 403)
        current = Resource.objects.get(biotoolsID='contract-rich', visibility=1)
        current.editPermission.type = 'public'
        current.editPermission.save()
        self.assertEqual(self.save(self.load()).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get('/editor/new/', **HTML_REQUEST).status_code, 302)
        for url in ('/editor/new/save/', self.url + 'save/'):
            response = self.client.post(url, {}, content_type='application/json', HTTP_ACCEPT='application/json', **HTML_REQUEST)
            self.assertEqual(response.status_code, 401)

    def test_private_editor_and_session_csrf_enforcement(self):
        self.resource.editPermission.type = 'private'
        self.resource.editPermission.save()
        body = self.load()
        missing = self.client.post(self.url + 'save/', body, content_type='application/json', HTTP_ACCEPT='application/json', **HTML_REQUEST)
        self.assertEqual(missing.status_code, 403)
        self.assertEqual(self.save(body, HTTP_ORIGIN='https://untrusted.invalid').status_code, 403)
        self.client.force_login(self.author)
        self.assertEqual(self.client.get(self.url, **HTML_REQUEST).status_code, 403)
        self.assertEqual(self.save(body).status_code, 403)
        self.es.index.assert_not_called()

    def test_authoritative_handler_rechecks_permissions_after_page_and_facade_checks(self):
        body = self.load()
        with patch('elixir.permissions.HasEditPermissionToEditResourceOrReadOnly.has_object_permission',
                   side_effect=[True, False]):
            self.assertEqual(self.save(body).status_code, 403)
        self.es.index.assert_not_called()

    def test_precise_basic_validation_does_not_change_existing_record(self):
        body = self.load()
        body['resource'].update(name='Invalid / name', homepage='not-a-homepage', description='short', toolType=['Unknown'])
        response = self.save(body)
        self.assertEqual(response.status_code, 400, response.content)
        self.assertTrue({'name', 'homepage', 'description', 'toolType'} <= response.json().keys())
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 1)
        self.assertEqual(self.resource.name, FIXTURES['rich']['name'])
        self.es.index.assert_not_called()

    def test_out_of_scope_changes_omissions_unknown_fields_and_renames_are_rejected(self):
        original = self.load()
        for key, value in [('owner', self.other.username), ('biotoolsID', 'renamed'),
                           ('unknown', 'unsafe')]:
            with self.subTest(key=key):
                body = deepcopy(original)
                body['resource'][key] = value
                self.assertEqual(self.save(body).status_code, 400)
        del original['resource']['owner']
        self.assertEqual(self.save(original).status_code, 400)
        self.es.index.assert_not_called()

    def test_owner_and_admin_can_edit_permissions_without_changing_schema_or_history(self):
        for user in (self.owner, self.admin):
            self.client.force_login(user)
            for mode in ('private', 'public', 'group'):
                with self.subTest(user=user.username, mode=mode):
                    config = self.client.get(self.url, **HTML_REQUEST).context['editor_config']
                    self.assertTrue(config['canManagePermissions'])
                    before = config['resource']
                    body = self.load()
                    body['resource']['editPermission'] = {'type': mode, 'authors': [self.author.username, self.other.username]}
                    response = self.save(body)
                    self.assertEqual(response.status_code, 200, response.content)
                    after = response.json()['resource']
                    self.assertEqual(after['editPermission']['type'], mode)
                    self.assertEqual(set(after['editPermission']['authors']), {self.author.username, self.other.username})
                    self.assertEqual(unrelated(before, {'editPermission'}), unrelated(after, {'editPermission'}))
        self.resource.refresh_from_db()
        self.assertEqual(ResourceSerializer(self.resource).data['editPermission'], FIXTURES['rich']['editPermission'])

    def test_nonowners_cannot_change_permissions_and_revocation_is_immediate(self):
        self.client.force_login(self.author)
        config = self.client.get(self.url, **HTML_REQUEST).context['editor_config']
        self.assertFalse(config['canManagePermissions'])
        body = self.load()
        for permission in ({'type': 'public'}, {'type': 'group', 'authors': [self.other.username]}, None):
            denied = deepcopy(body)
            denied['resource']['editPermission'] = permission
            self.assertEqual(self.save(denied).status_code, 403)
        self.es.index.assert_not_called()
        body['resource']['name'] = 'Allowed group edit'
        self.assertEqual(self.save(body).status_code, 200)
        stale_author = self.load()
        self.client.force_login(self.owner)
        body = self.load()
        body['resource']['editPermission'] = {'type': 'group', 'authors': [self.other.username]}
        self.assertEqual(self.save(body).status_code, 200)
        self.client.force_login(self.author)
        self.assertEqual(self.save(stale_author).status_code, 403)
        self.assertEqual(self.client.get(self.url, **HTML_REQUEST).status_code, 403)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.url, **HTML_REQUEST).status_code, 200)
        self.client.force_login(self.owner)
        body = self.load()
        body['resource']['editPermission'] = {'type': 'public', 'authors': []}
        self.assertEqual(self.save(body).status_code, 200)
        self.client.force_login(self.author)
        body = self.load()
        body['resource']['editPermission']['type'] = 'private'
        self.assertEqual(self.save(body).status_code, 403)

    def test_permission_validation_is_precise_and_create_supports_group_permissions(self):
        original = self.load()
        for permission in (None, [], 'public', {}, {'type': 'unknown'},
                           {'type': 'group', 'authors': ['no-such-editor-user']},
                           {'type': 'group', 'authors': [None]}, {'type': 'group', 'authors': [{}]},
                           {'type': 'group', 'authors': 1}):
            with self.subTest(permission=permission):
                body = deepcopy(original)
                body['resource']['editPermission'] = permission
                response = self.save(body)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn('editPermission', response.json())
        self.es.index.assert_not_called()
        permission = {'type': 'group', 'authors': [self.author.username]}
        response = self.save({'resource': {**FIXTURES['minimal'], 'biotoolsID': 'permission-created',
                             'editPermission': permission}, 'revision': None}, '/editor/new/save/')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['resource']['editPermission'], permission)
        self.assertTrue(response.json()['canManagePermissions'])
        self.client.force_login(self.author)
        self.assertEqual(self.client.get('/editor/tool/permission-created/', **HTML_REQUEST).status_code, 200)

    def test_permission_changes_require_csrf_and_current_revision(self):
        body = self.load()
        body['resource']['editPermission'] = {'type': 'public', 'authors': []}
        response = self.client.post(self.url + 'save/', body, content_type='application/json', HTTP_ACCEPT='application/json', **HTML_REQUEST)
        self.assertEqual(response.status_code, 403)
        self.es.index.assert_not_called()
        self.assertEqual(self.save(body).status_code, 200)
        body['resource']['editPermission']['type'] = 'private'
        self.assertEqual(self.save(body).status_code, 409)
        self.assertEqual(self.load()['resource']['editPermission'], {'type': 'public', 'authors': []})

    def test_existing_user_lookup_returns_usernames_only(self):
        response = self.client.get('/user-list/?format=json&term=contract')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json())
        self.assertTrue(all(set(item) == {'username'} for item in response.json()))
        self.assertIn({'username': self.author.username}, response.json())

    def test_stale_version_is_rejected_and_refresh_produces_a_new_revision(self):
        body = self.load()
        changed = deepcopy(body)
        changed['resource']['name'] = 'First update'
        self.assertEqual(self.save(changed).status_code, 200)
        body['resource']['name'] = 'Stale update'
        response = self.save(body)
        self.assertEqual(response.status_code, 409)
        self.assertIn('changed since', response.json()['detail'])
        self.assertEqual(Resource.objects.get(biotoolsID='contract-rich', visibility=1).name, 'First update')

    def test_enrichment_is_preserved_without_sharing_metadata_with_history(self):
        publication = self.resource.publication.first()
        publication.metadata = PublicationMetadata.objects.create(title='Must be preserved')
        publication.metadata.authors.create(name='Original Author')
        publication.save()
        self.resource.homepage_status = 2
        self.resource.elixir_badge = 4
        self.resource.save()
        before = ResourceSerializer(self.resource).data
        body = self.load()
        body['resource']['name'] = 'Enriched edit'
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        after = response.json()['resource']
        self.assertEqual(unrelated(after), unrelated(before))
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 0)
        current = Resource.objects.get(biotoolsID=self.resource.biotoolsID, visibility=1).publication.first()
        self.assertNotEqual(current.metadata_id, publication.metadata_id)
        current.metadata.title = 'Refreshed later'
        current.metadata.save()
        current.metadata.authors.all().delete()
        publication.metadata.refresh_from_db()
        self.assertEqual(publication.metadata.title, 'Must be preserved')
        self.assertEqual(list(publication.metadata.authors.values_list('name', flat=True)), ['Original Author'])

    def test_forged_enrichment_and_protected_identifier_changes_are_rejected(self):
        publication = self.resource.publication.first()
        publication.metadata = PublicationMetadata.objects.create(title='Authoritative title')
        publication.save()
        OtherID.objects.create(resource=self.resource, value='BIOTOOLS:previous-id', type='biotoolsCURIE')
        original = self.load()
        changes = [
            ('publication', [{**original['resource']['publication'][0], 'metadata': {'title': 'Forged'}}]),
            ('publication', [{**original['resource']['publication'][0], 'pmid': '99999'}]),
            ('otherID', []), ('otherID', [{'value': 'biotools:forged', 'type': 'biotoolsCURIE'}]),
            ('elixir_badge', 4), ('homepage_status', 2),
        ]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                body = deepcopy(original)
                body['resource'][field] = value
                self.assertIn(self.save(body).status_code, (400, 409))
        self.es.index.assert_not_called()

    def test_protected_identifiers_keep_error_indices_and_survive_owner_and_admin_saves(self):
        OtherID.objects.create(resource=self.resource, value='BIOTOOLS:previous-id', type='biotoolsCURIE')
        for user in (self.owner, self.admin):
            self.client.force_login(user)
            body = self.load()
            body['resource']['otherID'].reverse()
            body['resource']['otherID'].append({'value': 'invalid'})
            response = self.save(body)
            self.assertEqual(response.status_code, 400, response.content)
            self.assertEqual(response.json()['otherID'][:2], [{}, {}])
            self.assertIn('value', response.json()['otherID'][2])
            body['resource']['otherID'].pop()
            response = self.save(body)
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(normalized(response.json()['resource'], ResourceUpdateSerializer())['otherID'], body['resource']['otherID'])

    def test_unexpected_metadata_loss_rolls_back_before_indexing(self):
        original_create = ResourceUpdateSerializer.create
        def losing_create(serializer, values):
            resource = original_create(serializer, values)
            resource.credit.all().delete()
            return resource
        body = self.load()
        with patch.object(ResourceUpdateSerializer, 'create', losing_create):
            self.assertEqual(self.save(body).status_code, 409)
        self.assertEqual(Resource.objects.filter(biotoolsID='contract-rich').count(), 1)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 1)
        self.assertEqual(self.resource.credit.count(), 1)
        self.es.index.assert_not_called()

    def test_index_failure_rolls_back_database_and_malformed_input_is_rejected(self):
        publication = self.resource.publication.first()
        publication.metadata = PublicationMetadata.objects.create(title='Retained after failure')
        publication.metadata.authors.create(name='Retained Author')
        publication.save()
        metadata_count = PublicationMetadata.objects.count()
        body = self.load()
        self.es.index.side_effect = RuntimeError('Index unavailable')
        with self.assertLogs('elixirapp.resource_editor', level='ERROR'):
            self.assertEqual(self.save(body).status_code, 503)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 1)
        self.assertEqual(Resource.objects.filter(biotoolsID='contract-rich').count(), 1)
        self.assertEqual(PublicationMetadata.objects.count(), metadata_count)
        publication.metadata.refresh_from_db()
        self.assertEqual(publication.metadata.title, 'Retained after failure')
        self.assertEqual(list(publication.metadata.authors.values_list('name', flat=True)), ['Retained Author'])
        for value in ([], {}, {'resource': []}, {'resource': {}, 'revision': None, 'extra': 1}):
            self.assertEqual(self.save(value).status_code, 400)
        self.assertEqual(self.save('invalid-json').status_code, 400)

    def test_page_props_escape_markup_and_unknown_ids_do_not_render_an_editor(self):
        self.resource.description = '</script><script>alert(1)</script>'
        self.resource.save()
        page = self.client.get(self.url, **HTML_REQUEST)
        self.assertNotContains(page, self.resource.description)
        self.assertContains(page, 'hx-disable')
        self.assertContains(page, 'data-vue-island="resource-editor"')
        self.assertEqual(self.client.get('/editor/tool/missing/', **HTML_REQUEST).status_code, 404)
