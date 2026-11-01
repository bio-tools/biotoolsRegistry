"""Session transport for browser requests; /api stays token-only."""
from django.contrib.auth import logout
from django.http import Http404, JsonResponse
from django.urls import resolve, get_urlconf, set_urlconf, get_script_prefix, set_script_prefix
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView


@never_cache
@ensure_csrf_cookie
@require_GET
def configuration(request):
    return JsonResponse({'enabled': True, 'accountsEnabled': True})


class SessionLogin:
    def login(self):
        self.user = self.serializer.validated_data['user']
        self.process_login()

    def get_response(self):
        return Response({'detail': 'Signed in.'})


class SessionLogout(LogoutView):
    def logout(self, request):
        logout(request)
        return Response({'detail': 'Signed out.'})


class SessionRegistration(RegisterView):
    token_model = None

    def get_response_data(self, user):
        return super().get_response_data(user) or {'detail': 'Account registered.'}


@never_cache
def dispatch(request, api_path):
    # This outer Django view is deliberately NOT csrf_exempt, including login,
    # signup and recovery. Inner DRF views retain their original permissions.
    if request.headers.get('Authorization'):
        return JsonResponse({'detail': 'Use the browser session, not an API token.'}, status=400)
    match = resolve('/' + api_path, urlconf='elixirapp.urls')
    cls = getattr(match.func, 'view_class', None)
    if cls is None or not issubclass(cls, APIView):
        raise Http404
    if issubclass(cls, LoginView):
        cls = type('Browser' + cls.__name__, (SessionLogin, cls), {})
    elif issubclass(cls, LogoutView):
        cls = SessionLogout
    elif issubclass(cls, RegisterView):
        cls = SessionRegistration
    # Account emails must still link to the public verification/recovery routes.
    previous_urlconf, previous_prefix = get_urlconf(), get_script_prefix()
    try:
        set_urlconf('elixirapp.urls')
        set_script_prefix('/api/')
        return cls.as_view(**{**match.func.view_initkwargs, 'authentication_classes': (SessionAuthentication,)})(
            request, *match.args, **match.kwargs)
    finally:
        set_urlconf(previous_urlconf)
        set_script_prefix(previous_prefix)
