"""Disposable workflow media and isolated administrator for management acceptance."""
import os
import struct
import zlib
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from elixir.models import Workflow, WorkflowAnnotation

if os.environ.get('BIOTOOLS_ALLOW_TEST_SEED') != 'biotools-refresh':
    raise RuntimeError('Explicit disposable-stack opt-in required.')
User = get_user_model()
User.objects.get_or_create(username='admin', defaults={'is_active': False})
admin, created = User.objects.get_or_create(username='migration-management-admin')
if created:
    admin.is_superuser = admin.is_staff = True
    admin.set_password('Migration-test-only-2026')
    admin.save()

if Workflow.objects.filter(biotoolsID='management-workflow').exists():
    print('Management workflow already exists; not overwriting it.')
else:
    width, height = 1000, 500
    # Deterministic diagram fixture: three blue boxes and a connecting line.
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            box = 100 <= y <= 300 and any(start <= x <= start + 200 for start in (100, 400, 700))
            line = 198 <= y <= 202 and 100 <= x <= 900
            row.extend((51, 122, 183) if box or line else (245, 248, 251))
        rows.append(b'\0' + row)
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b''.join(rows))) + chunk(b'IEND', b'')
    workflow = Workflow(biotoolsID='management-workflow', description='Fictional workflow for migration acceptance.', sourceURL='https://example.org/workflow')
    workflow.image.save('management-workflow.png', ContentFile(png), save=False)
    workflow.image_width, workflow.image_height = width, height
    workflow.save()
    for x, title in ((100, 'Read input'), (400, 'Align sequences'), (700, 'Write output')):
        WorkflowAnnotation.objects.create(workflow=workflow, startX=x, startY=100, endX=x+200, endY=300,
            title=title, description='Inspect ' + title.lower() + ' in this fictional workflow.',
            edam_term='Sequence alignment', edam_uri='http://edamontology.org/operation_2928')
    print('Created management-workflow and its image; existing records untouched.')
