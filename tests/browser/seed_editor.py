"""Add one disposable editor fixture; never overwrite an existing record."""
from copy import deepcopy
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from elasticsearch import Elasticsearch

from elixir.models import OtherID, PublicationMetadata, Resource
from elixir.serializers import ResourceSerializer
from elixirapp.test_resource_editor_contract import FIXTURES


if os.environ.get('BIOTOOLS_ALLOW_TEST_SEED') != 'biotools-refresh':
    raise RuntimeError('Explicit disposable-stack opt-in required.')
enriched = os.environ.get('BIOTOOLS_TEST_ENRICHED_EDITOR') == '1'
identifier = 'editor-enriched' if enriched else 'editor-demo'
if Resource.objects.filter(biotoolsID__iexact=identifier).exists():
    raise RuntimeError(f'Refusing to overwrite an existing {identifier} record.')
owner = get_user_model().objects.get(username='migration-test')
es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
if es.exists(index=settings.ELASTIC_SEARCH_INDEX, id=identifier):
    raise RuntimeError(f'Refusing to overwrite an existing indexed {identifier} document.')
data = deepcopy(FIXTURES['rich'])
data.update(biotoolsID=identifier, name='Enriched Editor Demo' if enriched else 'Editor Demo', editPermission={'type': 'private'})
# Browser checks do not call publication enrichment services. The backend rich
# preservation test covers publications with deterministic enrichment mocks.
for field in ('publication', 'relation', 'owner', 'validated', 'biotoolsCURIE'):
    data.pop(field, None)

def resolve_local_terms(value):
    if isinstance(value, dict):
        if value.get('uri', '').startswith('http://edamontology.org/'):
            value.pop('term', None)
        for child in value.values():
            resolve_local_terms(child)
    elif isinstance(value, list):
        for child in value:
            resolve_local_terms(child)

resolve_local_terms(data)
serializer = ResourceSerializer(data=data)
if not serializer.is_valid():
    raise RuntimeError(serializer.errors)
tool = serializer.save(owner=owner)
if enriched:
    tool.homepage_status = 2
    tool.elixir_badge = 4
    tool.save()
    metadata = PublicationMetadata.objects.create(title='Fictional preservation fixture', citationCount=3)
    metadata.authors.create(name='Fixture Author')
    tool.publication.create(pmid='12345', metadata=metadata)
    OtherID.objects.create(resource=tool, value='biotools:editor-previous-id', type='biotoolsCURIE')
es.index(index=settings.ELASTIC_SEARCH_INDEX, id=identifier, body=ResourceSerializer(tool).data)
es.indices.refresh(index=settings.ELASTIC_SEARCH_INDEX)
print(f'Created fictional {identifier}; existing records were not modified.')
