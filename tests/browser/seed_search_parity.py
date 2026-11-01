"""Add one isolated domain to the existing disposable search samples."""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from elasticsearch import Elasticsearch

from elixir.models import Domain, DomainResource, Resource


if os.environ.get('BIOTOOLS_ALLOW_TEST_SEED') != 'biotools-refresh':
    raise RuntimeError('Explicit disposable-stack opt-in required.')
name = 'search-parity-fixture'
es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
if Domain.objects.filter(name=name).exists() or es.exists(index='domains', id=name):
    raise RuntimeError('Refusing to overwrite an existing domain.')
resources = Resource.objects.filter(visibility=1, biotoolsID__startswith='workspace-sample-')
if resources.count() != 13:
    raise RuntimeError('Seed the 13 workspace samples first.')
with transaction.atomic():
    domain = Domain.objects.create(name=name, owner=get_user_model().objects.get(username='migration-test'))
    DomainResource.objects.bulk_create([DomainResource(domain=domain, biotoolsID=resource.biotoolsID,
        name=resource.name, versionId=resource.versionId) for resource in resources])
    es.index(index='domains', id=name, body={'domain': name, 'resources': [
        {'biotoolsID': resource.biotoolsID} for resource in resources]})
es.indices.refresh(index='domains')
print('Created search-parity-fixture containing the 13 existing fictional samples.')
