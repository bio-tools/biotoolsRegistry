"""Mirror Apache's explicit mounts when Caddy forwards to runserver."""
from elixirapp import html_wsgi, wsgi, canonical_wsgi


def application(environ, start_response):
    path = environ.get('PATH_INFO', '')
    for mount, app in (('/_migration/html', html_wsgi.application),
                       ('/api', wsgi.application)):
        if path == mount or path.startswith(mount + '/'):
            environ['SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '') + mount
            environ['PATH_INFO'] = path[len(mount):] or '/'
            return app(environ, start_response)
    return canonical_wsgi.application(environ, start_response)
