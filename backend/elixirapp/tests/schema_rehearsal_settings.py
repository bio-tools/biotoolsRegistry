"""Opt-in settings for the disposable two-proxy schema rehearsal only."""
import re
from pathlib import Path

from elixirapp.settings import *  # noqa: F403

if os.environ.get('BIOTOOLS_SCHEMA_REHEARSAL') != 'biotools-refresh':
    raise RuntimeError('Schema rehearsal requires explicit disposable-stack opt-in.')
if not re.fullmatch(r'test_schema_ui_[a-f0-9]{8}', DATABASES['default']['NAME']):
    raise RuntimeError('Schema rehearsal must use its own test database.')

SCHEMA_REHEARSAL_DIRECTORY = Path('/schema-rehearsal')
SCHEMA_REHEARSAL_PHASE = (SCHEMA_REHEARSAL_DIRECTORY / 'active').read_text().strip()
if SCHEMA_REHEARSAL_PHASE not in {'baseline', 'added', 'removed'}:
    raise RuntimeError('Unknown schema rehearsal phase.')
RESOURCE_SCHEMA_PATH = str(SCHEMA_REHEARSAL_DIRECTORY / (SCHEMA_REHEARSAL_PHASE + '.xsd'))
RESOURCE_SCHEMA_VERSION = 'rehearsal-' + SCHEMA_REHEARSAL_PHASE
RESOURCE_UI_POLICY_PATH = str(SCHEMA_REHEARSAL_DIRECTORY / (SCHEMA_REHEARSAL_PHASE + '-policy.json'))
RESOURCE_UI_DESCRIPTOR_PATH = str(SCHEMA_REHEARSAL_DIRECTORY / (SCHEMA_REHEARSAL_PHASE + '.json'))
ELASTIC_SEARCH_INDEX = DATABASES['default']['NAME']
INSTALLED_APPS += ('elixirapp.tests.schema_rehearsal.FixtureConfig',)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
