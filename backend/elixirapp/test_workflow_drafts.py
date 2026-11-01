import json
import hashlib
import uuid
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import signing
from django.db import close_old_connections, connection, connections
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TransactionTestCase
from django.test.utils import CaptureQueriesContext

from elixir.models import EditPermission, Format, Function, Output, Resource, WorkflowDesign
from elixir.workflow_matching import reference
from elixirapp import test_workflow_matching as matching

BASE, CANONICAL = matching.BASE, matching.CANONICAL


class WorkflowDraftTests(matching.WorkflowMatchingTests):
    def setUp(self):
        self.owner = User.objects.get(username='private-owner')
        self.other = User.objects.create_user('another-user')
        self.client.force_login(self.owner)
        output = Output.objects.create(function=self.function, data=self.match.data)
        Format.objects.create(output=output, uri=BASE + 'format_1929', term='FASTA')

    def graph(self):
        response = self.get(**self.query()).json()
        candidate = response['items'][0]
        details = self.client.get('/_workflow/function/', {'ref': candidate['function']['token']}, **CANONICAL).json()
        step = {'id': 'a', 'note': 'Important note', 'resource': details['resource'], 'function': details['function'],
                'schemaRevision': response['schemaRevision'], 'vocabularyRevisions': response['vocabularyRevisions'],
                'selection': {'direction': 'input', 'ioId': candidate['io']['id'],
                              'fingerprint': candidate['referenceFingerprint'], 'evidence': candidate['evidence']}}
        return {'version': 1, 'steps': [step], 'connections': []}

    def send(self, method, url, body=None, revision=None):
        headers = {**CANONICAL, **({'HTTP_IF_MATCH': revision} if revision else {})}
        return getattr(self.client, method)(url, data=json.dumps(body or {}), content_type='application/json', **headers)

    def create(self):
        response = self.send('post', '/_workflow/designs/', {'title': 'My draft', 'graph': self.graph()})
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()

    def test_ownership_concurrent_updates_and_csrf(self):
        design = self.create()
        url = '/_workflow/designs/' + design['id'] + '/'
        first = self.client.get(url, **CANONICAL)
        self.assertEqual(first.status_code, 200)
        graph = first.json()['graph']
        updated = self.send('put', url, {'title': 'Updated', 'graph': graph}, design['revision'])
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.send('put', url, {'title': 'Lost update', 'graph': graph}, design['revision']).status_code, 409)
        self.assertEqual(self.client.get(url, **CANONICAL).json()['title'], 'Updated')
        self.client.force_login(self.other)
        self.assertEqual(self.client.get('/_workflow/designs/', HTTP_X_BIOTOOLS_USER=str(self.owner.pk), **CANONICAL).status_code, 409)
        self.assertEqual(self.client.get(url, **CANONICAL).status_code, 404)
        self.assertEqual(self.send('delete', url, revision=updated.json()['revision']).status_code, 404)
        self.assertEqual(self.client.get('/_workflow/designs/', **CANONICAL).json()['items'], [])
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.owner)
        self.assertEqual(csrf.post('/_workflow/designs/', data='{}', content_type='application/json', **CANONICAL).status_code, 403)

    def test_share_revoke_hidden_and_read_only(self):
        design = self.create()
        url = '/_workflow/designs/' + design['id'] + '/'
        shared = self.send('post', url + 'share/', {'action': 'create'}, design['revision'])
        self.assertEqual(shared.status_code, 200)
        token, revision = shared.json()['token'], shared.json()['revision']
        self.client.logout()
        read = self.send('post', '/_workflow/shared/', {'token': token})
        self.assertEqual(read.status_code, 200)
        self.assertTrue(read.json()['readOnly'])
        self.assertEqual(read['Referrer-Policy'], 'no-referrer')
        self.assertEqual(self.send('put', url, {}, revision).status_code, 401)
        Resource.objects.filter(pk=self.tool.pk).update(visibility=0)
        self.assertEqual(self.send('post', '/_workflow/shared/', {'token': token}).status_code, 404)
        self.client.force_login(self.owner)
        unresolved = self.client.get(url, **CANONICAL)
        self.assertEqual(unresolved.status_code, 200)
        self.assertEqual(unresolved.json()['graph']['steps'][0]['note'], 'Important note')
        self.assertEqual(unresolved.json()['unresolved'], ['a'])
        self.assertNotIn('Candidate', unresolved.content.decode())
        copy = self.send('post', '/_workflow/designs/', {'title': 'Recovered copy', 'graph': unresolved.json()['graph']})
        self.assertEqual(copy.status_code, 201, copy.content)
        self.assertEqual(WorkflowDesign.objects.get(pk=design['id']).graph['steps'][0]['resource']['name'], 'Candidate')
        Resource.objects.filter(pk=self.tool.pk).update(visibility=1)
        revoked = self.send('post', url + 'share/', {'action': 'revoke'}, revision)
        self.assertEqual(revoked.status_code, 200)
        self.assertEqual(self.send('post', '/_workflow/shared/', {'token': token}).status_code, 404)
        self.assertTrue(WorkflowDesign.objects.filter(pk=design['id']).exists())

    def test_invalid_graph_never_replaces_saved_draft(self):
        design = self.create()
        url = '/_workflow/designs/' + design['id'] + '/'
        graph = self.client.get(url, **CANONICAL).json()['graph']
        broken = deepcopy(graph)
        broken['steps'].append(deepcopy(broken['steps'][0]))
        self.assertEqual(self.send('put', url, {'title': 'Invalid', 'graph': broken}, design['revision']).status_code, 400)
        self.assertEqual(self.client.get(url, **CANONICAL).json()['graph'], graph)
        self.assertEqual(self.send('delete', url, revision=design['revision']).status_code, 200)
        self.assertEqual(self.client.get(url, **CANONICAL).status_code, 404)

    def test_malformed_term_and_overlong_unicode_are_rejected(self):
        graph = self.graph()
        del graph['steps'][0]['function']['input'][0]['data']['term']
        response = self.send('post', '/_workflow/designs/', {'title': 'Invalid', 'graph': graph})
        self.assertEqual(response.status_code, 400)
        for field in ('data', 'ioId'):
            graph = self.graph()
            if field == 'data':
                del graph['steps'][0]['function']['input'][0]['data']
            else:
                del graph['steps'][0]['selection']['ioId']
            self.assertEqual(self.send('post', '/_workflow/designs/', {'title': 'Invalid', 'graph': graph}).status_code, 400)
        graph = self.graph()
        graph['steps'][0]['note'] = '🧬' * 501
        response = self.send('post', '/_workflow/designs/', {'title': 'Invalid', 'graph': graph})
        self.assertEqual(response.status_code, 400)

    def test_deleted_function_preserves_a_private_placeholder_and_blocks_sharing(self):
        design = self.create()
        url = '/_workflow/designs/' + design['id'] + '/'
        token = self.send('post', url + 'share/', {'action': 'create'}, design['revision']).json()['token']
        self.function.delete()
        self.assertEqual(self.send('post', '/_workflow/shared/', {'token': token}).status_code, 404)
        recovered = self.client.get(url, **CANONICAL).json()
        self.assertEqual(recovered['unresolved'], ['a'])
        self.assertEqual(recovered['graph']['steps'][0]['note'], 'Important note')
        self.assertNotIn('Candidate', json.dumps(recovered))
        self.assertEqual(WorkflowDesign.objects.get(pk=design['id']).graph['steps'][0]['resource']['name'], 'Candidate')

    def test_duplicate_steps_do_not_repeat_function_queries(self):
        design = self.create()
        url = '/_workflow/designs/' + design['id'] + '/'
        token = self.send('post', url + 'share/', {'action': 'create'}, design['revision']).json()['token']
        with CaptureQueriesContext(connection) as baseline:
            self.assertEqual(self.send('post', '/_workflow/shared/', {'token': token}).status_code, 200)
        draft = WorkflowDesign.objects.get(pk=design['id'])
        original = draft.graph['steps'][0]
        draft.graph['steps'] = [{**original, 'id': 'step-' + str(index)} for index in range(10)]
        WorkflowDesign.objects.filter(pk=draft.pk).update(graph=draft.graph)
        with CaptureQueriesContext(connection) as expanded:
            response = self.send('post', '/_workflow/shared/', {'token': token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['graph']['steps']), 10)
        self.assertLessEqual(len(expanded), len(baseline) + 1)

    def test_invalid_connection_evidence_and_cycles_are_rejected(self):
        from elixir.workflow_drafts import validate_graph
        graph = self.graph()
        second = deepcopy(graph['steps'][0])
        second['id'] = 'b'
        graph['steps'].append(second)
        output = graph['steps'][0]['function']['output'][0]['id']
        input_io = second['function']['input'][0]['id']
        graph['connections'] = [{'id': 'x', 'from': {'step': 'a', 'io': output}, 'to': {'step': 'b', 'io': input_io},
                                 'evidence': 'exact', 'reason': ''}]
        validate_graph(graph)
        graph['connections'].append({'id': 'y', 'from': {'step': 'b', 'io': output}, 'to': {'step': 'a', 'io': input_io},
                                     'evidence': 'exact', 'reason': ''})
        with self.assertRaisesRegex(ValueError, 'cycles'):
            validate_graph(graph)
        graph['connections'].pop()
        graph['connections'][0]['evidence'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'evidence'):
            validate_graph(graph)

    def test_duplicate_create_is_idempotent_and_save_revokes_sharing(self):
        payload = {'id': str(uuid.uuid4()), 'title': 'Retry-safe draft', 'graph': self.graph()}
        created = self.send('post', '/_workflow/designs/', payload)
        retried = self.send('post', '/_workflow/designs/', payload)
        self.assertEqual((created.status_code, retried.status_code), (201, 200))
        self.assertEqual(created.json()['id'], retried.json()['id'])
        self.assertEqual(self.send('post', '/_workflow/designs/', {**payload, 'title': 'Different'}).status_code, 409)
        url = '/_workflow/designs/' + created.json()['id'] + '/'
        share = self.send('post', url + 'share/', {'action': 'create'}, created.json()['revision']).json()
        self.assertEqual(self.send('post', '/_workflow/shared/', {'token': share['token']}).status_code, 200)
        saved = self.send('put', url, {'title': 'Changed', 'graph': payload['graph']}, share['revision'])
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(self.send('post', '/_workflow/shared/', {'token': share['token']}).status_code, 404)


class WorkflowDraftConcurrencyTests(TransactionTestCase):
    def test_simultaneous_saves_and_duplicate_creates_do_not_lose_work(self):
        owner = User.objects.create_user('workflow-concurrency')
        graph = {'version': 1, 'steps': [], 'connections': []}
        draft = WorkflowDesign.objects.create(owner=owner, title='Original', graph=graph)
        clients = [Client(), Client()]
        for client in clients:
            client.force_login(owner)

        def race(method, url, bodies, revision=None):
            barrier = Barrier(2)
            def submit(index):
                close_old_connections()
                try:
                    barrier.wait(timeout=10)
                    response = getattr(clients[index], method)(url, data=json.dumps(bodies[index]),
                        content_type='application/json', **CANONICAL,
                        **({'HTTP_IF_MATCH': revision} if revision else {}))
                    return response.status_code
                finally:
                    connections.close_all()
            with ThreadPoolExecutor(max_workers=2) as pool:
                return sorted(pool.map(submit, range(2)))

        url = '/_workflow/designs/' + str(draft.pk) + '/'
        self.assertEqual(race('put', url, [{'title': 'First', 'graph': graph},
                         {'title': 'Second', 'graph': graph}], str(draft.revision)), [200, 409])
        draft.refresh_from_db()
        self.assertIn(draft.title, ('First', 'Second'))
        identifier = str(uuid.uuid4())
        create = {'id': identifier, 'title': 'One draft', 'graph': graph}
        self.assertEqual(race('post', '/_workflow/designs/', [create, create]), [200, 201])
        self.assertEqual(WorkflowDesign.objects.filter(pk=identifier, owner=owner).count(), 1)

    def test_isolated_migration_rollback_and_backup_restore(self):
        owner = User.objects.create_user('workflow-backup')
        graph = {'version': 1, 'steps': [], 'connections': []}
        draft = WorkflowDesign.objects.create(owner=owner, title='Backed up', graph=graph, share_digest='a' * 64)
        backup = WorkflowDesign.objects.filter(pk=draft.pk).values('id', 'owner_id', 'title', 'graph', 'revision', 'share_digest').get()
        try:
            MigrationExecutor(connection).migrate([('elixir', '0006_domain_name_lock')])
            self.assertNotIn(WorkflowDesign._meta.db_table, connection.introspection.table_names())
        finally:
            MigrationExecutor(connection).migrate([('elixir', '0007_workflow_design')])
        WorkflowDesign.objects.create(**backup)
        restored = WorkflowDesign.objects.filter(pk=draft.pk).values('id', 'owner_id', 'title', 'graph', 'revision', 'share_digest').get()
        self.assertEqual(restored, backup)

    def test_shared_read_serializes_with_hiding_and_revocation(self):
        from elixirapp.workflow_drafts import function_details

        for action in ('hide', 'revoke'):
            with self.subTest(action=action):
                owner = User.objects.create_user('workflow-race-' + action)
                permission = EditPermission.objects.create(type='public')
                resource = Resource.objects.create(biotoolsID='workflow-race-' + action, name='Visible tool',
                                                   owner=owner, editPermission=permission)
                function = Function.objects.create(resource=resource)
                token = signing.dumps({'resource': resource.pk, 'function': function.pk}, salt='biotools.workflow-function.v1')
                step = {'id': 'step', 'note': '', 'resource': {'id': resource.biotoolsID, 'name': resource.name,
                        'revision': {'token': 'snapshot'}}, 'function': {'id': reference('function', resource.pk, function.pk),
                        'token': token, 'operations': [], 'input': [], 'output': []}, 'schemaRevision': '',
                        'vocabularyRevisions': {}, 'selection': {'direction': 'input', 'ioId': None,
                        'fingerprint': '', 'evidence': {}}}
                secret = 'test-share-token-' + action + '-' + 'x' * 32
                design = WorkflowDesign.objects.create(owner=owner, title='Shared design',
                    graph={'version': 1, 'steps': [step], 'connections': []},
                    share_digest=hashlib.sha256(secret.encode()).hexdigest())
                reached, release, writer_started, writer_done = Event(), Event(), Event(), Event()

                def pause_after_check(value):
                    result = function_details(value)
                    reached.set()
                    if not release.wait(10):
                        raise RuntimeError('Timed out waiting for the race test.')
                    return result

                def read():
                    close_old_connections()
                    try:
                        return Client().post('/_workflow/shared/', data=json.dumps({'token': secret}),
                                             content_type='application/json', **CANONICAL).status_code
                    finally:
                        connections.close_all()

                def change():
                    close_old_connections()
                    try:
                        writer_started.set()
                        if action == 'hide':
                            Resource.objects.filter(pk=resource.pk).update(visibility=0)
                        else:
                            WorkflowDesign.objects.filter(pk=design.pk).update(share_digest=None)
                        writer_done.set()
                    finally:
                        connections.close_all()

                with patch('elixirapp.workflow_drafts.function_details', side_effect=pause_after_check):
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        reader = pool.submit(read)
                        try:
                            self.assertTrue(reached.wait(10))
                            writer = pool.submit(change)
                            self.assertTrue(writer_started.wait(10))
                            self.assertFalse(writer_done.wait(.3))
                        finally:
                            release.set()
                        self.assertEqual(reader.result(timeout=10), 200)
                        writer.result(timeout=10)
                response = Client().post('/_workflow/shared/', data=json.dumps({'token': secret}),
                                         content_type='application/json', **CANONICAL)
                self.assertEqual(response.status_code, 404)
