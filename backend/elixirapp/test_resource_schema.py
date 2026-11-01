from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command, CommandError
from django.test import SimpleTestCase, override_settings
from lxml import etree
from rest_framework.exceptions import ValidationError

from elixir.editor_contract import resource_contract
from elixir.resource_options import METADATA_CHOICES
from elixir.resource_schema import XS, flatten, ingest
from elixir.resource_ui import (DIRECTORY, SchemaUnavailable, build_descriptor, compatibility,
                                public_fields, read_descriptor, resource_descriptor, search_metadata, selected_sources, sources)
from elixir.serializers import ResourceSerializer
from elixirapp.resource_editor import protected_nested_values


class ResourceSchemaTests(SimpleTestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(TemporaryDirectory()))
        self.schema = self.directory / 'candidate.xsd'
        self.output = self.directory / 'candidate.json'
        self.tree = etree.parse(str(DIRECTORY / 'biotools_3.3.0-singletool.xsd'))
        self.policy = self.directory / 'policy.json'
        self.policy.write_text((DIRECTORY / 'registry-ui-policy.json').read_text())
        self.baseline = resource_descriptor()
        self.addCleanup(sources.cache_clear)
        self.addCleanup(read_descriptor.cache_clear)

    def field(self, name):
        return self.tree.find('.//' + XS + 'element[@name="' + name + '"]')

    def generate(self, *, check=False):
        self.tree.write(str(self.schema), encoding='UTF-8', xml_declaration=True)
        call_command('resource_schema', schema=str(self.schema), policy=str(self.policy),
                     schema_version='fixture', output=str(self.output),
                     against=str(DIRECTORY / 'resource-ui.generated.json'),
                     check=check, write=not check, stdout=StringIO())
        return json.loads(self.output.read_text())

    def activate(self):
        self.enterContext(override_settings(RESOURCE_SCHEMA_PATH=str(self.schema),
            RESOURCE_SCHEMA_VERSION='fixture', RESOURCE_UI_POLICY_PATH=str(self.policy),
            RESOURCE_UI_DESCRIPTOR_PATH=str(self.output)))

    def test_baseline_provenance_capabilities_and_generated_snapshot(self):
        call_command('resource_schema', check=True, stdout=StringIO())
        fields = flatten(self.baseline['contract'])
        self.assertEqual(self.baseline['schema']['version'], '3.3.0')
        self.assertEqual(len(self.baseline['schema']['sha256']), 64)
        self.assertTrue(fields['function.cmd']['writable'])
        self.assertTrue(fields['publication.metadata.title']['public'])
        self.assertFalse(fields['publication.metadata.title']['writable'])
        self.assertTrue(fields['owner']['public'])
        self.assertFalse(fields['editPermission.authors']['public'])
        self.assertFalse(fields['editPermission']['writable'])
        self.assertEqual(fields['function.operation']['search'], ['operation'])
        self.assertEqual(fields['function.cmd']['search'], [])
        self.assertIn('Rust', METADATA_CHOICES['language'])
        self.assertNotIn('Icarus', METADATA_CHOICES['language'])
        self.assertIn('Mobile application', METADATA_CHOICES['toolType'])

    def test_activated_label_help_and_enum_addition_reach_validator(self):
        field = self.field('maturity')
        info = etree.SubElement(field.find(XS + 'annotation'), XS + 'appinfo')
        etree.SubElement(info, 'uiLabel').text = 'Release maturity'
        etree.SubElement(info, 'uiTip').text = 'Selected release maturity.'
        restriction = field.find('.//' + XS + 'restriction')
        item = etree.SubElement(restriction, XS + 'enumeration', value='Preview')
        annotation = etree.SubElement(item, XS + 'annotation')
        info = etree.SubElement(annotation, XS + 'appinfo')
        etree.SubElement(info, 'uiLabel').text = 'Preview release'
        candidate = self.generate()
        self.assertEqual(compatibility(self.baseline, candidate), [])
        self.activate()
        field = resource_descriptor()['contract']['fields']['maturity']
        self.assertEqual(field['label'], 'Release maturity')
        self.assertEqual(field['help'], 'Selected release maturity.')
        self.assertIn({'value': 'Preview', 'label': 'Preview release'}, field['choices'])
        self.assertEqual(ResourceSerializer().validate_maturity('Preview'), 'Preview')
        self.assertNotEqual(resource_descriptor()['revision'], self.baseline['revision'])

    def test_nested_enum_documentation_does_not_replace_field_help(self):
        annotation = self.field('maturity').find(XS + 'annotation')
        info = etree.SubElement(annotation, XS + 'appinfo')
        etree.SubElement(info, 'uiTip').text = 'Field help.'
        enum = etree.SubElement(info, 'enum')
        item = etree.SubElement(enum, 'enumItem')
        etree.SubElement(item, 'uiTip').text = 'Choice help only.'
        etree.SubElement(item, 'uiLabel').text = 'Choice label only.'
        candidate = self.generate()
        field = candidate['contract']['fields']['maturity']
        self.assertEqual(field['help'], 'Field help.')
        self.assertNotEqual(field['label'], 'Choice label only.')

    def test_removed_value_is_correction_required_not_replaced(self):
        field = self.field('maturity')
        item = field.find('.//' + XS + 'enumeration')
        removed = item.get('value')
        item.getparent().remove(item)
        candidate = self.generate()
        self.assertEqual(candidate['removedValuePolicy'], 'correction-required')
        self.assertEqual(compatibility(self.baseline, candidate), [])
        self.activate()
        self.assertNotIn(removed, METADATA_CHOICES['maturity'])
        with self.assertRaises(ValidationError):
            ResourceSerializer().validate_maturity(removed)

    def test_unreviewed_sources_and_missing_or_invalid_descriptor_fail_closed(self):
        self.generate()
        self.activate()
        self.assertEqual(resource_descriptor()['schema']['version'], 'fixture')
        self.field('name').set('minOccurs', '0')
        self.tree.write(str(self.schema), encoding='UTF-8')
        sources.cache_clear()
        with self.assertRaises(SchemaUnavailable):
            resource_descriptor()
        with self.assertRaises(SchemaUnavailable):
            METADATA_CHOICES['maturity']
        with override_settings(RESOURCE_UI_DESCRIPTOR_PATH=str(self.directory / 'missing.json')):
            with self.assertRaises(SchemaUnavailable):
                selected_sources()
        self.output.write_text('[]')
        read_descriptor.cache_clear()
        with self.assertRaises(SchemaUnavailable):
            selected_sources()

    def test_source_and_contract_changes_block_generation_without_overwriting(self):
        self.generate()
        previous = self.output.read_bytes()
        self.field('version').set('minOccurs', '1')
        with self.assertRaisesMessage(CommandError, 'Activation blocked'):
            self.generate()
        self.assertEqual(self.output.read_bytes(), previous)
        self.field('version').set('minOccurs', '0')
        self.field('version').set('maxOccurs', '2')
        with self.assertRaisesMessage(CommandError, 'schema constraint'):
            self.generate()

    def test_unknown_field_and_unsupported_construct_are_not_inferred_as_storage(self):
        sequence = self.field('tool').find(XS + 'complexType/' + XS + 'sequence')
        etree.SubElement(sequence, XS + 'element', name='futureField', type='xs:string', minOccurs='0')
        with self.assertRaisesMessage(CommandError, 'lack backend support'):
            self.generate()
        sequence.remove(sequence[-1])
        etree.SubElement(sequence, XS + 'any')
        with self.assertRaisesMessage(CommandError, 'Unsupported schema construct'):
            self.generate()

    def test_optional_nested_field_needs_backend_contract_and_explicit_capability(self):
        schema, policy = deepcopy(selected_sources())
        schema['fields']['function']['item']['fields']['extra'] = {'kind': 'string', 'required': False, 'label': 'Extra'}
        with self.assertRaisesMessage(SchemaUnavailable, 'lack backend support'):
            build_descriptor(schema, policy)
        contract = resource_contract(constraints=True)
        contract['fields']['function']['item']['fields']['extra'] = {
            'kind': 'string', 'required': False, 'readOnly': False, 'nullable': False, 'blank': False}
        descriptor = build_descriptor(schema, policy, contract)
        field = flatten(descriptor['contract'])['function.extra']
        self.assertFalse(field['public'])
        self.assertFalse(field['writable'])
        policy['writePaths'].append('function.extra')
        policy['publicPaths'].append('function.extra')
        descriptor = build_descriptor(schema, policy, contract)
        self.assertTrue(flatten(descriptor['contract'])['function.extra']['writable'])
        self.assertEqual(compatibility(self.baseline, descriptor), [])

    def test_incompatible_ids_types_constraints_and_policy_changes_require_review(self):
        for mutate in (
            lambda fields: fields.pop('name'),
            lambda fields: fields['version'].update(kind='string'),
            lambda fields: fields['version']['item'].update(kind='number'),
            lambda fields: fields['version'].update(required=True),
            lambda fields: fields['version'].update(schemaMaxItems=1),
            lambda fields: fields['name'].update(writable=False),
            lambda fields: fields['maturity']['choices'][0].update(value='renamed'),
        ):
            candidate = deepcopy(self.baseline)
            mutate(candidate['contract']['fields'])
            self.assertTrue(compatibility(self.baseline, candidate))

    def test_presentation_cannot_override_permissions_and_array_types_must_match(self):
        schema, policy = deepcopy(selected_sources())
        policy['presentation']['name']['writable'] = False
        with self.assertRaisesMessage(SchemaUnavailable, 'presentation hint'):
            build_descriptor(schema, policy)
        policy['presentation']['name'].pop('writable')
        schema['fields']['version']['item']['kind'] = 'number'
        with self.assertRaisesMessage(SchemaUnavailable, 'array item mismatch'):
            build_descriptor(schema, policy)

    def test_drift_check_and_compatible_rollback(self):
        self.generate()
        self.field('name').find(XS + 'annotation/' + XS + 'documentation').text = 'Updated description.'
        with self.assertRaisesMessage(CommandError, 'Descriptor drift'):
            self.generate(check=True)
        candidate = self.generate()
        self.assertEqual(compatibility(candidate, self.baseline), [])

    def test_entities_and_unknown_attributes_are_rejected(self):
        self.schema.write_text('<!DOCTYPE schema [<!ENTITY x "expanded">]><schema>&x;</schema>')
        with self.assertRaises(Exception):
            ingest(self.schema, 'invalid')
        self.field('name').set('nillable', 'true')
        with self.assertRaisesMessage(CommandError, 'Unsupported element attributes'):
            self.generate()

    def test_unapproved_nested_metadata_survives_reorder_but_not_replacement(self):
        contract = deepcopy(self.baseline['contract'])
        contract['fields']['function']['item']['fields']['cmd']['writable'] = False
        before = {'function': [{'cmd': 'first', 'note': 'Editable'}, {'cmd': 'second'}]}
        reordered = {'function': list(reversed(before['function']))}
        self.assertEqual(protected_nested_values(before, contract), protected_nested_values(reordered, contract))
        self.assertNotEqual(protected_nested_values(before, contract), protected_nested_values({'function': []}, contract))
        changed = {'function': [{'cmd': 'forged'}, {'cmd': 'second'}]}
        self.assertNotEqual(protected_nested_values(before, contract), protected_nested_values(changed, contract))

    def test_public_projection_uses_labels_and_choices_without_leaking_private_or_unknown_values(self):
        contract = deepcopy(self.baseline['contract'])
        contract['fields']['maturity']['label'] = 'Release maturity'
        contract['fields']['maturity']['choices'] = [{'value': 'Mature', 'label': 'Stable release'}]
        contract['fields']['function']['item']['fields']['extra'] = {
            'path': 'function.extra', 'kind': 'string', 'label': 'Extra annotation', 'public': True}
        data = {'maturity': 'Mature', 'editPermission': {'authors': ['private-author']}, 'unknown': 'Secret',
                'function': [{'extra': '<script>retained as text</script>'}]}
        nodes = public_fields(data, contract)
        self.assertEqual({node['name'] for node in nodes}, {'maturity', 'function'})
        maturity = next(node for node in nodes if node['name'] == 'maturity')
        self.assertEqual(maturity['label'], 'Release maturity')
        self.assertEqual(maturity['values'], [{'value': 'Mature', 'label': 'Stable release'}])
        extra = next(node for node in nodes if node['name'] == 'function')['entries'][0][0]
        self.assertEqual(extra['values'][0]['value'], data['function'][0]['extra'])

    def test_search_metadata_never_infers_index_support_from_schema_fields(self):
        descriptor = deepcopy(self.baseline)
        descriptor['contract']['fields']['toolType']['label'] = 'Application type'
        metadata = search_metadata(descriptor, ['toolType'])
        self.assertEqual(set(metadata), {'toolType'})
        self.assertEqual(metadata['toolType']['label'], 'Application type')
        self.assertIn('Mobile application', [item['value'] for item in metadata['toolType']['choices']])
        with self.assertRaises(SchemaUnavailable):
            search_metadata(descriptor, ['toolType', 'newUnsupportedFilter'])

    def test_repeated_filter_labels_follow_schema_paths_and_query_scope(self):
        descriptor = deepcopy(self.baseline)
        keys = ['dataTypeID', 'inputID', 'inputDataTypeID', 'outputID', 'outputDataTypeID', 'linkType', 'documentationType']
        metadata = search_metadata(descriptor, keys)
        self.assertEqual(len({item['label'] for item in metadata.values()}), len(keys))
        self.assertIn('Inputs', metadata['dataTypeID']['label'])
        self.assertIn('Outputs', metadata['dataTypeID']['label'])
        self.assertIn('Format', metadata['inputID']['label'])
        descriptor['contract']['fields']['function']['item']['fields']['input']['label'] = 'Source material'
        changed = search_metadata(descriptor, keys)
        self.assertIn('Source material', changed['inputDataTypeID']['label'])
