from datetime import timedelta
import json
from unittest.mock import patch

from background_task.models import CompletedTask, Task
from background_task.tasks import tasks
from django.core import mail
from django.contrib.auth.models import User
from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from elixir.tasks import notify_resource_request, create_ecosystem_tool, update_ecosystem_tool, delete_ecosystem_tool
from elixir.serializers import ResourceUpdateSerializer
from elixirapp.test_resource_editor_contract import submission_from_readback


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   ADMIN_EMAIL_LIST=['reviewer@example.org'])
class BackgroundTaskTests(TransactionTestCase):
    def test_ecosystem_operations_run_from_the_queue(self):
        record = {'biotoolsID': 'queue-test', 'name': 'Test'}
        due = timezone.now() - timedelta(seconds=1)
        with patch('elixir.tasks.ecosytem_handle_tool_operations') as operation:
            create_ecosystem_tool(record, 'editor', schedule=due)
            update_ecosystem_tool(record, 'editor', schedule=due)
            delete_ecosystem_tool('queue-test', 'editor', schedule=due)
            for _ in range(3):
                self.assertTrue(tasks.run_next_task())
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(CompletedTask.objects.count(), 3)
        self.assertEqual([call.args[2] for call in operation.call_args_list], ['CREATE', 'UPDATE', 'DELETE'])
        self.assertEqual(json.loads(operation.call_args_list[0].args[1]), record)
        self.assertEqual(json.loads(operation.call_args_list[2].args[1]), {'biotoolsID': 'queue-test'})

    def test_ecosystem_failure_is_rescheduled(self):
        due = timezone.now() - timedelta(seconds=1)
        with patch('elixir.tasks.ecosytem_handle_tool_operations', side_effect=RuntimeError('temporary failure')):
            create_ecosystem_tool({'biotoolsID': 'queue-test'}, 'editor', schedule=due)
            self.assertTrue(tasks.run_next_task())
        task = Task.objects.get()
        self.assertEqual(task.attempts, 1)
        self.assertIn('temporary failure', task.last_error)
        self.assertGreater(task.run_at, timezone.now())

    def test_queued_notification_runs_and_is_recorded(self):
        notify_resource_request('editor', 'A test request', schedule=timezone.now() - timedelta(seconds=1))
        self.assertEqual(Task.objects.count(), 1)
        self.assertTrue(tasks.run_next_task())
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(CompletedTask.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('A test request', mail.outbox[0].body)


@override_settings(GITHUB_ECOSYSTEM_ON=True)
class EcosystemRouteQueueTests(TransactionTestCase):
    def test_create_update_and_delete_queue_expected_operations(self):
        user = User.objects.create_user('ecosystem-editor', is_superuser=True)
        client = APIClient(HTTP_ACCEPT='application/json')
        client.force_authenticate(user)
        record = {'biotoolsID': 'ecosystem-queue-test', 'name': 'Queue test',
                  'description': 'A test tool.', 'homepage': 'https://example.org/test'}
        with patch('elixir.view.resource.es') as es, patch('elixir.view.resource.notify_admins'), \
             patch('elixir.tasks.ecosytem_handle_tool_operations') as operation:
            es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'test'}]}}
            response = client.post('/t/', record, format='json')
            self.assertEqual(response.status_code, 201, response.data)
            update = submission_from_readback(response.data, ResourceUpdateSerializer())
            update['name'] = 'Updated queue test'
            response = client.put('/t/ecosystem-queue-test', update, format='json')
            self.assertEqual(response.status_code, 200, response.data)
            response = client.delete('/t/ecosystem-queue-test')
            self.assertEqual(response.status_code, 204, response.data)
            self.assertEqual(Task.objects.count(), 3)
            Task.objects.update(run_at=timezone.now() - timedelta(seconds=1))
            for _ in range(3):
                self.assertTrue(tasks.run_next_task())
        self.assertEqual([call.args[2] for call in operation.call_args_list], ['CREATE', 'UPDATE', 'DELETE'])
        self.assertEqual(json.loads(operation.call_args_list[1].args[1])['name'], 'Updated queue test')
