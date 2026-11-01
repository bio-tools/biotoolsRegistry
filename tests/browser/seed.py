"""Run with manage.py shell only in the disposable migration stack."""
import os
from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from elasticsearch import Elasticsearch
from rest_framework.test import APIClient

from elixir.models import Resource


if os.environ.get('BIOTOOLS_ALLOW_TEST_SEED') != 'biotools-refresh':
    raise RuntimeError('Explicit disposable-stack opt-in required.')
password = os.environ['BIOTOOLS_TEST_PASSWORD']
User = get_user_model()
if Resource.objects.exists() or User.objects.filter(username='migration-test').exists():
    raise RuntimeError('Refusing to overwrite existing records or the fixture account.')
es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
if any(es.indices.exists(index=index) for index in (settings.ELASTIC_SEARCH_INDEX, 'domains')):
    raise RuntimeError('Provision an empty disposable index first; this script never purges data.')
# Use the real search mapping; the API test mapping does not support name sorting.
with patch('elixir.management.commands.es_regenerate.cpu_count', return_value=2):
    call_command('es_regenerate')
call_command('parse_edam')
user = User.objects.create_user('migration-test', 'migration@example.invalid', password)
EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
client = APIClient()
client.force_authenticate(user)
response = client.post('/tool/', {
    'biotoolsID': 'migration-fixture',
    'name': 'Migration Fixture',
    'description': 'Deterministic local migration regression fixture.',
    'homepage': 'https://example.org/migration-fixture',
    'toolType': ['Command-line tool'],
}, format='json')
if response.status_code != 201:
    raise RuntimeError(f'Fixture registration failed: {response.status_code} {response.data}')
es.indices.refresh(index=settings.ELASTIC_SEARCH_INDEX)
print('Created migration-fixture and migration-test in the disposable stack.')
