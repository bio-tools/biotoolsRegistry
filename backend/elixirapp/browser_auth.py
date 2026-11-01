"""Session-only authentication for the isolated HTML mount; API auth is unchanged."""
from functools import wraps
from urllib.parse import urlencode

from django import forms
from django.contrib.auth import logout as end_session
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.csrf import csrf_failure as default_csrf_failure
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST
from dj_rest_auth.app_settings import api_settings

from elixirapp.html import is_htmx


def wants_json(request):
    return 'application/json' in request.headers.get('Accept', '')


def login_url(request):
    destination = request.get_full_path() if request.method in ('GET', 'HEAD') else reverse('html:account')
    # JSON status endpoints are not useful post-login destinations.
    if wants_json(request):
        destination = reverse('html:account')
    return reverse('html:login') + '?' + urlencode({'next': destination})


def authentication_required(request):
    url = login_url(request)
    if wants_json(request):
        response = JsonResponse({'error': {'code': 'authentication_required', 'loginUrl': url}}, status=401)
    elif is_htmx(request):
        response = HttpResponse(status=401)
        response['X-Login-URL'] = url
    else:
        response = redirect(url)
    response['Cache-Control'] = 'no-store'
    return response


def browser_login_required(view):
    @wraps(view)
    @never_cache
    def protected(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return authentication_required(request)
        return view(request, *args, **kwargs)
    protected.browser_session_required = True
    return protected


class BrowserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username or email', max_length=254,
                               widget=forms.TextInput(attrs={'autocomplete': 'username', 'autofocus': True}))

    def clean(self):
        identifier = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if identifier and password:
            # Reuse current API credential, active-user and verification policy, without issuing a token.
            serializer = api_settings.LOGIN_SERIALIZER(data={
                'email' if '@' in identifier else 'username': identifier, 'password': password,
            }, context={'request': self.request})
            if not serializer.is_valid():
                raise forms.ValidationError('Unable to sign in with these credentials.')
            self.user_cache = serializer.validated_data['user']
        return self.cleaned_data


class BrowserLoginView(LoginView):
    template_name = 'html/login.html'
    authentication_form = BrowserLoginForm

    def get_default_redirect_url(self):
        return reverse('html:account')


@never_cache
@require_POST
@browser_login_required
def logout(request):
    end_session(request)
    url = reverse('html:login')
    if is_htmx(request):
        response = HttpResponse(status=200)
        response['HX-Redirect'] = url
        return response
    return redirect(url)


@browser_login_required
@require_GET
def account(request):
    return render(request, 'html/account.html', {'session_config': {'endpoint': reverse('html:session-check')}})


@browser_login_required
@require_GET
def session(request):
    # An explicit recovery GET refreshes masked CSRF after sign-in in another tab.
    return JsonResponse({'csrfToken': get_token(request), 'userId': str(request.user.pk)})


@browser_login_required
@require_POST
def check(request):
    checked = timezone.now().isoformat()
    request.session['browser_last_verified'] = checked
    if wants_json(request):
        return JsonResponse({'checked': checked})
    return redirect('html:account')


def csrf_failure(request, reason=''):
    if not (request.META.get('biotools.html') or request.META.get('biotools.canonical')):
        return default_csrf_failure(request, reason=reason)
    protected = getattr(request.resolver_match.func, 'browser_session_required', False) if request.resolver_match else False
    if protected and not request.user.is_authenticated:
        return authentication_required(request)
    if wants_json(request):
        response = JsonResponse({'error': {'code': 'csrf_failed'}}, status=403)
    elif is_htmx(request):
        response = HttpResponse(status=403)
        response['X-CSRF-Failed'] = 'true'
    else:
        response = render(request, 'html/csrf-failure.html', status=403)
    response['Cache-Control'] = 'no-store'
    return response
