"""Exercise ambiguous index outcomes only on the disposable refresh stack."""
import os
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from elasticsearch.exceptions import TransportError
from rest_framework.test import APIRequestFactory, force_authenticate

from elixir.models import Domain, Resource
from elixir.serializers import ResourceSerializer
from elixir.view.domain import DomainResourceView, DomainView, es, index_domain
from elixir.view.resource import DisownResourceView, ResourceDetail, ResourceList

if os.environ.get('BIOTOOLS_READINESS_REHEARSAL') != 'biotools-refresh':
    raise RuntimeError('Explicit disposable-stack rehearsal opt-in required.')
if settings.GITHUB_ECOSYSTEM_ON or settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
    raise RuntimeError('The rehearsal requires disabled external integrations and console-only email.')

name = 'reconcile-' + uuid4().hex[:16]
index = getattr(settings, 'ELASTIC_SEARCH_DOMAIN_INDEX', 'domains')
user = get_user_model().objects.get(username='migration-test')
factory = APIRequestFactory()
assert not Domain.objects.filter(name=name).exists() and not es.exists(index=index, id=name)


def invoke(view, method, data=None):
    request = getattr(factory, method)('/d/' + name if view is DomainResourceView else '/d', data or {}, format='json')
    force_authenticate(request, user=user)
    return view.as_view()(request, **({'domain': name} if view is DomainResourceView else {}))


def applied_then_timeout(method):
    def perform(*args, **kwargs):
        method(*args, **kwargs)
        raise TransportError(503, 'simulated timeout after index write')
    return perform


try:
    real_index = es.index
    with patch.object(es, 'index', side_effect=applied_then_timeout(real_index)):
        assert invoke(DomainView, 'post', {'domain': name, 'title': 'Original'}).status_code == 503
    assert not Domain.objects.filter(name=name, visibility=1).exists()
    assert es.exists(index=index, id=name)
    es.delete(index=index, doc_type='_doc', id=name, ignore=[404], refresh='wait_for')
    assert not es.exists(index=index, id=name)
    print('Creation: removed index document after database rollback.')

    assert invoke(DomainView, 'post', {'domain': name, 'title': 'Original'}).status_code == 201
    with patch.object(es, 'index', side_effect=applied_then_timeout(real_index)):
        assert invoke(DomainResourceView, 'put', {'domain': name, 'title': 'Changed'}).status_code == 503
    current = Domain.objects.get(name=name, visibility=1)
    assert current.title == 'Original'
    assert es.get(index=index, id=name)['_source']['title'] == 'Changed'
    index_domain(current)
    assert es.get(index=index, id=name)['_source']['title'] == 'Original'
    print('Update: restored the visible database version to the index.')

    real_delete = es.delete
    with patch.object(es, 'delete', side_effect=applied_then_timeout(real_delete)):
        assert invoke(DomainResourceView, 'delete').status_code == 503
    current = Domain.objects.get(name=name, visibility=1)
    assert not es.exists(index=index, id=name)
    index_domain(current)
    assert es.get(index=index, id=name)['_source']['title'] == 'Original'
    print('Deletion: restored the visible database version to the index.')
finally:
    if Domain.objects.filter(name=name, visibility=1).exists():
        assert invoke(DomainResourceView, 'delete').status_code == 204
    elif es.exists(index=index, id=name):
        es.delete(index=index, doc_type='_doc', id=name, ignore=[404], refresh='wait_for')
    assert not Domain.objects.filter(name=name, visibility=1).exists()
    assert not es.exists(index=index, id=name)
    print('Disposed of the unique rehearsal domain.')

identifier = 'reconcile-tool-' + uuid4().hex[:12]
resource_index = settings.ELASTIC_SEARCH_INDEX
admin = get_user_model().objects.get(username='migration-management-admin', is_superuser=True)
assert not Resource.objects.filter(biotoolsID=identifier).exists()


def resource_request(view, method, actor, data=None):
    request = getattr(factory, method)('/t/' + identifier, data or {}, format='json')
    force_authenticate(request, user=actor)
    return view.as_view()(request, **({'biotoolsID': identifier} if view is not ResourceList else {}))


def hits():
    result = es.search(index=resource_index, body={'query': {'match': {'biotoolsID': identifier}}})
    records = result['hits']['hits']
    assert all(hit['_source']['biotoolsID'] == identifier for hit in records)
    return records


def restore_resource(current, document_id):
    es.index(index=resource_index, doc_type='_doc', id=document_id,
             body=ResourceSerializer(current).data, refresh='wait_for')


try:
    payload = {'name': 'Readiness reconciliation ' + identifier,
               'description': 'A disposable index recovery fixture.',
               'homepage': 'https://example.org/reconciliation', 'biotoolsID': identifier}
    assert resource_request(ResourceList, 'post', user, payload).status_code == 201
    records = hits()
    assert len(records) == 1
    document_id = records[0]['_id']
    real_index = es.index
    with patch.object(es, 'index', side_effect=applied_then_timeout(real_index)):
        assert resource_request(DisownResourceView, 'post', user).status_code == 503
    current = Resource.objects.get(biotoolsID=identifier, visibility=1)
    assert current.owner_id == user.pk and hits()[0]['_source']['owner'] == 'admin'
    restore_resource(current, document_id)
    assert hits()[0]['_source']['owner'] == user.username
    print('Disown: restored the database owner to the search document.')

    real_delete = es.delete
    with patch.object(es, 'delete', side_effect=applied_then_timeout(real_delete)):
        assert resource_request(ResourceDetail, 'delete', admin).status_code == 503
    current = Resource.objects.get(biotoolsID=identifier, visibility=1)
    assert not hits()
    restore_resource(current, document_id)
    assert len(hits()) == 1 and hits()[0]['_source']['owner'] == user.username
    print('Record deletion: restored the visible database version to the index.')
finally:
    if Resource.objects.filter(biotoolsID=identifier, visibility=1).exists():
        assert resource_request(ResourceDetail, 'delete', admin).status_code == 204
    assert not Resource.objects.filter(biotoolsID=identifier, visibility=1).exists()
    assert not hits()
    print('Disposed of the unique rehearsal record.')
