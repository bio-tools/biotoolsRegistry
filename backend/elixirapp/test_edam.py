import json
from unittest.mock import patch

from django.conf import settings
from django.test import Client, TestCase, override_settings

from elixir.edam_lookup import EdamUnavailable, EdamVocabulary
from elixir.models import Ontology
from elixirapp.edam import EdamField
from elixirapp.test_html import HTML_REQUEST


def node(scope, number, label, children=None, **metadata):
    return {'text': label, 'data': {'uri': f'http://edamontology.org/{scope}_{number}'},
            'children': children or [], 'definition': 'A fixture definition.',
            'exact_synonyms': [], 'narrow_synonyms': [], **metadata}


def seed_ontology():
    branches = {
        'topic': node('topic', '0003', 'Topic', [
            node('topic', '0091', 'Bioinformatics', [node('topic', '0080', 'Sequence analysis')],
                 exact_synonyms=['Computational biology']),
            node('topic', '3071', 'Data management'),
            *[node('topic', f'{2000 + i}', f'Fixture topic {i:02}') for i in range(25)]]),
        'operation': node('operation', '0004', 'Operation', [node('operation', '0292', 'Sequence alignment')]),
        'data': node('data', '0006', 'Data', [node('data', '0863', 'Sequence'), node('data', '2044', 'Sequence name')]),
        'format': node('format', '1915', 'Format', [node('format', '1929', 'FASTA', narrow_synonyms=['FASTA format'])]),
    }
    for scope, tree in branches.items():
        Ontology.objects.create(name='EDAM_' + scope, data=json.dumps(tree))
    Ontology.objects.create(name='EDAM_obsolete', data=json.dumps(node('topic', '9999', 'Deprecated', [
        node('data', '9998', 'Old sequence'), node('topic', '9997', 'Old topic')])))


class EdamTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_ontology()

    def test_permanent_lookup_matches_preview_for_all_route_modes(self):
        query = '?scope=topic&q=computational%20biology'
        preview = self.client.get('/edam/terms/' + query, **HTML_REQUEST)
        self.assertEqual(preview.status_code, 200)
        response = self.client.get('/_edam/terms/' + query, **{'biotools.canonical': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), preview.json())
        self.assertEqual(response['X-Biotools-Route'], 'django-edam')
        self.assertEqual(response['X-Robots-Tag'], 'noindex, follow')
        self.assertEqual(self.client.post('/_edam/terms/', **{'biotools.canonical': True}).status_code, 405)

    def test_bounded_scoped_synonym_lookup_and_suggestion_hints(self):
        with self.assertNumQueries(2):
            response = self.client.get('/edam/terms/?scope=topic', **HTML_REQUEST)
        body = response.json()
        self.assertEqual(len(body['items']), 20)
        self.assertTrue(body['more'])
        self.assertEqual(response['Cache-Control'], 'no-store')
        response = self.client.get('/edam/terms/', {'scope': 'topic', 'q': 'computational biology'}, **HTML_REQUEST)
        self.assertEqual(response.json()['items'][0]['term'], 'Bioinformatics')
        body = self.client.get('/edam/terms/', {'scope': 'topic', 'q': '',
                               'suggest': 'http://edamontology.org/topic_3071'}, **HTML_REQUEST).json()
        self.assertEqual(body['items'][0]['term'], 'Data management')
        self.assertEqual(body['suggestions'][0]['term'], 'Data management')
        for scope, query in (('operation', 'alignment'), ('data', 'sequence'), ('format', 'FASTA')):
            body = self.client.get('/edam/terms/', {'scope': scope, 'q': query}, **HTML_REQUEST).json()
            self.assertTrue(body['items'])
            self.assertTrue(all('/' + scope + '_' in item['uri'] for item in body['items']))

    def test_resolve_selected_outside_query_and_scope_branch_rules(self):
        for params in ({'scope': 'topic', 'id': 'http://edamontology.org/data_0863'},
                       {'scope': 'topic', 'id': 'http://edamontology.org/topic_8888'},
                       {'scope': 'topic', 'branch': 'http://edamontology.org/topic_0091', 'id': 'http://edamontology.org/topic_3071'},
                       {'scope': 'topic', 'branch': 'http://edamontology.org/topic_8888'}):
            self.assertEqual(self.client.get('/edam/terms/', params, **HTML_REQUEST).status_code, 400)
        result = self.client.get('/edam/terms/', {'scope': 'topic', 'branch': 'http://edamontology.org/topic_0091'}, **HTML_REQUEST).json()
        self.assertEqual({item['term'] for item in result['items']}, {'Bioinformatics', 'Sequence analysis'})
        selected = self.client.get('/edam/terms/', {'scope': 'data', 'id': 'http://edamontology.org/data_9998'}, **HTML_REQUEST).json()
        self.assertTrue(selected['items'][0]['obsolete'])
        self.assertEqual(selected['items'][0]['term'], 'Old sequence')
        self.assertEqual(self.client.get('/edam/terms/?scope=data&q=Old', **HTML_REQUEST).json()['items'], [])

    def test_activated_vocabulary_changes_revision_and_labels_without_changing_uri(self):
        params = {'scope': 'topic', 'id': 'http://edamontology.org/topic_0091'}
        before = self.client.get('/edam/terms/', params, **HTML_REQUEST).json()
        ontology = Ontology.objects.get(name='EDAM_topic')
        tree = json.loads(ontology.data)
        tree['children'][0]['text'] = 'Updated bioinformatics label'
        tree['children'][0]['exact_synonyms'].append('New synonym')
        ontology.data = json.dumps(tree)
        ontology.save()
        after = self.client.get('/edam/terms/', params, **HTML_REQUEST).json()
        self.assertNotEqual(before['vocabulary']['revision'], after['vocabulary']['revision'])
        self.assertEqual(after['items'][0]['uri'], params['id'])
        self.assertEqual(after['items'][0]['term'], 'Updated bioinformatics label')
        self.assertIn('New synonym', after['items'][0]['synonyms'])
        self.assertEqual(after['vocabulary']['revision'], EdamVocabulary('topic').revision)

    def test_invalid_inputs_fail_before_ontology_reads(self):
        queries = ['scope=unknown', 'scope=topic&scope=data', 'scope=topic&unknown=x', 'scope=topic&q=' + 'x' * 129,
                   'scope=topic&q=%00', 'scope=topic&id=javascript:alert(1)',
                   'scope=topic&id=http://edamontology.org/topic_0091&q=x',
                   'scope=topic&' + '&'.join(['id=http://edamontology.org/topic_0091'] * 21)]
        for query in queries:
            with self.subTest(query=query), self.assertNumQueries(0):
                response = self.client.get('/edam/terms/?' + query, **HTML_REQUEST)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()['error']['code'], 'invalid_edam')
        self.assertEqual(self.client.post('/edam/terms/', **HTML_REQUEST).status_code, 405)

    def test_missing_ontology_is_recoverable(self):
        Ontology.objects.filter(name='EDAM_topic').delete()
        response = self.client.get('/edam/terms/?scope=topic', **HTML_REQUEST)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['error']['code'], 'edam_unavailable')
        with self.assertRaises(EdamUnavailable):
            EdamVocabulary('topic')

    def test_form_resolves_authoritative_labels_and_preserves_values_after_errors(self):
        values = {'label': '', 'topic': ['http://edamontology.org/topic_0091', 'http://edamontology.org/topic_3071'],
                  'data': ['http://edamontology.org/data_0863'], 'format': ['http://edamontology.org/format_1929'],
                  'topic_term': '<script>forged</script>', 'scope': 'format'}
        response = self.client.post('/edam/', values, **HTML_REQUEST)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'This field is required.', status_code=400)
        self.assertContains(response, 'Bioinformatics', status_code=400)
        self.assertNotContains(response, 'forged', status_code=400)
        self.assertEqual(response.context['selectors'][0]['config']['initial'], values['topic'])
        values['label'] = 'Example annotation'
        response = self.client.post('/edam/', values, **HTML_REQUEST)
        self.assertEqual(response.status_code, 200)
        payload = response.context['payload']
        self.assertEqual(payload['input']['data'], {'uri': values['data'][0], 'term': 'Sequence'})
        self.assertEqual(payload['input']['format'], [{'uri': values['format'][0], 'term': 'FASTA'}])
        self.assertEqual(payload['topic'][0]['term'], 'Bioinformatics')
        values['data'].append('http://edamontology.org/data_2044')
        self.assertContains(self.client.post('/edam/', values, **HTML_REQUEST), 'Choose one term only.', status_code=400)

    def test_form_csrf_and_unknown_uri_rejection(self):
        client = Client(enforce_csrf_checks=True)
        token = client.get('/edam/', **HTML_REQUEST).cookies[settings.CSRF_COOKIE_NAME].value
        self.assertEqual(client.post('/edam/', {'label': 'Example'}, **HTML_REQUEST).status_code, 403)
        self.assertEqual(client.post('/edam/', {'label': 'Example', 'csrfmiddlewaretoken': token}, **HTML_REQUEST).status_code, 200)
        response = self.client.post('/edam/', {'label': 'Example', 'topic': 'http://edamontology.org/topic_8888'}, **HTML_REQUEST)
        self.assertContains(response, 'Unknown EDAM identifier', status_code=400)
        self.assertEqual(EdamField('topic', required=False).clean(['']), [])

    def test_promoted_search_rejects_unknown_ids_before_elasticsearch(self):
        condition = {'type': 'ontology', 'scope': 'server', 'field': 'topic', 'values': ['http://edamontology.org/topic_8888']}
        with patch('elixirapp.search_workspace.search_tools') as search:
            response = self.client.get('/search/data/', {'advanced': json.dumps([condition])}, **HTML_REQUEST)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error']['field'], 'advanced')
        search.assert_not_called()

    def test_public_serializers_keep_their_existing_identity_validation(self):
        from elixir.serializers import TopicSerialiser, OperationSerializer, DataSerializer, FormatSerializer
        cases = [(TopicSerialiser, 'topic_0091', 'Bioinformatics'),
                 (OperationSerializer, 'operation_0292', 'Sequence alignment'),
                 (DataSerializer, 'data_0863', 'Sequence'),
                 (FormatSerializer, 'format_1929', 'FASTA')]
        for serializer, identifier, label in cases:
            uri = 'http://edamontology.org/' + identifier
            with self.subTest(serializer=serializer):
                selected = serializer(data={'uri': uri})
                self.assertTrue(selected.is_valid(), selected.errors)
                self.assertEqual(selected.validated_data, {'uri': uri, 'term': label})
                mismatch = serializer(data={'uri': uri, 'term': 'Forged label'})
                self.assertFalse(mismatch.is_valid())
