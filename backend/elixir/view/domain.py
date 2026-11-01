"""Domain writes shared by token API and native session forms."""
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from elasticsearch.exceptions import TransportError
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from elixir.management_errors import ManagementUnavailable
from elixir.models import Domain
from elixir.permissions import IsDomainOwnerOrEditorOrReadOnly
from elixir.serializers import DomainSerializer, DomainUpdateSerializer, PublicSubdomainSerializer, SubdomainNameSerializer
from elixir.view.resource import es

NOT_DELETABLE_DOMAINS = {'all', 'covid-19'}


def manages_domain(user, domain):
    return user.is_authenticated and (user.is_superuser or domain.owner_id == user.pk)


def index_domain(domain, *, delete=False):
    try:
        index = getattr(settings, 'ELASTIC_SEARCH_DOMAIN_INDEX', 'domains')
        if delete:
            es.delete(index=index, doc_type='_doc', id=domain.name, ignore=[404], refresh='wait_for')
        else:
            es.index(index=index, doc_type='_doc', id=domain.name,
                     body=DomainSerializer(domain).data, refresh='wait_for')
    except TransportError as exc:
        raise ManagementUnavailable() from exc


class DomainView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsDomainOwnerOrEditorOrReadOnly)

    def get(self, request, format=None):
        domains = Domain.objects.filter(visibility=1)
        if request.user.is_authenticated and not request.user.is_superuser:
            domains = domains.filter(Q(owner=request.user) | Q(editors=request.user)).distinct()
            serializer = SubdomainNameSerializer(domains, many=True, context={'request': request})
        else:
            serializer = PublicSubdomainSerializer(domains, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, format=None):
        serializer = DomainSerializer(data=request.data, context={'request': request, 'request_type': 'POST'})
        serializer.is_valid(raise_exception=True)
        domain = serializer.save(owner=request.user)
        index_domain(domain)
        return Response(serializer.data, status=201)


class DomainResourceView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsDomainOwnerOrEditorOrReadOnly)

    def get_object(self, name, *, lock=False):
        query = Domain.objects.select_for_update() if lock else Domain.objects.all()
        obj = get_object_or_404(query, name=name.lower(), visibility=1)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, domain, format=None):
        if domain.lower() == 'all':
            result = es.search(index=getattr(settings, 'ELASTIC_SEARCH_DOMAIN_INDEX', 'domains'),
                               body={'size': 10000, 'query': {'match_all': {}}})
            return Response({'count': result['hits']['total']['value'],
                             'data': [hit['_source'] for hit in result['hits']['hits']]})
        return Response({'count': 1, 'data': DomainSerializer(self.get_object(domain)).data})

    @transaction.atomic
    def put(self, request, domain=None, format=None):
        # The legacy API also accepts PUT /d with the identifier in the body.
        if not isinstance(request.data, dict) or not isinstance(request.data.get('domain'), str):
            raise ValidationError({'domain': 'Supply a domain identifier.'})
        name = domain or request.data.get('domain', '')
        old = self.get_object(name, lock=True)
        if request.data.get('domain', '').lower() != old.name:
            raise ValidationError({'domain': 'The URL and domain identifier must match.'})
        data = request.data.copy()
        current_editors = set(old.editors.values_list('username', flat=True))
        data.setdefault('editors', sorted(current_editors))
        serializer = DomainUpdateSerializer(data=data, context={'request': request, 'request_type': 'PUT'})
        serializer.is_valid(raise_exception=True)
        if not manages_domain(request.user, old) and {user.username for user in serializer.validated_data['editors']} != current_editors:
            raise PermissionDenied('Only the owner can change domain editors.')
        old.visibility = 0
        old.save(update_fields=['visibility'])
        updated = serializer.save(owner=old.owner)
        index_domain(updated)
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, domain, format=None):
        current = self.get_object(domain, lock=True)
        if not manages_domain(request.user, current) or current.name in NOT_DELETABLE_DOMAINS:
            raise PermissionDenied('Only the owner can delete a domain; all and covid-19 are protected.')
        current.visibility = 0
        current.save(update_fields=['visibility'])
        index_domain(current, delete=True)
        return Response(status=204)
