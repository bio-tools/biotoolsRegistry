"""Add only the fictional detail demo to an already provisioned local preview."""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from elasticsearch import Elasticsearch

from elixir.models import Resource
from elixir.serializers import ResourceSerializer
from elixirapp.tests.detail_fixtures import create_detail_fixture


if os.environ.get('BIOTOOLS_ALLOW_TEST_SEED') != 'biotools-refresh':
    raise RuntimeError('Explicit disposable-stack opt-in required.')
if Resource.objects.filter(biotoolsID__iexact='detail-demo').exists():
    raise RuntimeError('Refusing to overwrite an existing detail-demo record.')
owner = get_user_model().objects.get(username='migration-test')
es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
es.cluster.health()
if es.exists(index=settings.ELASTIC_SEARCH_INDEX, id='detail-demo'):
    raise RuntimeError('Refusing to overwrite an existing indexed detail-demo document.')
tool = create_detail_fixture(owner)
es.index(index=settings.ELASTIC_SEARCH_INDEX, id='detail-demo', body=ResourceSerializer(tool).data)
es.indices.refresh(index=settings.ELASTIC_SEARCH_INDEX)
print('Created fictional detail-demo; existing records were not modified.')
