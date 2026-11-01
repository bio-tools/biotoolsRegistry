"""Root browser entry point selected by the proxy, never by HTTP headers."""
import sys
from urllib.parse import unquote, urlsplit

sys.path.insert(0, '/elixir/application/backend')
from elixirapp.wsgi import application as django_application


def application(environ, start_response):
    # Apache's file rewrite changes SCRIPT_NAME; REQUEST_URI retains the public URL.
    if environ.get('REQUEST_URI'):
        environ['PATH_INFO'] = unquote(urlsplit(environ['REQUEST_URI']).path)
    environ['SCRIPT_NAME'] = ''
    environ['biotools.canonical'] = True
    return django_application(environ, start_response)
