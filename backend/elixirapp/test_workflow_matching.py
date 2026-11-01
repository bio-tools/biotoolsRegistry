import copy
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from elixir.models import Data, EditPermission, Format, Function, Input, Ontology, Operation, Output, Resource
from elixir.resource_ui import resource_descriptor
from elixirapp.test_edam import seed_ontology

BASE = 'http://edamontology.org/'
CANONICAL = {'biotools.canonical': True}


@override_settings(DEBUG=False)
class WorkflowMatchingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_ontology()
        owner = User.objects.create_user('private-owner')
        permission = EditPermission.objects.create(type='private')
        cls.tool = Resource.objects.create(biotoolsID='candidate', name='Candidate', owner=owner, editPermission=permission)
        cls.hidden = Resource.objects.create(biotoolsID='hidden', name='Hidden', owner=owner, editPermission=permission, visibility=0)
        data = Data.objects.create(uri=BASE + 'data_0863', term='Sequence')
        other = Data.objects.create(uri=BASE + 'data_2044', term='Sequence name')
        cls.function = Function.objects.create(resource=cls.tool)
        Operation.objects.create(function=cls.function, uri=BASE + 'operation_0292', term='Alignment')
        cls.match = Input.objects.create(function=cls.function, data=data)
        Format.objects.create(input=cls.match, uri=BASE + 'format_1929', term='FASTA')
        # A separate input has the requested format but a different data type.
        other_input = Input.objects.create(function=cls.function, data=other)
        Format.objects.create(input=other_input, uri=BASE + 'format_1929', term='FASTA')
        # A separate function has the requested data but no operation or format.
        cls.missing = Function.objects.create(resource=cls.tool)
        Input.objects.create(function=cls.missing, data=data)
        hidden_function = Function.objects.create(resource=cls.hidden)
        Operation.objects.create(function=hidden_function, uri=BASE + 'operation_0292', term='Alignment')
        hidden_input = Input.objects.create(function=hidden_function, data=data)
        Format.objects.create(input=hidden_input, uri=BASE + 'format_1929', term='FASTA')

    def get(self, **params):
        return self.client.get('/_workflow/matches/', params, **CANONICAL)

    def query(self):
        return {'direction': 'input', 'data': BASE + 'data_0863', 'format': BASE + 'format_1929',
                'operation': BASE + 'operation_0292'}

    def test_correlated_matching_and_public_projection(self):
        response = self.get(**self.query())
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        self.assertEqual(len(body['items']), 1)
        item = body['items'][0]
        self.assertEqual(item['resource']['id'], 'candidate')
        self.assertEqual(item['io']['data']['uri'], BASE + 'data_0863')
        self.assertEqual([item['evidence'][key]['state'] for key in ('data', 'format', 'operation')], ['exact'] * 3)
        self.assertNotIn('private-owner', response.content.decode())
        self.assertNotIn('editPermission', response.content.decode())
        self.assertEqual(body['source']['consistency'], 'live')
        self.assertEqual(response['X-Biotools-Route'], 'django-workflow-matches')

    def test_no_cross_input_or_function_matches(self):
        self.match.format.all().delete()
        other = Function.objects.create(resource=self.tool)
        other_input = Input.objects.create(function=other, data=self.match.data)
        Format.objects.create(input=other_input, uri=BASE + 'format_1929', term='FASTA')
        self.assertEqual(self.get(**self.query()).json()['items'], [])

    def test_matching_is_independent_of_search_index_and_detects_annotation_edits(self):
        with patch('elasticsearch.Elasticsearch.search', side_effect=AssertionError('Search index must not be used')):
            before = self.get(**self.query()).json()['items'][0]
            Data.objects.filter(pk=self.match.data_id).update(term='Changed sequence label')
            after = self.get(**self.query()).json()['items'][0]
        self.assertEqual(before['function']['id'], after['function']['id'])
        self.assertNotEqual(before['referenceFingerprint'], after['referenceFingerprint'])

    def test_output_direction_and_visibility_change_during_scan(self):
        output = Output.objects.create(function=self.function, data=self.match.data)
        Format.objects.create(output=output, uri=BASE + 'format_1929', term='FASTA')
        params = {**self.query(), 'direction': 'output'}
        self.assertEqual(self.get(**params).json()['items'][0]['io']['direction'], 'output')
        from django.db.models import prefetch_related_objects
        def hide_then_prefetch(*args, **kwargs):
            Resource.objects.filter(pk=self.tool.pk).update(visibility=0)
            prefetch_related_objects(*args, **kwargs)
        with patch('django.db.models.prefetch_related_objects', side_effect=hide_then_prefetch):
            self.assertEqual(self.get(**params).json()['items'], [])

    def test_live_cursor_reflects_added_and_hidden_resources(self):
        def create_match(identifier):
            resource = Resource.objects.create(biotoolsID=identifier, name=identifier,
                                               owner=self.tool.owner, editPermission=self.tool.editPermission)
            function = Function.objects.create(resource=resource)
            Operation.objects.create(function=function, uri=BASE + 'operation_0292')
            item = Input.objects.create(function=function, data=self.match.data)
            Format.objects.create(input=item, uri=BASE + 'format_1929')
            return resource

        hidden = create_match('later-hidden')
        params = {**self.query(), 'limit': '1'}
        first = self.get(**params).json()
        self.assertEqual(first['items'][0]['resource']['id'], 'candidate')
        cursor = first['pagination']['next']
        self.assertTrue(cursor)
        Resource.objects.filter(pk=hidden.pk).update(visibility=0)
        create_match('later-added')
        second = self.get(**params, cursor=cursor).json()
        self.assertEqual([item['resource']['id'] for item in second['items']], ['later-added'])
        self.assertEqual(second['source']['consistency'], 'live')
        self.assertEqual(second['pagination']['completeScope'], 'live-scan')
        self.assertIn('change between pages', second['pagination']['note'])

    def test_function_details_preserve_io_identity_and_visibility(self):
        output = Output.objects.create(function=self.function, data=self.match.data)
        Format.objects.create(output=output, uri=BASE + 'format_1929', term='FASTA')
        Output.objects.create(function=self.function, data=Data.objects.create(uri=BASE + 'data_2044', term='Sequence name'))
        match = self.get(**self.query()).json()['items'][0]
        url = '/_workflow/function/'
        token = match['function']['token']
        response = self.client.get(url, {'ref': token}, **CANONICAL)
        self.assertEqual(response.status_code, 200, response.content)
        function = response.json()['function']
        self.assertEqual(function['id'], match['function']['id'])
        self.assertIn(match['io']['id'], [item['id'] for item in function['input']])
        self.assertEqual(function['output'][0]['data']['uri'], BASE + 'data_0863')
        missing_format = next(item for item in function['output'] if item['data']['uri'] == BASE + 'data_2044')
        self.assertEqual(missing_format['formats'], [])
        self.assertNotEqual(missing_format['id'], function['output'][0]['id'])
        self.assertEqual(self.client.get(url, {'ref': 'bad'}, **CANONICAL).status_code, 400)
        Resource.objects.filter(pk=self.tool.pk).update(visibility=0)
        self.assertEqual(self.client.get(url, {'ref': token}, **CANONICAL).status_code, 404)

    def test_designer_and_gallery_are_separate_routes(self):
        designer = self.client.get('/workflows/design/', **CANONICAL)
        self.assertEqual(designer.status_code, 200)
        self.assertContains(designer, 'workflow-designer')
        self.assertContains(designer, 'requires its interactive assets')
        gallery = self.client.get('/workflows', **CANONICAL)
        self.assertEqual(gallery.status_code, 200)
        self.assertContains(gallery, 'Design a workflow from tool functions')

    def test_related_unknown_obsolete_and_operation_are_distinguished(self):
        params = {'direction': 'input', 'data': BASE + 'data_0006', 'mode': 'related', 'include': 'unknown',
                  'operation': BASE + 'operation_0292'}
        items = self.get(**params).json()['items']
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['evidence']['data']['relation'], 'annotated_more_specific')
        self.assertEqual(items[0]['evidence']['data']['direction'], 'input')
        self.assertEqual(items[-1]['evidence']['operation']['reasons'], ['missing'])
        Data.objects.filter(pk=self.match.data_id).update(uri=BASE + 'data_9998')
        params = {'direction': 'input', 'data': BASE + 'data_0863', 'include': 'unknown'}
        items = self.get(**params).json()['items']
        self.assertEqual(items[0]['evidence']['data']['reasons'], ['obsolete'])
        params['data'] = BASE + 'data_9998'
        item = self.get(**params).json()['items'][0]
        self.assertTrue(item['evidence']['data']['obsolete'])

    def test_strict_related_search_keeps_correlated_descendants(self):
        params = {'direction': 'input', 'data': BASE + 'data_0006', 'format': BASE + 'format_1915',
                  'operation': BASE + 'operation_0004', 'mode': 'related', 'include': 'matches'}
        items = self.get(**params).json()['items']
        self.assertEqual(len(items), 2)
        for item in items:
            self.assertEqual([item['evidence'][key]['state'] for key in ('data', 'format', 'operation')], ['related'] * 3)

    def test_unknown_search_preserves_noncanonical_and_term_only_values(self):
        Data.objects.filter(pk=self.match.data_id).update(uri=(BASE + 'data_2044').upper())
        params = {'direction': 'input', 'data': BASE + 'data_0863', 'include': 'unknown'}
        items = self.get(**params).json()['items']
        self.assertEqual(items[0]['evidence']['data']['reasons'], ['unrecognized'])
        Data.objects.filter(pk=self.match.data_id).update(uri=BASE + 'data_2044 ')
        items = self.get(**params).json()['items']
        self.assertEqual(items[0]['evidence']['data']['reasons'], ['unrecognized'])
        Data.objects.filter(pk=self.match.data_id).update(uri=None, term='Sequence')
        items = self.get(**params).json()['items']
        self.assertEqual(items[0]['evidence']['data']['reasons'], ['term_only'])

    def test_unknown_format_and_operation_survive_case_insensitive_database_collation(self):
        self.match.format.update(uri=(BASE + 'format_1929').upper())
        self.function.operation.update(uri=(BASE + 'operation_0292').upper())
        params = {'direction': 'input', 'data': BASE + 'data_0863', 'format': BASE + 'format_1915',
                  'operation': BASE + 'operation_0004', 'include': 'unknown'}
        items = self.get(**params).json()['items']
        self.assertEqual(items[0]['evidence']['format']['reasons'], ['unrecognized'])
        self.assertEqual(items[0]['evidence']['operation']['reasons'], ['unrecognized'])

    def test_uncertain_search_falls_back_when_prefilter_is_too_large(self):
        params = {**self.query(), 'include': 'unknown', 'limit': '1'}
        def results():
            items, cursor = [], None
            while True:
                body = self.get(**params, **({'cursor': cursor} if cursor else {})).json()
                items.extend(item['referenceFingerprint'] for item in body['items'])
                cursor = body['pagination']['next']
                if not cursor:
                    return sorted(items)
        expected = results()
        with patch('elixir.workflow_matching.PREFILTER_LIMIT', 0):
            self.assertEqual(results(), expected)

    def test_connection_comparison_distinguishes_related_conflict_and_unknown(self):
        def annotation(data):
            return {'data': {'uri': BASE + data, 'term': data} if data else None,
                    'formats': [{'uri': BASE + 'format_1929', 'term': 'FASTA'}]}
        def compare(output, input_data):
            response = self.client.post('/_workflow/compare/',
                data=json.dumps({'output': annotation(output), 'input': annotation(input_data)}),
                content_type='application/json', **CANONICAL)
            self.assertEqual(response.status_code, 200, response.content)
            return response.json()
        related = compare('data_0006', 'data_0863')
        self.assertEqual(related['state'], 'related')
        self.assertEqual(related['dimensions']['data']['relation'], 'annotated_more_specific')
        self.assertEqual(compare('data_0863', 'data_2044')['state'], 'conflict')
        self.assertEqual(compare('data_0863', None)['state'], 'unknown')
        self.assertEqual(compare('data_9998', 'data_9998')['state'], 'unknown')

    def test_missing_direction_and_conflicts_are_explicit(self):
        Function.objects.create(resource=self.tool)
        params = {'direction': 'input', 'data': BASE + 'data_0863', 'include': 'all'}
        cursor, items = None, []
        while True:
            body = self.get(**params, **({'cursor': cursor} if cursor else {})).json()
            items.extend(body['items'])
            cursor = body['pagination']['next']
            if not cursor:
                break
        self.assertEqual({item['evidence']['data']['state'] for item in items}, {'exact', 'conflict', 'unknown'})
        self.assertTrue(any(item['io']['id'] is None and item['evidence']['data']['reasons'] == ['missing'] for item in items))

    def test_bounded_pagination_and_cursor_revision(self):
        params = {'direction': 'input', 'data': BASE + 'data_0863', 'include': 'all', 'limit': '1'}
        with patch('elixir.workflow_matching.SCAN_LIMIT', 2):
            cursor, references = None, []
            while True:
                response = self.get(**params, **({'cursor': cursor} if cursor else {}))
                self.assertEqual(response.status_code, 200, response.content)
                body = response.json()
                references.extend(item['referenceFingerprint'] for item in body['items'])
                self.assertLessEqual(body['pagination']['scanned'], 2)
                cursor = body['pagination']['next']
                if not cursor:
                    break
            self.assertEqual(len(references), 3)
            self.assertEqual(len(set(references)), 3)
            self.assertEqual(body['pagination']['completeScope'], 'live-scan')
            first = self.get(**params).json()['pagination']['next']
            self.assertEqual(self.get(**{**params, 'data': BASE + 'data_2044', 'cursor': first}).status_code, 409)
            ontology = Ontology.objects.get(name='EDAM_data')
            tree = json.loads(ontology.data)
            tree['text'] = 'Changed label'
            ontology.data = json.dumps(tree)
            ontology.save()
            self.assertEqual(self.get(**params, cursor=first).status_code, 409)

    def test_sparse_exact_search_finds_later_results_without_empty_pages(self):
        Input.objects.bulk_create([Input(function=self.function, data=self.match.data) for _ in range(105)])
        other = Data.objects.create(uri=BASE + 'data_2044', term='Sequence name')
        later = Input.objects.create(function=self.function, data=other)
        Format.objects.create(input=later, uri=BASE + 'format_1915', term='Format')
        params = {'direction': 'input', 'data': BASE + 'data_2044', 'format': BASE + 'format_1915',
                  'operation': BASE + 'operation_0292'}
        body = self.get(**params).json()
        self.assertEqual(len(body['items']), 1)
        self.assertEqual(body['items'][0]['io']['data']['uri'], BASE + 'data_2044')
        self.assertTrue(body['pagination']['complete'])

    def test_invalid_unavailable_and_privacy_changes(self):
        for params in ({'direction': 'input'}, {'direction': 'other', 'data': BASE + 'data_0863'},
                       {'direction': 'input', 'data': BASE + 'data_8888'},
                       {'direction': 'input', 'data': BASE + 'data_0863', 'cursor': 'invalid'}):
            self.assertEqual(self.get(**params).status_code, 400)
        descriptor = copy.deepcopy(resource_descriptor())
        descriptor['contract']['fields']['function']['item']['fields']['input']['item']['fields']['format']['public'] = False
        with patch('elixir.workflow_matching.resource_descriptor', return_value=descriptor):
            self.assertEqual(self.get(**self.query()).status_code, 503)
        Ontology.objects.filter(name='EDAM_data').delete()
        self.assertEqual(self.get(**self.query()).status_code, 503)
        self.assertEqual(self.client.post('/_workflow/matches/', **CANONICAL).status_code, 405)
