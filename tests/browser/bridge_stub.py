"""Deterministic provider for the disposable bridge rehearsal, never production."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

if os.environ.get('BIOTOOLS_ALLOW_TEST_SEED') != 'biotools-refresh':
    raise SystemExit('Only run this provider in the disposable migration stack.')


class Provider(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', '0'))))
        if body.get('repo') == 'failure':
            self.send_error(503)
            return
        content = json.dumps(json.dumps({'name': 'GitHub suggested tool',
            'description': 'Metadata suggested by the deterministic GitHub bridge rehearsal.',
            'license': '3D-Slicer-1.0', 'version': ['bridge-1.0'],
            'owner': 'must-not-be-applied', 'biotoolsID': 'must-not-be-applied',
            'function': [{'operation': [{'uri': 'http://edamontology.org/operation_2422', 'term': 'Data retrieval'}], 'note': 'Repository annotation'}]})).encode()
        self.send_response(201)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)


ThreadingHTTPServer(('0.0.0.0', 8000), Provider).serve_forever()
