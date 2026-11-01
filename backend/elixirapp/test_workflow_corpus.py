from django.test import SimpleTestCase

from elixirapp.tests.collect_workflow_corpus import anonymous


class WorkflowCorpusTests(SimpleTestCase):
    def test_only_annotation_uris_are_retained(self):
        tool = {
            'biotoolsID': 'private-in-local-fixture', 'name': 'Not retained',
            'function': [{'note': 'Not retained', 'operation': [{'uri': 'operation', 'term': 'Not retained'}],
                          'input': [{'data': {'uri': 'data', 'term': 'Not retained'},
                                     'format': [{'uri': 'format', 'term': 'Not retained'}]}]}],
        }
        self.assertEqual(anonymous(tool), {'functions': [{'operation': [{'uri': 'operation'}],
            'input': [{'data': {'uri': 'data'}, 'format': [{'uri': 'format'}]}], 'output': []}]})

    def test_invalid_ontology_shapes_fail_instead_of_being_silently_discarded(self):
        with self.assertRaises(ValueError):
            anonymous({'function': [{'operation': ['not-an-object']}]})
