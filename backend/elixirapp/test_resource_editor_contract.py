"""Characterize develop replacement semantics without writing to the preview DB or ES."""

from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from elixir.editor_contract import describe, render_contract
from elixir.models import Domain, DomainResource, OtherID, PublicationMetadata, Resource
from elixir.serializers import ResourceSerializer, ResourceUpdateSerializer
from elixirapp.test_edam import seed_ontology


FIXTURES = json.loads((Path(__file__).parent / 'tests/data/ResourceEditor.json').read_text())


def submission_from_readback(value, field):
    """Test-side expected normalization, independently checked against the serializer."""
    if field.read_only:
        return value
    if isinstance(value, list):
        return [submission_from_readback(item, field.child) for item in value]
    if isinstance(value, dict):
        return {
            key: submission_from_readback(child, field.fields[key])
            for key, child in value.items()
            if not (not field.fields[key].required and not field.fields[key].read_only and (
                (child is None and not field.fields[key].allow_null)
                or (child == [] and not getattr(field.fields[key], 'allow_empty', True))))
        }
    return value


@override_settings(GITHUB_ECOSYSTEM_ON=False)
class ResourceEditorContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_ontology()
        cls.owner = User.objects.create_user('contract-owner')
        cls.author = User.objects.create_user('contract-author')
        serializer = ResourceSerializer(data={**FIXTURES['minimal'], 'biotoolsID': 'contract-related'})
        assert serializer.is_valid(), serializer.errors
        serializer.save(owner=cls.owner)

    def setUp(self):
        self.client = APIClient(HTTP_ACCEPT='application/json')
        self.client.force_authenticate(self.owner)
        self.es = self.enterContext(patch('elixir.view.resource.es'))
        self.es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'test-only'}]}}
        self.enterContext(patch('elixir.signals.update_publication'))

    def create(self, fixture='rich'):
        serializer = ResourceSerializer(data=deepcopy(FIXTURES[fixture]))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        return serializer.save(owner=self.owner)

    def test_generated_types_are_current_and_develop_fields_are_distinct(self):
        artifact = Path(__file__).parents[1] / 'elixir/resource-contract.generated.ts'
        self.assertEqual(artifact.read_text(), render_contract(), 'Regenerate editor field types after serializer changes.')
        fields = ResourceSerializer().fields
        self.assertEqual(set(fields), set(FIXTURES['rich']))
        self.assertIn('elixirCommunity', fields)
        self.assertIn('collectionID', fields)
        self.assertNotIn('community', fields)
        self.assertNotIn('domain', fields)
        self.assertEqual(describe(fields['editPermission'].fields['authors'])['item']['kind'], 'string')

    def test_minimal_and_rich_serialization_and_basic_edit_replacement(self):
        for fixture in ('minimal', 'rich'):
            with self.subTest(fixture=fixture):
                resource = self.create(fixture)
                original = self.client.get('/t/' + resource.biotoolsID).json()
                payload = submission_from_readback(original, ResourceUpdateSerializer())
                payload['name'] = 'Changed basic name'
                result = self.client.put('/t/' + resource.biotoolsID, payload, format='json')
                self.assertEqual(result.status_code, 200, result.data)
                reloaded = self.client.get('/t/' + resource.biotoolsID).json()
                self.assertEqual(reloaded['name'], payload['name'])
                for key in original.keys() - {'name', 'lastUpdate'}:
                    # These are deduplicated via sets by the existing create() method.
                    if key in {'toolType', 'operatingSystem', 'language', 'collectionID'}:
                        self.assertCountEqual(reloaded[key], original[key])
                    else:
                        self.assertEqual(reloaded[key], original[key], key)
                resource.refresh_from_db()
                self.assertEqual(resource.visibility, 0)
                self.es.index.assert_called()

    def test_full_rich_fixture_is_accepted_and_has_no_removed_community_field(self):
        resource = self.create()
        output = ResourceSerializer(resource).data
        self.assertEqual(output['elixirCommunity'], ['Proteomics'])
        self.assertCountEqual(output['collectionID'], FIXTURES['rich']['collectionID'])
        self.assertEqual(output['editPermission'], FIXTURES['rich']['editPermission'])
        self.assertEqual(output['function'][0]['output'][1]['data']['term'], 'Sequence name')
        self.assertEqual(output['publication'][1]['note'], '')
        self.assertEqual(output['credit'], FIXTURES['rich']['credit'])
        for serializer_class in (ResourceSerializer, ResourceUpdateSerializer):
            data = {**FIXTURES['minimal'], 'biotoolsID': 'not-yet-created'}
            serializer = serializer_class(data=data)
            self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_null_empty_string_and_empty_list_semantics(self):
        cases = [
            ({'license': None}, False), ({'license': ''}, False), ({'version': []}, False),
            ({'function': [{'operation': []}]}, False), ({'editPermission': {'type': 'group', 'authors': []}}, True),
            ({'additionDate': None}, True), ({'publication': [{'pmid': '12345', 'note': ''}]}, True),
            ({'credit': [{'name': 'Author', 'note': ''}]}, False),
            ({'topic': [{'uri': 'http://edamontology.org/topic_0091', 'term': None}]}, True),
        ]
        for extra, valid in cases:
            with self.subTest(extra=extra):
                serializer = ResourceUpdateSerializer(data={**FIXTURES['minimal'], **extra})
                self.assertEqual(serializer.is_valid(), valid, serializer.errors)
        resource = self.create('minimal')
        readback = ResourceSerializer(resource).data
        self.assertIsNone(readback['license'])
        self.assertEqual(readback['version'], [])
        invalid = ResourceUpdateSerializer(data=readback)
        self.assertFalse(invalid.is_valid())
        normalized = ResourceUpdateSerializer(data=submission_from_readback(readback, ResourceUpdateSerializer()))
        self.assertTrue(normalized.is_valid(), normalized.errors)

    def test_nested_error_shape_and_missing_fields_do_not_save(self):
        resource = self.create()
        data = deepcopy(FIXTURES['rich'])
        data['function'][0]['output'][1]['data'] = {}
        data['publication'][0] = {}
        data['name'] = ''
        response = self.client.put('/t/' + resource.biotoolsID, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('general_errors', response.data['function'][0]['output'][1]['data'])
        self.assertEqual(response.data['function'][0]['output'][0], {})
        self.assertEqual(response.data['function'][1], {})
        self.assertEqual(list(response.data['publication'][0]), ['general_errors'])
        self.assertEqual(response.data['name'], FIXTURES['errors']['name'])
        self.assertEqual(response.data['publication'], FIXTURES['errors']['publication'])
        resource.refresh_from_db()
        self.assertEqual(resource.visibility, 1)
        self.es.index.assert_not_called()

    def test_server_owned_fields_permissions_and_domain_membership(self):
        resource = self.create()
        domain = Domain.objects.create(name='contract-domain', owner=self.owner)
        membership = DomainResource.objects.create(domain=domain, biotoolsID=resource.biotoolsID, name=resource.name)
        data = deepcopy(FIXTURES['rich'])
        data.update(biotoolsID='cannot-rename', biotoolsCURIE='cannot-change', owner='contract-author',
                    additionDate='2000-01-01T00:00:00Z', validated=1)
        del data['editPermission']
        self.client.force_authenticate(self.author)
        response = self.client.put('/t/' + resource.biotoolsID, data, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        for key in ('biotoolsID', 'biotoolsCURIE', 'owner', 'additionDate', 'validated', 'editPermission'):
            self.assertEqual(response.data[key], ResourceSerializer(resource).data[key], key)
        membership.refresh_from_db()
        self.assertEqual(membership.biotoolsID, resource.biotoolsID)
        self.assertEqual(domain.resource.count(), 1)
        data['editPermission'] = {'type': 'public'}
        rejected = self.client.put('/t/' + resource.biotoolsID, data, format='json')
        self.assertEqual(rejected.status_code, 401)

    def test_replacement_preserves_server_enrichment_but_unknown_fields_are_still_discarded(self):
        resource = self.create()
        publication = resource.publication.first()
        publication.metadata = PublicationMetadata.objects.create(title='Enriched title', citationCount=3)
        publication.save()
        resource.homepage_status = 2
        resource.elixir_badge = 4
        resource.save()
        payload = submission_from_readback(ResourceSerializer(resource).data, ResourceUpdateSerializer())
        response = self.client.put('/t/' + resource.biotoolsID, payload, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['publication'][0]['metadata'], payload['publication'][0]['metadata'])
        self.assertEqual(response.data['homepage_status'], 2)
        self.assertEqual(response.data['elixir_badge'], 4)
        unknown = ResourceUpdateSerializer(data={**FIXTURES['minimal'], 'futureField': 'not stored'})
        self.assertTrue(unknown.is_valid(), unknown.errors)
        self.assertNotIn('futureField', unknown.validated_data)

    def test_omission_is_replacement_and_community_values_follow_the_schema(self):
        resource = self.create()
        payload = {**FIXTURES['minimal'], 'biotoolsID': resource.biotoolsID}
        response = self.client.put('/t/' + resource.biotoolsID, payload, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['function'], [])
        self.assertEqual(response.data['credit'], [])
        self.assertIsNone(response.data['license'])
        accepted = ResourceUpdateSerializer(data={**FIXTURES['minimal'], 'elixirCommunity': ['Cancer Data']})
        self.assertTrue(accepted.is_valid(), accepted.errors)
        invalid = ResourceUpdateSerializer(data={**FIXTURES['minimal'], 'elixirCommunity': ['Not a known community']})
        self.assertFalse(invalid.is_valid())
        self.assertIn('elixirCommunity', invalid.errors)

    def test_protected_other_id_api_rewriting_is_limited_to_non_admins(self):
        resource = self.create('minimal')
        OtherID.objects.create(resource=resource, value='biotools:previous-id', type='biotoolsCURIE')
        data = {**FIXTURES['minimal'], 'otherID': [
            {'value': 'biotools:previous-id', 'type': 'biotoolsCURIE'},
            {'value': 'not-a-valid-identifier'},
        ]}
        response = self.client.put('/t/' + resource.biotoolsID, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('value', response.data['otherID'][0])
        self.assertEqual(response.data['otherID'][1], {})
        self.es.index.assert_not_called()
        admin = User.objects.create_user('contract-admin', is_superuser=True)
        self.client.force_authenticate(admin)
        data['otherID'].pop()
        response = self.client.put('/t/' + resource.biotoolsID, data, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data['otherID']), 1)
        self.assertEqual(response.data['otherID'][0]['value'], 'biotools:previous-id')

    def test_api_permission_payloads_are_validated_before_comparing_members(self):
        resource = self.create('minimal')
        for permission in (None, [], {'type': 'private', 'authors': [{}]},
                           {'type': 'private', 'authors': [None]}, {'type': 'private', 'authors': 1}):
            with self.subTest(permission=permission):
                response = self.client.put('/t/' + resource.biotoolsID,
                    {**FIXTURES['minimal'], 'editPermission': permission}, format='json')
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn('editPermission', response.data)
        resource.refresh_from_db()
        self.assertEqual(resource.visibility, 1)
        self.es.index.assert_not_called()
