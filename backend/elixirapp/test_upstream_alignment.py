from unittest.mock import patch
from io import BytesIO
import json
import os
import subprocess
import sys

from django.core.exceptions import DisallowedHost
from django.test import RequestFactory, SimpleTestCase, override_settings

from elixir.resource_options import METADATA_CHOICES
from elixir.resource_ui import resource_descriptor
from elixir.serializers import ResourceSerializer
from elixir.parsers import XMLSchemaParser
from elixir.renderers import XMLSchemaRenderer
from elixir.view.resource import payload_fingerprint
from elixirapp.settings import getenv, proxy_ssl_header, string_list


class UpstreamAlignmentTests(SimpleTestCase):
    def test_security_configuration_parses_and_rejects_malformed_values(self):
        self.assertEqual(string_list('["bio.tools", "www.bio.tools"]'), ['bio.tools', 'www.bio.tools'])
        self.assertEqual(proxy_ssl_header('["HTTP_X_FORWARDED_PROTO", "https"]'), ('HTTP_X_FORWARDED_PROTO', 'https'))
        for invalid in ('"bio.tools"', '["", "host"]', '[1]'):
            with self.assertRaises(ValueError):
                string_list(invalid)
        for invalid in ('[]', '["HTTP_X_FORWARDED_PROTO"]', '["X_FORWARDED_PROTO", "https"]'):
            with self.assertRaises(ValueError):
                proxy_ssl_header(invalid)

    def test_security_settings_can_be_selected_by_environment(self):
        env = {**os.environ, 'BIOTOOLS_ALLOWED_HOSTS': '["registry.example"]',
               'BIOTOOLS_SESSION_COOKIE_SECURE': '1', 'BIOTOOLS_CSRF_COOKIE_SECURE': 'true',
               'BIOTOOLS_SECURE_PROXY_SSL_HEADER': '["HTTP_X_FORWARDED_PROTO", "https"]',
               'BIOTOOLS_EMAIL_USE_SSL': '0', 'BIOTOOLS_EMAIL_USE_TLS': '1',
               'BIOTOOLS_EMAIL_HOST_PASSWORD': 'test-only-mail-password'}
        command = 'import json; from elixirapp import settings; print(json.dumps([settings.ALLOWED_HOSTS, settings.SESSION_COOKIE_SECURE, settings.CSRF_COOKIE_SECURE, settings.SECURE_PROXY_SSL_HEADER, settings.EMAIL_USE_SSL, settings.EMAIL_USE_TLS, bool(settings.EMAIL_HOST_PASSWORD)]))'
        result = subprocess.run([sys.executable, '-c', command], env=env, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout.splitlines()[-1]), [['registry.example'], True, True, ['HTTP_X_FORWARDED_PROTO', 'https'], False, True, True])

    @override_settings(ALLOWED_HOSTS=['registry.example'], CSRF_COOKIE_SECURE=True,
                       SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
    def test_configured_host_proxy_and_csrf_cookie_behavior(self):
        request = RequestFactory().get('/', HTTP_HOST='registry.example', HTTP_X_FORWARDED_PROTO='https')
        self.assertEqual(request.get_host(), 'registry.example')
        self.assertTrue(request.is_secure())
        with self.assertRaises(DisallowedHost):
            RequestFactory().get('/', HTTP_HOST='attacker.example').get_host()
        response = self.client.get('/browser-session/', HTTP_HOST='registry.example')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.cookies['csrftoken']['secure'])

    def test_environment_booleans(self):
        for value in ('true', 'True', '1', 'yes', ' ON '):
            with patch.dict('os.environ', BIOTOOLS_TEST_FLAG=value):
                self.assertIs(getenv('TEST_FLAG', False, bool), True)
        for value in ('false', 'False', '0', 'no', 'off', ''):
            with patch.dict('os.environ', BIOTOOLS_TEST_FLAG=value):
                self.assertIs(getenv('TEST_FLAG', True, bool), False)
        with patch.dict('os.environ', BIOTOOLS_TEST_FLAG='mistyped'):
            with self.assertRaises(ValueError):
                getenv('TEST_FLAG', False, bool)

    def test_reviewed_vocabularies_reach_shared_contract_and_validators(self):
        fields = resource_descriptor()['contract']['fields']
        self.assertEqual(len(METADATA_CHOICES['license']), 725)
        for value in ('3D-Slicer-1.0', 'GPL-3.0', 'Freeware', 'Proprietary', 'Other', 'Not licensed'):
            self.assertEqual(ResourceSerializer().validate_license(value), value)
            self.assertIn(value, [choice['value'] for choice in fields['license']['choices']])
        for value in ('Cancer Data', 'Food and Nutrition', 'Microbiome', 'Research Data Management', 'Single-cell Omics', 'Toxicology'):
            self.assertIn(value, METADATA_CHOICES['elixirCommunity'])
        self.assertTrue({'Android', 'iOS'} <= set(METADATA_CHOICES['operatingSystem']))

    def test_save_fingerprint_preserves_order_duplicates_and_validation_state(self):
        first = {'function': [{'note': 'first'}, {'note': 'second'}]}
        self.assertNotEqual(payload_fingerprint(first, 0), payload_fingerprint({'function': list(reversed(first['function']))}, 0))
        self.assertNotEqual(payload_fingerprint(first, 0), payload_fingerprint({'function': first['function'] * 2}, 0))
        self.assertNotEqual(payload_fingerprint(first, 0), payload_fingerprint(first, 1))
        self.assertEqual(payload_fingerprint({'name': 'Name', 'homepage': 'URL'}, 0),
                         payload_fingerprint({'homepage': 'URL', 'name': 'Name'}, 0))

    def test_new_vocabularies_round_trip_through_xml(self):
        value = {'biotoolsID': 'vocabulary-fixture', 'name': 'Vocabulary fixture',
                 'description': 'A tool for checking the reviewed vocabulary.', 'homepage': 'https://example.org',
                 'license': '3D-Slicer-1.0', 'elixirCommunity': ['Cancer Data', 'Toxicology']}
        parsed = XMLSchemaParser().parse(BytesIO(XMLSchemaRenderer().render(value)))
        self.assertEqual(parsed['license'], value['license'])
        self.assertEqual(parsed['elixirCommunity'], value['elixirCommunity'])
