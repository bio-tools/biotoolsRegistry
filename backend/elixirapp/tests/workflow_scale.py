"""Opt-in synthetic scale rehearsal; Django creates and destroys only test data."""
import json
import logging
import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import median, quantiles
from time import perf_counter
from unittest import skipUnless

from django.contrib.auth.models import User
from django.db import close_old_connections, connections
from django.test import Client, TransactionTestCase
from django.utils import timezone

from elixir.models import Data, EditPermission, Format, Function, Input, Ontology, Operation, Output, Resource
from elixirapp.test_edam import node

SAMPLE = Path(__file__).parent / 'data' / 'WorkflowPublicSample.json'
CANONICAL = {'biotools.canonical': True}


@skipUnless(os.environ.get('BIOTOOLS_WORKFLOW_SCALE') == '1', 'Explicitly opt in to the synthetic scale rehearsal.')
class WorkflowScaleTests(TransactionTestCase):
    def test_sample_patterns_at_registry_scale(self):
        routes = logging.getLogger('biotools.routes')
        self.addCleanup(routes.setLevel, routes.level)
        routes.setLevel(logging.WARNING)
        corpus_path = os.environ.get('BIOTOOLS_WORKFLOW_CORPUS')
        sample = json.loads(Path(corpus_path).read_text() if corpus_path else SAMPLE.read_text())
        copies = 1 if corpus_path else 70
        ontology_path = os.environ.get('BIOTOOLS_WORKFLOW_ONTOLOGY')
        ontology = json.loads(Path(ontology_path).read_text()) if ontology_path else None

        def tree_uris(root):
            found, stack = set(), [root]
            while stack:
                item = stack.pop()
                found.add(item['data']['uri'])
                stack.extend(item.get('children', []))
            return found

        active = {scope: tree_uris(ontology[scope]) for scope in ('data', 'format', 'operation')} if ontology else None
        def valid(scope, value):
            return (isinstance(value, str) and re.fullmatch(r'http://edamontology.org/' + scope + r'_[0-9]{4}', value)
                    and (active is None or value in active[scope]))

        terms = {'data': set(), 'format': set(), 'operation': set()}
        frequencies = Counter()
        for tool in sample:
            for function in tool['functions']:
                terms['operation'].update(item['uri'] for item in function['operation'] if valid('operation', item['uri']))
                for direction in ('input', 'output'):
                    for io in function[direction]:
                        if valid('data', io['data']['uri']):
                            terms['data'].add(io['data']['uri'])
                        terms['format'].update(item['uri'] for item in io['format'] if valid('format', item['uri']))
                        if direction == 'input':
                            for fmt in io['format']:
                                for operation in function['operation']:
                                    if valid('data', io['data']['uri']) and valid('format', fmt['uri']) and valid('operation', operation['uri']):
                                        frequencies[(io['data']['uri'], fmt['uri'], operation['uri'])] += 1
        for scope, number in {'data': '0006', 'format': '1915', 'operation': '0004'}.items():
            if ontology:
                terms[scope] = active[scope]
                tree = ontology[scope]
            else:
                root = f'http://edamontology.org/{scope}_{number}'
                children = [node(scope, uri.rsplit('_', 1)[1], uri) for uri in sorted(terms[scope] - {root})]
                tree = node(scope, number, scope, children)
            Ontology.objects.create(name='EDAM_' + scope, data=json.dumps(tree))
        Ontology.objects.create(name='EDAM_obsolete', data=json.dumps(ontology['obsolete'] if ontology else node('topic', '9999', 'Obsolete')))
        owner = User.objects.create_user('workflow-scale-test')
        permission = EditPermission.objects.create(type='public')
        created_at = timezone.now()
        resources = [Resource(biotoolsID=f'wfscale-{index:05}', name=f'Anonymous {index}', owner=owner,
                              editPermission=permission, additionDate=created_at)
                     for index in range(copies * len(sample))]
        Resource.objects.bulk_create(resources, batch_size=500)
        resource_ids = dict(Resource.objects.filter(biotoolsID__startswith='wfscale-').values_list('biotoolsID', 'pk'))
        functions, operation_rows, io_rows = [], [], []
        for index in range(copies * len(sample)):
            for position, function in enumerate(sample[index % len(sample)]['functions']):
                key = f'wfscale-{index:05}-{position:03}'
                functions.append(Function(resource_id=resource_ids[f'wfscale-{index:05}'], note=key))
                operation_rows.extend((key, item['uri']) for item in function['operation'])
                for direction in ('input', 'output'):
                    for io_index, io in enumerate(function[direction]):
                        io_rows.append((key, direction, f'{key}-{direction}-{io_index:03}', io))
        Function.objects.bulk_create(functions, batch_size=500)
        function_ids = dict(Function.objects.filter(note__startswith='wfscale-').values_list('note', 'pk'))
        Operation.objects.bulk_create([Operation(function_id=function_ids[key], uri=uri) for key, uri in operation_rows], batch_size=500)
        Data.objects.bulk_create([Data(term=key, uri=io['data']['uri']) for _, _, key, io in io_rows], batch_size=500)
        data_ids = dict(Data.objects.filter(term__startswith='wfscale-').values_list('term', 'pk'))
        for direction, model in (('input', Input), ('output', Output)):
            model.objects.bulk_create([model(function_id=function_ids[function], data_id=data_ids[key])
                for function, kind, key, _ in io_rows if kind == direction], batch_size=500)
        input_ids = dict(Input.objects.filter(data__term__startswith='wfscale-').values_list('data__term', 'pk'))
        output_ids = dict(Output.objects.filter(data__term__startswith='wfscale-').values_list('data__term', 'pk'))
        Format.objects.bulk_create([Format(**{direction + '_id': (input_ids if direction == 'input' else output_ids)[key]}, uri=fmt['uri'])
            for _, direction, key, io in io_rows for fmt in io['format']], batch_size=500)

        data_uri, format_uri, operation_uri = frequencies.most_common(1)[0][0]
        expected_per_copy = sum(1 for tool in sample for function in tool['functions'] for io in function['input']
            if io['data']['uri'] == data_uri and any(fmt['uri'] == format_uri for fmt in io['format']) and
            any(operation['uri'] == operation_uri for operation in function['operation']))
        params = {'direction': 'input', 'data': data_uri, 'format': format_uri,
                  'operation': operation_uri, 'limit': '50', 'include': 'matches'}
        def result_key(resource_id, operations, data, formats):
            return (resource_id, tuple(sorted(value or '' for value in operations)), data or '',
                    tuple(sorted(value or '' for value in formats)))

        def record_items(target, items):
            for item in items:
                target[result_key(item['resource']['id'], [op['uri'] for op in item['function']['operations']],
                                  (item['io']['data'] or {}).get('uri'), [fmt['uri'] for fmt in item['io']['formats']])] += 1

        client, cursor, timings, found, strict_actual = Client(), None, [], set(), Counter()
        for _ in range(100):
            started = perf_counter()
            response = client.get('/_workflow/matches/', {**params, **({'cursor': cursor} if cursor else {})}, **CANONICAL)
            timings.append((perf_counter() - started) * 1000)
            self.assertEqual(response.status_code, 200, response.content)
            body = response.json()
            found.update(item['referenceFingerprint'] for item in body['items'])
            record_items(strict_actual, body['items'])
            cursor = body['pagination']['next']
            if not cursor:
                break
        else:
            self.fail('Strict matching did not finish within the rehearsal limit.')
        self.assertEqual(len(found), expected_per_copy * copies)

        def first_page(query):
            close_old_connections()
            try:
                start = perf_counter()
                response = Client().get('/_workflow/matches/', query, **CANONICAL)
                return response.status_code, (perf_counter() - start) * 1000
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=4) as pool:
            concurrent = list(pool.map(first_page, [params] * 4))
        self.assertTrue(all(status == 200 for status, _ in concurrent))

        def matches_or_unknown(values, requested, known):
            return requested in values or not values or any(not value or value not in known for value in values)

        unknown_per_copy = sum(
            (1 if not function['input'] else sum(1 for io in function['input']
                if matches_or_unknown([io['data']['uri']], data_uri, terms['data']) and
                matches_or_unknown([fmt['uri'] for fmt in io['format']], format_uri, terms['format'])))
            for tool in sample for function in tool['functions']
            if matches_or_unknown([op['uri'] for op in function['operation']], operation_uri, terms['operation']))
        unknown_params = {**params, 'include': 'unknown'}
        unknown_cursor, unknown_timings, unknown_found, unknown_actual = None, [], set(), Counter()
        for _ in range(1000):
            started = perf_counter()
            response = client.get('/_workflow/matches/', {**unknown_params, **({'cursor': unknown_cursor} if unknown_cursor else {})}, **CANONICAL)
            unknown_timings.append((perf_counter() - started) * 1000)
            self.assertEqual(response.status_code, 200, response.content)
            body = response.json()
            unknown_found.update(item['referenceFingerprint'] for item in body['items'])
            record_items(unknown_actual, body['items'])
            unknown_cursor = body['pagination']['next']
            if not unknown_cursor:
                break
        else:
            self.fail('Uncertain matching did not finish within the rehearsal limit.')
        self.assertEqual(len(unknown_found), unknown_per_copy * copies)
        strict_oracle, unknown_oracle = Counter(), Counter()
        for index in range(copies * len(sample)):
            for function in sample[index % len(sample)]['functions']:
                operations = [op['uri'] for op in function['operation']]
                ios = function['input'] or [{'data': {'uri': None}, 'format': []}]
                for io in ios:
                    data = io['data']['uri']
                    formats = [fmt['uri'] for fmt in io['format']]
                    key = result_key(f'wfscale-{index:05}', operations, data, formats)
                    if data == data_uri and format_uri in formats and operation_uri in operations:
                        strict_oracle[key] += 1
                    if (matches_or_unknown(operations, operation_uri, terms['operation']) and
                            matches_or_unknown([data], data_uri, terms['data']) and
                            matches_or_unknown(formats, format_uri, terms['format'])):
                        unknown_oracle[key] += 1
        self.assertEqual(strict_actual, strict_oracle)
        self.assertEqual(unknown_actual, unknown_oracle)
        percentile = lambda values: quantiles(values, n=20, method='inclusive')[18] if len(values) > 1 else values[0]
        print(json.dumps({'resources': len(resources), 'corpus': 'public-live-crawl' if corpus_path else 'synthetic-repeat',
            'ontology': 'preview-edam' if ontology else 'synthetic-flat',
            'functions': len(functions), 'io_records': len(io_rows),
            'strict_matches': len(found), 'strict_pages': len(timings), 'strict_median_ms': round(median(timings), 1),
            'strict_p95_ms': round(percentile(timings), 1), 'strict_slowest_ms': round(max(timings), 1),
            'four_concurrent_ms': [round(ms, 1) for _, ms in concurrent],
            'unknown_matches': len(unknown_found), 'unknown_pages': len(unknown_timings),
            'unknown_total_seconds': round(sum(unknown_timings) / 1000, 1), 'unknown_median_ms': round(median(unknown_timings), 1),
            'unknown_p95_ms': round(percentile(unknown_timings), 1), 'unknown_slowest_ms': round(max(unknown_timings), 1)}), flush=True)
        if corpus_path:
            self.assertLessEqual(percentile(timings), 2000, 'Strict matching exceeded the provisional p95 page budget.')
            self.assertLessEqual(percentile(unknown_timings), 2000, 'Uncertain matching exceeded the provisional p95 page budget.')
            self.assertLessEqual(max(timings + unknown_timings), 5000, 'Matching exceeded the provisional maximum page budget.')
            self.assertLessEqual(max(ms for _, ms in concurrent), 5000, 'Concurrent matching exceeded the provisional page budget.')

            output_frequencies = Counter(
                (io['data']['uri'], fmt['uri'], op['uri'])
                for tool in sample for function in tool['functions'] for io in function['output']
                for fmt in io['format'] for op in function['operation']
                if valid('data', io['data']['uri']) and valid('format', fmt['uri']) and valid('operation', op['uri']))
            output_data, output_format, output_operation = output_frequencies.most_common(1)[0][0]
            scenarios = [
                {'direction': 'output', 'data': output_data, 'format': output_format,
                 'operation': output_operation, 'include': 'matches', 'limit': '50'},
                {'direction': 'input', 'data': data_uri, 'include': 'unknown', 'limit': '50'},
            ]
            for query in scenarios:
                expected = Counter()
                direction = query['direction']
                for index, tool in enumerate(sample):
                    for function in tool['functions']:
                        operations = [op['uri'] for op in function['operation']]
                        if query.get('operation') and query['operation'] not in operations:
                            continue
                        ios = function[direction] or ([{'data': {'uri': None}, 'format': []}]
                                                     if query['include'] == 'unknown' else [])
                        for io in ios:
                            data = io['data']['uri']
                            formats = [item['uri'] for item in io['format']]
                            if query['include'] == 'matches':
                                accepted = data == query['data'] and (not query.get('format') or query['format'] in formats)
                            else:
                                accepted = matches_or_unknown([data], query['data'], terms['data'])
                            if accepted:
                                expected[(f'wfscale-{index:05}', tuple(sorted(value or '' for value in operations)),
                                          data or '', tuple(sorted(value or '' for value in formats)))] += 1
                actual, scenario_cursor, scenario_times = Counter(), None, []
                for page in range(1000):
                    started = perf_counter()
                    response = client.get('/_workflow/matches/', {**query, **({'cursor': scenario_cursor} if scenario_cursor else {})}, **CANONICAL)
                    scenario_times.append((perf_counter() - started) * 1000)
                    self.assertEqual(response.status_code, 200, response.content)
                    body = response.json()
                    for item in body['items']:
                        actual[(item['resource']['id'], tuple(sorted(op['uri'] or '' for op in item['function']['operations'])),
                                (item['io']['data'] or {}).get('uri') or '',
                                tuple(sorted(fmt['uri'] or '' for fmt in item['io']['formats'])))] += 1
                    scenario_cursor = body['pagination']['next']
                    if not scenario_cursor:
                        break
                    if (page + 1) % 100 == 0:
                        print(f'{direction} {query["include"]}: {page + 1} pages', flush=True)
                else:
                    self.fail('The full-corpus scenario did not finish within the rehearsal limit.')
                self.assertEqual(actual, expected)
                with ThreadPoolExecutor(max_workers=4) as pool:
                    parallel = list(pool.map(first_page, [query] * 4))
                self.assertTrue(all(status == 200 for status, _ in parallel))
                print(json.dumps({'direction': direction, 'include': query['include'], 'matches': sum(actual.values()),
                    'pages': len(scenario_times), 'total_seconds': round(sum(scenario_times) / 1000, 1),
                    'p95_ms': round(percentile(scenario_times), 1), 'slowest_ms': round(max(scenario_times), 1),
                    'four_concurrent_ms': [round(ms, 1) for _, ms in parallel]}), flush=True)
                self.assertLessEqual(percentile(scenario_times), 2000, 'Scenario exceeded the provisional p95 page budget.')
                self.assertLessEqual(max(scenario_times), 5000, 'Scenario exceeded the provisional maximum page budget.')
                self.assertLessEqual(max(ms for _, ms in parallel), 5000, 'Scenario exceeded the provisional concurrent budget.')
