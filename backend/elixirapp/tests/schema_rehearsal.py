"""Real-storage schema fixtures, never installed by normal application settings."""
import json

from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command, CommandError
from lxml import etree


def expose_download_command():
    from rest_framework import serializers
    from elixir.serialization.resource_serialization.download import DownloadSerializer
    if 'cmd' not in DownloadSerializer.Meta.fields:
        DownloadSerializer._declared_fields['cmd'] = serializers.CharField(
            required=False, allow_null=True, allow_blank=True, max_length=100)
        DownloadSerializer.Meta.fields += ('cmd',)


class FixtureConfig(AppConfig):
    name = 'elixirapp.tests.schema_rehearsal'
    label = 'schema_rehearsal'

    def ready(self):
        if settings.SETTINGS_MODULE != 'elixirapp.tests.schema_rehearsal_settings':
            raise RuntimeError('Fixture serializers are forbidden in normal settings.')
        if settings.SCHEMA_REHEARSAL_PHASE != 'baseline':
            expose_download_command()


def generate():
    from elixir.resource_ui import DIRECTORY
    from elixir.resource_schema import XS
    target = settings.SCHEMA_REHEARSAL_DIRECTORY
    tree = etree.parse(str(DIRECTORY / 'biotools_3.3.0-singletool.xsd'))
    policy = json.loads((DIRECTORY / 'registry-ui-policy.json').read_text())
    previous = DIRECTORY / 'resource-ui.generated.json'
    for phase in ('baseline', 'added', 'removed'):
        if phase == 'added':
            expose_download_command()
            download = tree.find('.//' + XS + 'element[@name="download"]')
            sequence = download.find(XS + 'complexType/' + XS + 'sequence')
            field = etree.SubElement(sequence, XS + 'element', name='cmd', type='xs:string', minOccurs='0')
            info = etree.SubElement(etree.SubElement(field, XS + 'annotation'), XS + 'appinfo')
            etree.SubElement(info, 'uiLabel').text = 'Installation command'
            etree.SubElement(info, 'uiTip').text = 'A fixture field backed by the existing Download.cmd column.'
            for key in ('writePaths', 'publicPaths'):
                policy[key].append('download.cmd')
            maturity = tree.find('.//' + XS + 'element[@name="maturity"]')
            restriction = maturity.find('.//' + XS + 'restriction')
            enum = etree.SubElement(restriction, XS + 'enumeration', value='Preview')
            info = etree.SubElement(etree.SubElement(enum, XS + 'annotation'), XS + 'appinfo')
            etree.SubElement(info, 'uiLabel').text = 'Preview release'
        if phase != 'baseline':
            maturity = tree.find('.//' + XS + 'element[@name="maturity"]')
            info = etree.SubElement(maturity.find(XS + 'annotation'), XS + 'appinfo')
            etree.SubElement(info, 'uiLabel').text = 'Release maturity' if phase == 'added' else 'Release stage'
            etree.SubElement(info, 'uiTip').text = 'Activated fixture release guidance: ' + phase
            policy['presentation']['function.note']['label'] = 'Function annotation ' + phase
            policy['presentation']['toolType']['label'] = 'Application category ' + phase
        if phase == 'removed':
            value = maturity.find('.//' + XS + 'enumeration[@value="Mature"]')
            value.getparent().remove(value)
        schema = target / (phase + '.xsd')
        schema.write_bytes(etree.tostring(tree, xml_declaration=True, encoding='UTF-8'))
        policy_path = target / (phase + '-policy.json')
        policy_path.write_text(json.dumps(policy))
        output = target / (phase + '.json')
        call_command('resource_schema', schema=str(schema), schema_version='rehearsal-' + phase,
                     policy=str(policy_path), output=str(output), against=str(previous), write=True)
        previous = output
    # Rolling back the enum/labels is compatible; removing the new stored field is not.
    call_command('resource_schema', schema=str(target / 'added.xsd'), schema_version='rehearsal-added',
                 policy=str(target / 'added-policy.json'), output=str(target / 'added.json'),
                 against=str(target / 'removed.json'), check=True)
    from elixir.resource_ui import compatibility
    errors = compatibility(json.loads((target / 'added.json').read_text()),
                           json.loads((target / 'baseline.json').read_text()))
    if not any('download.cmd' in error for error in errors):
        raise CommandError('Unsafe rollback unexpectedly allowed removing the stored field.')
    print('Unsafe field-removal rollback blocked:', errors)


def seed():
    from allauth.account.models import EmailAddress
    from django.contrib.auth import get_user_model
    from elasticsearch import Elasticsearch
    from elixir.models import Resource
    from elixir.serializers import ResourceSerializer
    from elixirapp.test_edam import seed_ontology
    if Resource.objects.exists() or get_user_model().objects.filter(username='schema-test').exists():
        raise RuntimeError('Refusing to overwrite an existing rehearsal fixture.')
    es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
    if es.indices.exists(index=settings.ELASTIC_SEARCH_INDEX):
        raise RuntimeError('Rehearsal index already exists; refusing to overwrite it.')
    # Read the preview mapping only; never regenerate or modify its live index.
    mapping = es.indices.get_mapping(index='elixir')['elixir']['mappings']
    analysis = es.indices.get_settings(index='elixir')['elixir']['settings']['index'].get('analysis', {})
    es.indices.create(index=settings.ELASTIC_SEARCH_INDEX, body={'mappings': mapping, 'settings': {'analysis': analysis}})
    seed_ontology()
    owner = get_user_model().objects.create_user('schema-test', 'schema@example.invalid', 'Schema-test-only-2026')
    EmailAddress.objects.create(user=owner, email=owner.email, verified=True, primary=True)
    for identifier in ('schema-apache-desktop', 'schema-apache-mobile', 'schema-caddy-desktop', 'schema-caddy-mobile'):
        serializer = ResourceSerializer(data={
            'biotoolsID': identifier, 'name': 'Schema Rehearsal',
            'description': 'A fictional resource for an isolated schema activation rehearsal.',
            'homepage': 'https://example.org/schema-rehearsal', 'toolType': ['Command-line tool'],
            'maturity': 'Mature', 'editPermission': {'type': 'private'},
            'topic': [{'uri': 'http://edamontology.org/topic_0091'}],
            'function': [{'operation': [{'uri': 'http://edamontology.org/operation_0292'}],
                          'note': 'An annotation inside the specialized function diagram.'}],
            'download': [{'url': 'https://example.org/download', 'type': 'Source code'}],
        })
        serializer.is_valid(raise_exception=True)
        tool = serializer.save(owner=owner)
        es.index(index=settings.ELASTIC_SEARCH_INDEX, id=identifier, body=ResourceSerializer(tool).data)
    es.indices.refresh(index=settings.ELASTIC_SEARCH_INDEX)


def vocabulary(phase):
    from elixir.models import Ontology
    row = Ontology.objects.get(name='EDAM_topic')
    tree = json.loads(row.data)
    tree['children'][0]['text'] = 'Bioinformatics' if phase == 'baseline' else 'Revised bioinformatics'
    tree['children'][0]['exact_synonyms'] = ['Computational biology', 'Fixture synonym ' + phase]
    row.data = json.dumps(tree)
    row.save()


def assert_persisted():
    from elixir.models import Resource
    resources = Resource.objects.filter(biotoolsID__startswith='schema-', visibility=1)
    for resource in resources:
        assert resource.download.get().cmd == 'install schema-fixture', resource.biotoolsID
        assert resource.maturity == 'Preview', resource.biotoolsID
        assert resource.topic.get().uri == 'http://edamontology.org/topic_0091', resource.biotoolsID
    assert resources.count() == 4
    print('All four fixture resources retained the new column value and stable EDAM URI.')
