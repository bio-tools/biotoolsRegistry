"""Session-backed forms using the same request handlers as token API clients."""
import logging
from types import SimpleNamespace

from django import forms
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST
from rest_framework.exceptions import APIException

from elixir.models import Resource
from elixir.view.resource import ResourceRequestView, ProcessResourceRequest
from elixirapp.browser_auth import browser_login_required


class RequestForm(forms.Form):
    type = forms.ChoiceField(label='Request', choices=(('editing', 'Editing rights'), ('ownership', 'Ownership')),
                            widget=forms.RadioSelect)


def invoke(view_class, request, method, data=None):
    mutation = SimpleNamespace(user=request.user, method=method.upper(), data=data or {},
                               authenticators=(), successful_authenticator=None)
    view = view_class()
    view.request = mutation
    view.check_permissions(mutation)
    return getattr(view, method)(mutation)


@browser_login_required
@require_http_methods(['GET', 'POST'])
def create(request, identifier):
    resource = get_object_or_404(Resource, visibility=1, biotoolsID__iexact=identifier)
    form = RequestForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                response = invoke(ResourceRequestView, request, 'put',
                                  {'resourceId': resource.biotoolsID, 'type': form.cleaned_data['type']})
                if response.status_code >= 400:
                    form.add_error(None, str(response.data))
                else:
                    messages.success(request, 'Request sent.')
                    return redirect('html:requests')
        except Exception:
            logging.getLogger(__name__).exception('Resource request could not be created')
            form.add_error(None, 'Request could not be sent. Please try again.')
    return render(request, 'html/resource_request.html', {'tool': resource, 'form': form},
                  status=400 if form.errors else 200)


@browser_login_required
@require_http_methods(['GET'])
def inbox(request):
    data = invoke(ResourceRequestView, request, 'get').data['requests']
    show_completed = request.GET.get('completed') == '1'
    for kind in data:
        data[kind] = [item for item in data[kind] if show_completed or not item['completed']]
    return render(request, 'html/resource_requests.html', {**data, 'show_completed': show_completed})


@browser_login_required
@require_POST
def conclude(request):
    try:
        response = invoke(ProcessResourceRequest, request, 'post', request.POST.dict())
        if response.status_code >= 400:
            messages.error(request, str(response.data.get('detail', response.data)))
        else:
            messages.success(request, 'Request accepted.' if response.data['accepted'] else 'Request declined.')
    except APIException as exc:
        messages.error(request, str(exc.detail))
    except Exception:
        logging.getLogger(__name__).exception('Resource request could not be concluded')
        messages.error(request, 'Request could not be confirmed. Check its status before retrying.')
    return redirect('html:requests')
