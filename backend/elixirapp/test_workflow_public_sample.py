"""Compare database matching with an anonymized sample of public annotations."""
import json
from collections import Counter
from pathlib import Path

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from elixir.models import Data, EditPermission, Format, Function, Input, Ontology, Operation, Output, Resource
from elixirapp.test_edam import node

SAMPLE = Path(__file__).parent / 'tests' / 'data' / 'WorkflowPublicSample.json'
CANONICAL = {'biotools.canonical': True}


class PublicSampleMatchingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sample = json.loads(SAMPLE.read_text())
        terms = {'data': set(), 'format': set(), 'operation': set()}
        for tool in cls.sample:
            for function in tool['functions']:
                terms['operation'].update(item['uri'] for item in function['operation'] if item['uri'])
                for direction in ('input', 'output'):
                    for annotation in function[direction]:
                        if annotation['data']['uri']:
                            terms['data'].add(annotation['data']['uri'])
                        terms['format'].update(item['uri'] for item in annotation['format'] if item['uri'])
        roots = {'data': '0006', 'format': '1915', 'operation': '0004'}
        for scope, number in roots.items():
            root_uri = f'http://edamontology.org/{scope}_{number}'
            children = [node(scope, uri.rsplit('_', 1)[1], uri) for uri in sorted(terms[scope] - {root_uri})]
            Ontology.objects.create(name='EDAM_' + scope, data=json.dumps(node(scope, number, scope, children)))
        Ontology.objects.create(name='EDAM_obsolete', data=json.dumps(node('topic', '9999', 'Obsolete')))
        owner = User.objects.create_user('workflow-public-sample')
        permission = EditPermission.objects.create(type='public')
        resources = [Resource(biotoolsID=f'workflow-sample-{index:04}', name=f'Anonymous sample {index}',
                              owner=owner, editPermission=permission, additionDate=timezone.now())
                     for index in range(len(cls.sample))]
        Resource.objects.bulk_create(resources, batch_size=100)
        by_id = {item.biotoolsID: item for item in Resource.objects.filter(biotoolsID__startswith='workflow-sample-')}
        operations, formats = [], []
        for index, tool in enumerate(cls.sample):
            resource = by_id[f'workflow-sample-{index:04}']
            for raw_function in tool['functions']:
                function = Function.objects.create(resource=resource)
                operations.extend(Operation(function=function, uri=item['uri']) for item in raw_function['operation'])
                for direction, model in (('input', Input), ('output', Output)):
                    for annotation in raw_function[direction]:
                        data = Data.objects.create(uri=annotation['data']['uri'])
                        io = model.objects.create(function=function, data=data)
                        formats.extend(Format(**{direction: io}, uri=item['uri']) for item in annotation['format'])
        Operation.objects.bulk_create(operations, batch_size=200)
        Format.objects.bulk_create(formats, batch_size=200)

    def test_sample_exact_and_unknown_matches_equal_independent_structured_oracle(self):
        for direction in ('input', 'output'):
            frequencies = Counter()
            for tool in self.sample:
                for function in tool['functions']:
                    for annotation in function[direction]:
                        for fmt in annotation['format']:
                            for operation in function['operation']:
                                if annotation['data']['uri'] and fmt['uri'] and operation['uri']:
                                    frequencies[(annotation['data']['uri'], fmt['uri'], operation['uri'])] += 1
            data_uri, format_uri, operation_uri = frequencies.most_common(1)[0][0]
            for include in ('matches', 'unknown'):
                expected = Counter()
                for index, tool in enumerate(self.sample):
                    for function in tool['functions']:
                        operation_uris = tuple(sorted(item['uri'] for item in function['operation']))
                        annotations = function[direction] or ([{'data': {'uri': None}, 'format': []}] if include == 'unknown' else [])
                        for annotation in annotations:
                            data = annotation['data']['uri']
                            format_uris = tuple(sorted(item['uri'] for item in annotation['format']))
                            states = [data == data_uri if data else None,
                                      format_uri in format_uris if format_uris else None,
                                      operation_uri in operation_uris if operation_uris else None]
                            if False not in states and (include == 'unknown' or None not in states):
                                expected[(f'workflow-sample-{index:04}', data, format_uris, operation_uris)] += 1
                params = {'direction': direction, 'data': data_uri, 'format': format_uri,
                          'operation': operation_uri, 'include': include, 'limit': '3'}
                actual, cursor = Counter(), None
                for _ in range(100):
                    response = self.client.get('/_workflow/matches/', {**params, **({'cursor': cursor} if cursor else {})}, **CANONICAL)
                    self.assertEqual(response.status_code, 200, response.content)
                    body = response.json()
                    self.assertLessEqual(body['pagination']['scanned'], 100)
                    for item in body['items']:
                        actual[(item['resource']['id'], (item['io']['data'] or {}).get('uri'),
                                tuple(sorted(fmt['uri'] for fmt in item['io']['formats'])),
                                tuple(sorted(op['uri'] for op in item['function']['operations'])))] += 1
                    cursor = body['pagination']['next']
                    if not cursor:
                        self.assertTrue(body['pagination']['complete'])
                        break
                else:
                    self.fail('The bounded scan did not finish.')
                self.assertTrue(expected)
                self.assertEqual(actual, expected)
