from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import close_old_connections, connection
from django.test import TransactionTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from elixir.models import Domain, DomainNameLock
from elixir.serializers import DomainSerializer
from elixir.view.domain import DomainView


class ConcurrentDomainCreationTests(TransactionTestCase):
    def test_same_name_is_created_once_after_both_requests_validate(self):
        if connection.vendor != 'mysql':
            self.skipTest('Concurrent row-lock behavior requires MySQL.')
        user = User.objects.create_user('domain-concurrency')
        barrier = None
        validate = DomainSerializer.is_valid

        def coordinated_validation(serializer, *args, **kwargs):
            result = validate(serializer, *args, **kwargs)
            barrier.wait()
            return result

        def create(name):
            close_old_connections()
            try:
                request = APIRequestFactory().post('/d', {'domain': name}, format='json')
                force_authenticate(request, user=user)
                response = DomainView.as_view()(request)
                return response.status_code
            finally:
                close_old_connections()

        with patch.object(DomainSerializer, 'is_valid', coordinated_validation), patch('elixir.view.domain.index_domain') as index:
            for number in range(5):
                barrier = Barrier(2, timeout=10)
                name = f'concurrent-name-{number}'
                with ThreadPoolExecutor(max_workers=2) as pool:
                    results = list(pool.map(create, [name.upper(), name]))
                self.assertEqual(sorted(results), [201, 400])
                self.assertEqual(Domain.objects.filter(name=name, visibility=1).count(), 1)
                self.assertEqual(DomainNameLock.objects.filter(name=name).count(), 1)
            self.assertEqual(index.call_count, 5)
