"""Dedicated users keep provider rate limits exercised without slowing the suite."""
import os
from django.contrib.auth import get_user_model

if os.environ.get('BIOTOOLS_ALLOW_TEST_SEED') != 'biotools-refresh':
    raise RuntimeError('Only seed the disposable migration stack.')
for width in (1440, 390, 'failure'):
    user, _ = get_user_model().objects.get_or_create(username='migration-bridge-' + str(width))
    user.set_password('Migration-test-only-2026')
    user.save()
print('Disposable bridge users ready.')
