from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from rest_framework.exceptions import ValidationError

from elixir.models import PublicationMetadata, Resource
from elixir.publication_metadata import fetch_publication_data, update_publication
from elixir.resource_options import METADATA_CHOICES
from elixir.serializers import ResourceSerializer, ResourceUpdateSerializer
from elixir.resource_ui import resource_descriptor
from elixirapp.resource_editor import BASIC_FIELDS, editor_fields, normalized, unrelated
from elixirapp.test_edam import seed_ontology
from elixirapp.test_html import HTML_REQUEST
from elixirapp.test_resource_editor_contract import FIXTURES

EDITOR_FIELDS = editor_fields(resource_descriptor())
METADATA_FIELDS = EDITOR_FIELDS - BASIC_FIELDS - {'function'}


@override_settings(GITHUB_ECOSYSTEM_ON=False)
class MetadataEditorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_ontology()
        cls.owner = User.objects.create_user('contract-owner')
        User.objects.create_user('contract-author')
        serializer = ResourceSerializer(data={**FIXTURES['minimal'], 'biotoolsID': 'contract-related'})
        assert serializer.is_valid(), serializer.errors
        serializer.save(owner=cls.owner)

    def setUp(self):
        self.es = self.enterContext(patch('elixir.view.resource.es'))
        self.es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'metadata-test'}]}}
        self.publication_update = self.enterContext(patch('elixir.signals.update_publication'))
        serializer = ResourceSerializer(data=deepcopy(FIXTURES['rich']))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.resource = serializer.save(owner=self.owner)
        self.url = '/editor/tool/contract-rich/'
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)

    def load(self):
        config = self.client.get(self.url, **HTML_REQUEST).context['editor_config']
        return {'resource': normalized(config['resource'], ResourceUpdateSerializer()), 'revision': config['revision'],
                'schemaRevision': config['schemaRevision']}

    def save(self, body, url=None):
        body.setdefault('schemaRevision', resource_descriptor()['revision'])
        return self.client.post(url or self.url + 'save/', body, content_type='application/json',
            HTTP_ACCEPT='application/json', HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST)

    def test_schema_coverage_and_all_shared_options_are_accepted_by_the_authoritative_validators(self):
        schema = ElementTree.parse(Path(__file__).parents[1] / 'elixir/biotoolsSchema/biotools_3.3.0-singletool.xsd')
        ns = {'x': 'http://www.w3.org/2001/XMLSchema'}
        fields = schema.findall('x:element[@name="tool"]/x:complexType/x:sequence/x:element', ns)
        self.assertEqual({field.get('name') for field in fields}, EDITOR_FIELDS | {'biotoolsID', 'biotoolsCURIE'})
        self.assertEqual(len(METADATA_FIELDS), 19)
        self.assertEqual(self.client.get(self.url, **HTML_REQUEST).context['editor_config']['metadataOptions'], METADATA_CHOICES)
        serializer = ResourceSerializer()
        for path, choices in METADATA_CHOICES.items():
            parent = serializer
            for name in path.split('.')[:-1]:
                parent = parent.fields[name].child
            name = path.split('.')[-1]
            field = parent.fields[name]
            if hasattr(field, 'child'):
                validate = field.child.run_validation
            else:
                validate = getattr(parent, 'validate_' + name)
            for choice in choices:
                with self.subTest(path=path, choice=choice):
                    validate(choice)
            with self.assertRaises(ValidationError):
                validate('not-a-schema-choice')
        self.assertIn('Android', METADATA_CHOICES['operatingSystem'])
        self.assertIn('Rust', METADATA_CHOICES['language'])

    def test_edit_all_metadata_and_round_trip_without_changing_basic_functions_or_server_fields(self):
        before = ResourceSerializer(self.resource).data
        body = self.load()
        values = body['resource']
        values.update(version=['3.0'], otherID=[{'value': 'RRID:SCR_123456', 'type': 'rrid', 'version': '3.0'}],
            topic=[{'uri': 'http://edamontology.org/topic_0080'}], operatingSystem=['Android'], language=['Rust'],
            license='Apache-2.0', collectionID=['Updated collection'], maturity='Emerging', cost='Commercial',
            accessibility='Restricted access', elixirPlatform=['Data'], elixirCommunity=['Galaxy'], elixirNode=['Sweden'],
            link=[{'url': 'https://example.org/issues', 'type': ['Repository', 'Issue tracker'], 'note': 'Updated link description.'}],
            documentation=[{'url': 'https://example.org/docs', 'type': ['API documentation', 'User manual']}],
            download=[{'url': 'https://example.org/package', 'type': 'Software package', 'version': '3.0', 'note': 'Updated package description.'}],
            relation=[{'biotoolsID': 'contract-related', 'type': 'includes'}],
            publication=[{'pmid': '12345', 'type': ['Method', 'Usage'], 'version': '3.0', 'note': 'Updated publication description.', 'metadata': None}],
            credit=[{**FIXTURES['rich']['credit'][0], 'name': 'Updated Credit', 'typeRole': ['Provider', 'Support']}])
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        saved = response.json()['resource']
        self.assertEqual(unrelated(before, METADATA_FIELDS), unrelated(saved, METADATA_FIELDS))
        expected = normalized(saved, ResourceUpdateSerializer())
        for field in METADATA_FIELDS - {'topic'}:
            self.assertEqual(expected.get(field), values.get(field), field)
        self.assertEqual(saved['topic'][0]['uri'], values['topic'][0]['uri'])
        self.assertEqual(self.save(self.load()).status_code, 200)

    def test_create_with_all_metadata_and_explicit_optional_clearing(self):
        self.load()
        values = {key: deepcopy(value) for key, value in FIXTURES['rich'].items() if key in EDITOR_FIELDS | {'biotoolsID'}}
        values['biotoolsID'] = 'metadata-created'
        response = self.save({'resource': values, 'revision': None}, '/editor/new/save/')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertTrue(METADATA_FIELDS <= response.json()['resource'].keys())
        body = self.load()
        for field in METADATA_FIELDS:
            body['resource'].pop(field, None)
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        for field in METADATA_FIELDS:
            self.assertIn(response.json()['resource'][field], [None, []], field)

    def test_precise_errors_unknown_keys_and_malformed_shapes_do_not_save(self):
        for field, invalid in [('credit', [{'name': 'Valid'}, {'email': 'invalid'}]),
                               ('publication', [{'pmid': '12345'}, {}]),
                               ('link', [{'url': 'https://example.org', 'type': 'Repository'}]),
                               ('download', [{'url': 'https://example.org', 'type': ['Source code']}]),
                               ('publication', ['invalid']), ('otherID', [{'value': 12}]), ('otherID', [None]), ('otherID', 12)]:
            with self.subTest(field=field, invalid=invalid):
                body = self.load()
                body['resource'][field] = invalid
                response = self.save(body)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(field, response.json())
        body = self.load()
        body['resource']['credit'].append({'name': 'New credit', 'id': 'client-id'})
        response = self.save(body)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['credit'][0], {})
        self.assertIn('id', response.json()['credit'][1])
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 1)
        self.es.index.assert_not_called()

    def test_readonly_metadata_and_protected_identifiers_cannot_bypass_preservation_checks(self):
        self.load()
        for patch_value in [{'publication': [{'pmid': '12345', 'metadata': {'title': 'Forged'}}]},
                            {'otherID': [{'value': 'biotools:protected', 'type': 'biotoolsCURIE'}]},
                            {'otherID': [{'value': '  BIOTOOLS:protected', 'type': 'biotoolsCURIE'}]}]:
            response = self.save({'resource': {**FIXTURES['minimal'], **patch_value}, 'revision': None}, '/editor/new/save/')
            self.assertEqual(response.status_code, 409, response.content)
        self.es.index.assert_not_called()

    def test_publication_metadata_follows_identity_through_reordering_and_annotation_changes(self):
        publication = self.resource.publication.first()
        self.resource.publication.exclude(pk=publication.pk).delete()
        publication.metadata = PublicationMetadata.objects.create(title='First publication')
        publication.save()
        self.resource.publication.create(pmid='54321', metadata=PublicationMetadata.objects.create(title='Second publication'))
        body = self.load()
        body['resource']['publication'].reverse()
        body['resource']['publication'][1].update(note='Updated publication description.', version='4.0', type=['Method'])
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual([item['metadata']['title'] for item in response.json()['resource']['publication']],
                         ['Second publication', 'First publication'])
        body = self.load()
        body['resource']['publication'][0]['pmid'] = '99999'
        body['resource']['publication'][0].pop('metadata')
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIsNone(response.json()['resource']['publication'][0]['metadata'])
        self.assertEqual(response.json()['resource']['publication'][1]['metadata']['title'], 'First publication')

    def test_successful_publication_lookup_persists_enrichment_and_missing_ids_then_can_be_edited(self):
        self.load()
        self.publication_update.side_effect = update_publication
        values = {**FIXTURES['minimal'], 'biotoolsID': 'lookup-created', 'publication': [{'pmid': '12345'}]}
        with patch('elixir.publication_metadata.requests.get') as get:
            get.return_value.status_code = 200
            get.return_value.json.return_value = {'resultList': {'result': [{
                'pmid': '12345', 'doi': '10.1234/lookup', 'pmcid': 'PMC12345',
                'title': 'Fetched publication', 'abstractText': 'Fetched abstract',
                'journalInfo': {'journal': {'title': 'Test journal'}, 'printPublicationDate': '2026-01-01T00:00:00Z'},
                'authorList': {'author': [{'fullName': 'Fetched Author'}]},
            }]}}
            response = self.save({'resource': values, 'revision': None}, '/editor/new/save/')
            self.assertEqual(response.status_code, 201, response.content)
            saved = response.json()['resource']
            publication = saved['publication'][0]
            self.assertEqual(publication['metadata']['title'], 'Fetched publication')
            self.assertEqual(publication['metadata']['citationCount'], 0)
            self.assertEqual(publication['metadata']['authors'], [{'name': 'Fetched Author'}])
            self.assertEqual(publication['doi'], '10.1234/lookup')
            self.assertEqual(publication['pmcid'], 'PMC12345')
            self.url = '/editor/tool/lookup-created/'
            body = self.load()
            body['resource']['name'] = 'Edited after lookup'
            edited = self.save(body)
            self.assertEqual(edited.status_code, 200, edited.content)
            self.assertEqual(edited.json()['resource']['publication'], saved['publication'])
            get.assert_called_once()

    def test_unchanged_unenriched_publications_do_not_trigger_lookup_during_replacement(self):
        self.publication_update.side_effect = update_publication
        before = ResourceSerializer(self.resource).data['publication']
        with patch('elixir.publication_metadata.requests.get') as get:
            body = self.load()
            body['resource']['name'] = 'Unrelated name edit'
            response = self.save(body)
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(response.json()['resource']['publication'], before)
            get.assert_not_called()

    def test_publication_network_request_has_a_bounded_timeout(self):
        with patch('elixir.publication_metadata.requests.get') as get:
            get.return_value.status_code = 200
            get.return_value.json.return_value = {'resultList': {'result': []}}
            self.assertIsNone(fetch_publication_data('DOI', '10.1234/test', 'core'))
            self.assertEqual(get.call_args.kwargs['timeout'], (3, 5))

    def test_unchanged_tool_types_are_compared_as_a_set_without_hiding_loss(self):
        first = {'toolType': ['Command-line tool', 'Web application']}
        self.assertEqual(unrelated(first, set()), unrelated({'toolType': list(reversed(first['toolType']))}, set()))
        self.assertNotEqual(unrelated(first, set()), unrelated({'toolType': ['Command-line tool']}, set()))
