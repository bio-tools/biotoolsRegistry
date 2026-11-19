from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth.models import User
from django.db import connection, connections
from django.test import TransactionTestCase, override_settings
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from elixir.models import EditPermission, Resource, ResourceIdentifier
from elixir.serializers import ResourceSerializer, ResourceUpdateSerializer
from elixirapp.test_resource_editor_contract import submission_from_readback


@override_settings(GITHUB_ECOSYSTEM_ON=False)
class PermanentResourceIdentifierTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user('identifier-admin', is_superuser=True)
        self.client = APIClient(HTTP_ACCEPT='application/json')
        self.client.force_authenticate(self.user)
        self.payload = {'biotoolsID': 'Permanent-ID', 'name': 'Permanent ID test',
                        'description': 'A test resource.', 'homepage': 'https://example.org/tool'}
        self.es = self.enterContext(patch('elixir.view.resource.es'))
        self.es.search.return_value = {'hits': {'total': {'value': 1}, 'hits': [{'_id': 'test'}]}}
        self.enterContext(patch('elixir.view.resource.notify_admins'))

    def test_id_remains_reserved_after_edit_deletion_and_physical_record_removal(self):
        created = self.client.post('/t/', self.payload, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        update = submission_from_readback(created.data, ResourceUpdateSerializer())
        update['name'] = 'Updated tool'
        updated = self.client.put('/t/Permanent-ID', update, format='json')
        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertEqual(updated.data['biotoolsID'], 'Permanent-ID')
        self.assertEqual(self.client.delete('/t/Permanent-ID').status_code, 204)
        self.assertEqual(self.client.get('/t/Permanent-ID').status_code, 404)
        for identifier in ('Permanent-ID', 'permanent-id', 'PERMANENT-ID'):
            response = self.client.post('/t/', {**self.payload, 'biotoolsID': identifier}, format='json')
            self.assertEqual(response.status_code, 400, response.data)
            self.assertIn('biotoolsID', response.data)
        Resource.objects.filter(biotoolsID__iexact='permanent-id').delete()
        self.assertTrue(ResourceIdentifier.objects.filter(pk='permanent-id').exists())
        response = self.client.post('/t/', self.payload, format='json')
        self.assertEqual(response.status_code, 400, response.data)

    def test_invisible_historical_record_cannot_be_claimed(self):
        Resource.objects.create(biotoolsID='Old-ID', biotoolsCURIE='biotools:Old-ID', visibility=0,
                                owner=self.user, editPermission=EditPermission.objects.create(type='private'))
        response = self.client.post('/t/', {**self.payload, 'biotoolsID': 'old-id'}, format='json')
        self.assertEqual(response.status_code, 400, response.data)

    def test_admin_cannot_bypass_registration_or_change_an_identifier(self):
        from django.contrib import admin
        resource_admin = admin.site._registry[Resource]
        self.assertFalse(resource_admin.has_add_permission(None))
        self.assertFalse(resource_admin.has_delete_permission(None))
        self.assertIn('biotoolsID', resource_admin.get_readonly_fields(None))
        self.assertIn('biotoolsCURIE', resource_admin.get_readonly_fields(None))

    def test_failed_save_rolls_back_the_reservation(self):
        serializer = ResourceSerializer(data=self.payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with patch('elixir.serialization.resource_serialization.resource.Resource.objects.create',
                   side_effect=RuntimeError('simulated failure')):
            with self.assertRaises(RuntimeError):
                serializer.save(owner=self.user)
        self.assertFalse(ResourceIdentifier.objects.filter(pk='permanent-id').exists())

    def test_simultaneous_registrations_cannot_claim_the_same_id(self):
        barrier = Barrier(2, timeout=15)
        def register():
            try:
                serializer = ResourceSerializer(data=self.payload)
                if not serializer.is_valid():
                    return 'invalid'
                barrier.wait()
                try:
                    serializer.save(owner=self.user)
                    return 'created'
                except ValidationError:
                    return 'invalid'
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: register(), range(2)))
        self.assertCountEqual(results, ['created', 'invalid'])
        self.assertEqual(Resource.objects.filter(biotoolsID__iexact='permanent-id').count(), 1)

    def test_migration_reserves_active_and_hidden_history_once(self):
        permission = EditPermission.objects.create(type='private')
        for identifier, visible in [('Old-ID', 1), ('OLD-id', 0), ('Retired', 0)]:
            Resource.objects.create(biotoolsID=identifier, biotoolsCURIE='biotools:' + identifier,
                                    visibility=visible, owner=self.user, editPermission=permission)
        migration = import_module('elixir.migrations.0009_resource_identifier')
        migration.reserve_existing_identifiers(apps, SimpleNamespace(connection=connection))
        self.assertEqual(set(ResourceIdentifier.objects.values_list('identifier', flat=True)), {'old-id', 'retired'})
