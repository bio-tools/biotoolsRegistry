from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

from elixir.models import Ontology, Resource
from elixir.serializers import FunctionSerializer, ResourceSerializer, ResourceUpdateSerializer
from elixir.resource_ui import resource_descriptor
from elixirapp.resource_editor import editor_fields, normalized, unrelated
from elixirapp.test_edam import seed_ontology
from elixirapp.test_html import HTML_REQUEST
from elixirapp.test_resource_editor_contract import FIXTURES


FUNCTIONS = json.loads((Path(__file__).parent / 'tests/data/NestedFunctions.json').read_text())
EDITOR_FIELDS = editor_fields(resource_descriptor())


@override_settings(GITHUB_ECOSYSTEM_ON=False)
class NestedEditorTests(TestCase):
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
        self.es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'nested-test'}]}}
        self.enterContext(patch('elixir.signals.update_publication'))
        serializer = ResourceSerializer(data={**deepcopy(FIXTURES['rich']), 'function': deepcopy(FUNCTIONS)})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.resource = serializer.save(owner=self.owner)
        self.url = '/editor/tool/contract-rich/'
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)

    def load(self):
        config = self.client.get(self.url, **HTML_REQUEST).context['editor_config']
        self.assertEqual(config['edamEndpoint'], '/edam/terms/')
        return {'resource': normalized(config['resource'], ResourceUpdateSerializer()), 'revision': config['revision'],
                'schemaRevision': config['schemaRevision']}

    def save(self, body, url=None):
        body.setdefault('schemaRevision', resource_descriptor()['revision'])
        return self.client.post(url or self.url + 'save/', body, content_type='application/json',
            HTTP_ACCEPT='application/json', HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST)

    def test_schema_330_cardinalities_match_the_nested_serializer(self):
        path = Path(__file__).parents[1] / 'elixir/biotoolsSchema/biotools_3.3.0-singletool.xsd'
        ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        schema = ElementTree.parse(path)
        function = schema.find('.//xs:element[@name="function"]', ns)
        self.assertEqual((function.get('minOccurs'), function.get('maxOccurs')), ('0', 'unbounded'))
        sequence = function.find('xs:complexType/xs:sequence', ns)
        self.assertEqual([field.get('name') for field in sequence], ['operation', 'input', 'output', 'note', 'cmd'])
        operation = sequence.find('xs:element[@name="operation"]', ns)
        self.assertEqual((operation.get('minOccurs', '1'), operation.get('maxOccurs')), ('1', 'unbounded'))
        fields = FunctionSerializer().fields
        self.assertTrue(fields['operation'].required)
        self.assertFalse(fields['operation'].allow_empty)
        for name in ('input', 'output'):
            node = sequence.find(f'xs:element[@name="{name}"]', ns)
            self.assertEqual((node.get('minOccurs'), node.get('maxOccurs')), ('0', 'unbounded'))
            data = node.find('.//xs:element[@name="data"]', ns)
            self.assertEqual((data.get('minOccurs', '1'), data.get('maxOccurs', '1')), ('1', '1'))
            formats = node.find('.//xs:element[@name="format"]', ns)
            self.assertEqual((formats.get('minOccurs'), formats.get('maxOccurs')), ('0', 'unbounded'))
            self.assertTrue(fields[name].child.fields['data'].required)
            self.assertFalse(fields[name].child.fields['format'].required)

    def test_rich_round_trip_reorders_functions_and_io_without_changing_other_metadata(self):
        before = ResourceSerializer(self.resource).data
        body = self.load()
        functions = body['resource']['function']
        functions.reverse()
        functions[1]['input'].reverse()
        functions[1]['output'].reverse()
        functions[1]['operation'] = functions[1]['operation'][:1]
        functions[1]['note'] = 'Updated function note with untouched publications and credits.'
        functions[1]['cmd'] = 'example --updated'
        expected = deepcopy(functions)
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        after = response.json()['resource']
        self.assertEqual(unrelated(after, EDITOR_FIELDS), unrelated(before, EDITOR_FIELDS))
        self.assertEqual(len(after['function']), len(expected))
        for original, saved in zip(expected, after['function']):
            self.assertEqual(saved['note'], original['note'])
            self.assertEqual(saved['cmd'], original['cmd'])
            self.assertCountEqual(saved['operation'], original['operation'])
            for kind in ('input', 'output'):
                self.assertEqual([item['data'] for item in saved[kind]], [item['data'] for item in original[kind]])
                for left, right in zip(original[kind], saved[kind]):
                    self.assertCountEqual(left.get('format', []), right['format'])
        self.assertEqual(len(after['publication']), 2)
        self.assertEqual(after['credit'], before['credit'])

    def test_create_multiple_operations_formats_and_single_data_objects(self):
        self.client.get('/editor/new/', **HTML_REQUEST)
        body = {'resource': {**FIXTURES['minimal'], 'biotoolsID': 'nested-created', 'function': deepcopy(FUNCTIONS)}, 'revision': None}
        response = self.save(body, '/editor/new/save/')
        self.assertEqual(response.status_code, 201, response.content)
        functions = response.json()['resource']['function']
        self.assertEqual(len(functions), 2)
        self.assertEqual(len(functions[0]['operation']), 2)
        self.assertEqual(len(functions[0]['input'][0]['format']), 2)
        self.assertIsInstance(functions[0]['input'][0]['data'], dict)
        self.assertNotIn('id', functions[0])

    def test_uri_submission_survives_an_activated_edam_label_change(self):
        body = self.load()
        before = deepcopy(body['resource']['topic'])
        ontology = Ontology.objects.get(name='EDAM_topic')
        tree = json.loads(ontology.data)
        tree['children'][0]['text'] = 'Revised bioinformatics'
        ontology.data = json.dumps(tree)
        ontology.save()
        for concept in body['resource']['topic']:
            concept.pop('term', None)
        body['resource']['name'] = 'Updated with current vocabulary'
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        after = response.json()['resource']['topic']
        self.assertEqual([item['uri'] for item in before], [item['uri'] for item in after])
        self.assertEqual(after[0]['term'], 'Revised bioinformatics')

    def test_invalid_second_output_format_has_precise_indexed_errors_and_no_save(self):
        body = self.load()
        body['resource']['function'][0]['output'][1]['format'] = [{'uri': 'http://edamontology.org/data_0863'}]
        response = self.save(body)
        self.assertEqual(response.status_code, 400, response.content)
        errors = response.json()['function']
        self.assertEqual(errors[1], {})
        self.assertEqual(errors[0]['output'][0], {})
        self.assertIn('general_errors', errors[0]['output'][1]['format'][0])
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.visibility, 1)
        self.es.index.assert_not_called()

    def test_required_operations_single_data_and_note_rules_remain_authoritative(self):
        for function, field in [({'operation': []}, 'operation'),
                                ({'operation': FUNCTIONS[1]['operation'], 'input': [{'data': []}]}, 'input'),
                                ({'operation': FUNCTIONS[1]['operation'], 'input': [{}]}, 'input'),
                                ({'operation': FUNCTIONS[1]['operation'], 'note': 'short'}, 'note')]:
            with self.subTest(field=field):
                body = self.load()
                body['resource']['function'] = [function]
                response = self.save(body)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(field, response.json()['function'][0])
        self.es.index.assert_not_called()

    def test_optional_lists_and_all_functions_can_be_explicitly_removed(self):
        body = self.load()
        body['resource']['function'] = [{'operation': deepcopy(FUNCTIONS[1]['operation'])}]
        response = self.save(body)
        self.assertEqual(response.status_code, 200, response.content)
        saved = response.json()['resource']['function'][0]
        self.assertEqual(saved['input'], [])
        self.assertEqual(saved['output'], [])
        self.assertIsNone(saved['note'])
        self.assertIsNone(saved['cmd'])
        body = self.load()
        del body['resource']['function']
        response = self.save(body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['resource']['function'], [])

    def test_unknown_nested_keys_client_ids_and_unrelated_writes_are_rejected(self):
        for key in ('id', 'value', 'futureField'):
            body = self.load()
            body['resource']['function'][0]['input'][1]['data'][key] = 'not-public-data'
            response = self.save(body)
            self.assertEqual(response.status_code, 400)
            self.assertIn(key, response.json()['function'][0]['input'][1]['data'])
        body = self.load()
        body['resource']['owner'] = 'not-the-owner'
        self.assertEqual(self.save(body).status_code, 400)
        self.es.index.assert_not_called()

    def test_nested_mutation_keeps_permission_csrf_and_revision_guards(self):
        body = self.load()
        body['resource']['function'].reverse()
        missing_csrf = self.client.post(self.url + 'save/', body, content_type='application/json', HTTP_ACCEPT='application/json', **HTML_REQUEST)
        self.assertEqual(missing_csrf.status_code, 403)
        stranger = User.objects.create_user('nested-stranger')
        self.client.force_login(stranger)
        self.assertEqual(self.save(body).status_code, 403)
        self.client.force_login(self.owner)
        self.assertEqual(self.save(body).status_code, 200)
        self.assertEqual(self.save(body).status_code, 409)
