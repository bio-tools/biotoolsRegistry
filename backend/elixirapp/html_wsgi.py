"""Isolated browser entry point; the public API keeps its original URLconf."""
import sys

sys.path.insert(0, '/elixir/application/backend')

from elixirapp.wsgi import application as django_application


def application(environ, start_response):
    environ['biotools.html'] = True
    return django_application(environ, start_response)
