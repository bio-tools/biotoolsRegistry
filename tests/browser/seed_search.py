"""Add fictional search samples only to the opted-in disposable preview."""
import os
from datetime import datetime, timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from elasticsearch import Elasticsearch

from elixir.models import Resource, EditPermission, ToolType, Language, Topic, CollectionID
from elixir.serializers import ResourceSerializer


if os.environ.get('BIOTOOLS_ALLOW_TEST_SEED') != 'biotools-refresh':
    raise RuntimeError('Explicit disposable-stack opt-in required.')
identifiers = [f'workspace-sample-{i:02}' for i in range(1, 14)]
owner = get_user_model().objects.get(username='migration-test')
es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
es.cluster.health()
if Resource.objects.filter(biotoolsID__in=identifiers).exists() or any(
        es.exists(index=settings.ELASTIC_SEARCH_INDEX, id=identifier) for identifier in identifiers):
    raise RuntimeError('Refusing to overwrite existing search samples.')
documents = []
with transaction.atomic():
    for i, identifier in enumerate(identifiers, 1):
        tool = Resource.objects.create(
            biotoolsID=identifier, biotoolsCURIE='biotools:' + identifier,
            name=f'Workspace sample {i:02} (fictional)', owner=owner,
            editPermission=EditPermission.objects.create(type='private'),
            homepage='https://example.org/' + identifier,
            description='Fictional software record for local search and pagination checks. '
                        'Illustrative sequence analysis metadata; no real software is represented.',
            license='MIT', cost='Free of charge', accessibility='Open access',
            additionDate=datetime(2026, 1, i, tzinfo=timezone.utc))
        ToolType.objects.create(resource=tool, name='Command-line tool' if i % 2 else 'Web application')
        Language.objects.create(resource=tool, name='Python' if i % 2 else 'R')
        Topic.objects.create(resource=tool, term='Sequence analysis', uri='http://edamontology.org/topic_0080')
        CollectionID.objects.create(resource=tool, name='Local workspace samples')
        documents.append((identifier, ResourceSerializer(tool).data))
for identifier, document in documents:
    es.index(index=settings.ELASTIC_SEARCH_INDEX, id=identifier, body=document)
es.indices.refresh(index=settings.ELASTIC_SEARCH_INDEX)
print('Created 13 fictional workspace samples. Existing records were not changed.')
