from django import forms
from django.contrib import messages
from django.http import HttpResponseServerError, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_headers
from django.conf import settings
from time import perf_counter
import logging
import re


RESERVED = {'404', 'about', 'community', 'communities', 'schema', 'stats', 'domains',
            'register', 'subdomain', 'domain-manager', 'edit-domain', 'edit-subdomain', 'login', 'signup', 'reset-password',
            'profile', 'requests', 'workflows', 'governance', 'events', 'mail', 'faq',
            'apidoc', 'changelog', 'helpdesk', 'projects', 'roadmap', 'api', 't', 'tool',
            'static', 'dist', 'img', 'css', 'js', 'fonts', 'components', 'partials',
            'bower_components', 'node_modules', 'index.html', 'robots.txt', 'favicon.ico', 'sitemap.xml',
            'auth', 'orcid'}


def canonical_family(path):
    if path == '/github-to-biotools':
        return 'bridge'
    if path == '/_edam/terms/':
        return 'edam'
    if re.fullmatch(r'/_workflow/(?:matches/|function/|compare/|shared/|designs/(?:[a-f0-9-]{36}/(?:share/)?)?)', path):
        return 'workflow-matches'
    if re.fullmatch(
            r'/(?:domain-manager/?|subdomain/?|edit-(?:domain|subdomain)(?:/[A-Za-z0-9-]{2,40})?/?|workflows(?:/design)?/?|[A-Za-z0-9.~_-]{1,100}/manage/?)', path):
        return 'management'
    from elixirapp.public_pages import PAGES
    if path == '/' or path.strip('/').split('/')[0] in PAGES:
        return 'public'
    if re.fullmatch(
            r'/(?:login/?|signup(?:/.*)?|reset-password(?:/.*)?|profile(?:/.*)?|auth/.*|orcid/callback/)', path):
        return 'accounts'
    if path.lstrip('/').split('/', 1)[0] in {'api', 'static', 'dist', 'img', 'css', 'js', 'fonts',
                            'components', 'partials', 'bower_components', 'node_modules'}:
        return None
    if re.fullmatch(
            r'/(?:register/?|register/(?:save|validate)/|[A-Za-z0-9.~_-]{1,100}/edit(?:/(?:save|validate)/|/?)|'
            r'requests/?|requests/conclude/|requests/tool/[A-Za-z0-9.~_-]{1,100}/)', path):
        return 'requests' if path.split('/')[1] == 'requests' else 'editor'
    if path in ('/t', '/t/', '/_search/data/', '/_search/options/'):
        return 'search'
    if path.strip('/') not in RESERVED and re.fullmatch(
            r'/(?:(?:tool|t)/)?(?:biotools:)?[A-Za-z0-9.~_-]{1,100}/?', path):
        return 'detail'
    if not re.fullmatch(r'/[A-Za-z0-9.~_-]{1,100}/?', path) and path.split('/')[1] not in {
            *RESERVED, 'media', '_migration', '_search', 'edit-domain', 'edit-subdomain', '.well-known'}:
        return 'public'
    return None


class HtmlRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only the HTML WSGI entry point sets this key; HTTP headers cannot set it.
        if request.META.get('biotools.canonical'):
            request.urlconf = 'elixirapp.canonical_accounts_editor_urls'
            family = canonical_family(request.path_info)
            if not family:
                return HttpResponseNotFound('Not found')
            request.canonical = True
            request.native_accounts = True
            start = perf_counter()
            response = self.get_response(request)
            elapsed = (perf_counter() - start) * 1000
            response['X-Biotools-Route'] = 'django-' + family
            response['Cache-Control'] = 'private, no-store'
            if family == 'accounts':
                response['Referrer-Policy'] = 'same-origin'
            indexable = family == 'detail' or (family == 'public' and request.path.strip('/') in {'', 'about', 'community', 'communities', 'stats'})
            response['X-Robots-Tag'] = 'index, follow' if indexable and response.status_code < 400 else 'noindex, follow'
            response['Server-Timing'] = ', '.join(filter(None, [response.get('Server-Timing'), f'route;dur={elapsed:.2f}']))
            logging.getLogger('biotools.routes').info('route=%s method=%s status=%s duration_ms=%.2f',
                                                    family, request.method, response.status_code, elapsed)
            return response
        elif request.META.get('biotools.html'):
            if not settings.MIGRATION_PREVIEW_DEMOS and request.path_info.rstrip('/') in ('', '/preview', '/islands', '/edam'):
                return HttpResponseNotFound('Not found')
            request.urlconf = 'elixirapp.html_urls'
        return self.get_response(request)


@require_http_methods(['GET', 'HEAD', 'POST'])
def index(request):
    if request.method == 'POST':
        messages.success(request, 'Session check complete.')
        return redirect('html:index')
    return render(request, 'html/index.html')


def is_htmx(request):
    return (request.headers.get('HX-Request') == 'true'
            and request.headers.get('HX-History-Restore-Request') != 'true')


class MessagePreviewForm(forms.Form):
    message = forms.CharField(max_length=120, initial='Welcome to bio.tools.')


@require_http_methods(['GET', 'HEAD'])
@vary_on_headers('HX-Request', 'HX-History-Restore-Request')
def preview(request):
    form = MessagePreviewForm(request.GET if 'message' in request.GET else None)
    valid = not form.is_bound or form.is_valid()
    message = form.cleaned_data['message'] if form.is_bound and valid else form['message'].initial
    template = 'html/fragments/preview.html' if is_htmx(request) else 'html/preview.html'
    return render(request, template, {'form': form, 'preview_message': message},
                  status=200 if valid else 400)


@require_http_methods(['GET', 'HEAD'])
@vary_on_headers('HX-Request', 'HX-History-Restore-Request')
def islands(request):
    template = 'html/fragments/islands.html' if is_htmx(request) else 'html/islands.html'
    return render(request, template, {
        'first_counter': {'label': 'First counter', 'initial': 3},
        'second_counter': {'label': 'Second counter', 'initial': 7},
    })


def page_not_found(request, exception):
    return render(request, 'html/404.html', status=404)


def server_error(request):
    # A broken database/session must not break the error page's context processors.
    return HttpResponseServerError(render_to_string('html/500.html'))
