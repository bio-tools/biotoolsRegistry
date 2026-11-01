"""Native forms for remaining record/domain actions; shared API handlers own writes."""
import logging
from types import SimpleNamespace

from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import APIException

from elixir.models import Domain, Resource
from elixir.permissions import IsDomainOwnerOrEditorOrReadOnly
from elixir.serializers import DomainSerializer, ResourceSerializer
from elixir.view.domain import DomainView, DomainResourceView, manages_domain, NOT_DELETABLE_DOMAINS
from elixir.view.resource import DisownResourceView, ResourceDetail
from elixirapp.browser_auth import browser_login_required
from elixirapp.resource_editor import revision

logger = logging.getLogger(__name__)


def command(view, user, method, data=None, **kwargs):
    request = SimpleNamespace(user=user, method=method.upper(), data=data or {},
                              authenticators=(), successful_authenticator=None)
    view.request = request
    view.check_permissions(request)
    return getattr(view, method)(request, **kwargs)


class ConfirmationForm(forms.Form):
    revision = forms.CharField(widget=forms.HiddenInput)
    action = forms.ChoiceField(choices=[('disown', 'Disown'), ('delete', 'Delete')])
    confirm = forms.BooleanField(label='I confirm this action cannot be undone here.')


@browser_login_required
@require_http_methods(['GET', 'HEAD', 'POST'])
def record(request, identifier):
    resource = get_object_or_404(Resource, biotoolsID__iexact=identifier, visibility=1)
    token = revision(resource, ResourceSerializer(resource).data)
    form = ConfirmationForm(request.POST or None, initial={'revision': token})
    status = 200
    if request.method == 'POST':
        if form.is_valid():
            try:
                with transaction.atomic():
                    current = get_object_or_404(Resource.objects.select_for_update(), pk=resource.pk, visibility=1)
                    if form.cleaned_data['revision'] != revision(current, ResourceSerializer(current).data):
                        form.add_error(None, 'This record changed. Reload and review it before confirming again.')
                        status = 409
                    else:
                        action = form.cleaned_data['action']
                        result = command(DisownResourceView() if action == 'disown' else ResourceDetail(), request.user,
                                         'post' if action == 'disown' else 'delete', biotoolsID=current.biotoolsID)
                        if result.status_code >= 400:
                            form.add_error(None, result.data.get('detail', 'Action rejected.'))
                            status = result.status_code
                        else:
                            messages.success(request, 'Record disowned.' if action == 'disown' else 'Record removed.')
                            return redirect('/' + current.biotoolsID if action == 'disown' else '/profile')
            except APIException as exc:
                form.add_error(None, str(exc.detail))
                status = exc.status_code
            except Http404:
                form.add_error(None, 'This record is no longer current. Nothing was changed.')
                status = 409
            except Exception:
                logger.exception('Record management failed')
                form.add_error(None, 'The action could not be confirmed. Reload the record before retrying.')
                status = 503
        else:
            status = 400
    return render(request, 'html/manage_record.html', {'resource': resource, 'form': form,
        'can_disown': request.user.is_superuser or resource.owner_id == request.user.pk,
        'can_delete': request.user.is_superuser}, status=status)


class DomainForm(forms.Form):
    revision = forms.CharField(required=False, widget=forms.HiddenInput)
    domain = forms.RegexField(r'^[A-Za-z0-9-]{2,40}$', label='Domain identifier', max_length=40)
    title = forms.CharField(required=False, max_length=50)
    sub_title = forms.CharField(label='Subtitle', required=False, max_length=150)
    description = forms.CharField(required=False, widget=forms.Textarea)
    is_private = forms.BooleanField(label='Private domain setting', required=False,
        help_text='This existing setting does not hide the domain from the public directory.')
    resources = forms.CharField(label='Tool identifiers (one per line)', required=False, widget=forms.Textarea)
    tag = forms.CharField(label='Tags (one per line)', required=False, widget=forms.Textarea(attrs={'rows': 3}))
    collection = forms.CharField(label='Collections (one per line)', required=False, widget=forms.Textarea(attrs={'rows': 3}))
    editors = forms.CharField(label='Editors (one username per line)', required=False, widget=forms.Textarea(attrs={'rows': 3}))
    confirm_delete = forms.BooleanField(label='I confirm deletion of this domain.', required=False)

    def payload(self):
        data = {key: self.cleaned_data[key] for key in ('domain', 'title', 'sub_title', 'description', 'is_private')}
        for key in ('resources', 'tag', 'collection', 'editors'):
            data[key] = list(dict.fromkeys(line.strip() for line in self.cleaned_data[key].splitlines() if line.strip()))
        data['resources'] = [{'biotoolsID': value} for value in data['resources']]
        return data


def domain_initial(domain):
    if domain is None:
        return {'is_private': True}
    data = dict(DomainSerializer(domain).data)
    data['revision'] = revision(domain, data)
    data['resources'] = '\n'.join(item['biotoolsID'] for item in data['resources'])
    for field in ('tag', 'collection', 'editors'):
        data[field] = '\n'.join(data[field])
    return data


@browser_login_required
@require_http_methods(['GET', 'HEAD'])
def domains(request):
    query = Domain.objects.filter(visibility=1)
    if not request.user.is_superuser:
        query = query.filter(Q(owner=request.user) | Q(editors=request.user)).distinct()
    return render(request, 'html/manage_domains.html', {'domains': query.order_by('name')})


@browser_login_required
@require_http_methods(['GET', 'HEAD', 'POST'])
def domain(request, identifier=None):
    current = get_object_or_404(Domain, name=identifier.lower(), visibility=1) if identifier else None
    if current and not IsDomainOwnerOrEditorOrReadOnly().has_object_permission(
            SimpleNamespace(user=request.user, method='PUT'), None, current):
        raise PermissionDenied
    initial = domain_initial(current)
    form = DomainForm(request.POST or None, initial=initial)
    owner = current is None or manages_domain(request.user, current)
    if current:
        form.fields['domain'].disabled = True
    if not owner:
        form.fields['editors'].disabled = True
    status = 200
    if request.method == 'POST':
        if form.is_valid():
            try:
                with transaction.atomic():
                    if current:
                        current = get_object_or_404(Domain.objects.select_for_update(), pk=current.pk, visibility=1)
                        if form.cleaned_data['revision'] != revision(current, DomainSerializer(current).data):
                            form.add_error(None, 'This domain changed. Copy your draft, then reload before saving.')
                            status = 409
                    if not form.errors:
                        action = request.POST.get('action', 'save')
                        if action == 'delete' and (current is None or not form.cleaned_data['confirm_delete']):
                            form.add_error('confirm_delete', 'Confirm domain deletion first.')
                            status = 400
                        elif action not in {'save', 'delete'}:
                            form.add_error(None, 'Unknown action.')
                            status = 400
                        else:
                            view = DomainResourceView() if current else DomainView()
                            result = command(view, request.user, 'delete' if action == 'delete' else 'put' if current else 'post',
                                             form.payload(), **({'domain': current.name} if current else {}))
                            messages.success(request, 'Domain deleted.' if action == 'delete' else 'Domain saved.')
                            return redirect('/domain-manager' if action == 'delete' else '/edit-domain/' + result.data['domain'])
            except APIException as exc:
                if isinstance(exc.detail, dict):
                    for field, errors in exc.detail.items():
                        form.add_error(field if field in form.fields else None, str(errors))
                else:
                    form.add_error(None, str(exc.detail))
                status = exc.status_code
            except Http404:
                form.add_error(None, 'This domain is no longer current. Copy your draft and reload.')
                status = 409
            except Exception:
                logger.exception('Domain management failed')
                form.add_error(None, 'Save could not be confirmed. Copy your draft and reload before retrying.')
                status = 503
        else:
            status = 400
    # A bounded native lookup aids membership editing without replacing the form draft.
    query = request.GET.get('q', '').strip()[:100]
    matches = Resource.objects.filter(visibility=1).filter(Q(name__icontains=query) | Q(biotoolsID__icontains=query))[:30] if query else []
    return render(request, 'html/manage_domain.html', {'form': form, 'domain': current, 'query': query, 'matches': matches,
        'can_manage': owner, 'can_delete': current and owner and current.name not in NOT_DELETABLE_DOMAINS,
        'editors_config': {'initial': str(form['editors'].value() or '').splitlines()}}, status=status)
