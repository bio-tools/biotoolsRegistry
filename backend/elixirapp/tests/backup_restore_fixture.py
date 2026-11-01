"""Seed or verify only the disposable backup rehearsal database."""
import os
import uuid

from django.contrib.auth.models import User
from django.db import connection

from elixir.models import Data, Domain, DomainNameLock, EditPermission, Format, Function, Input, Operation, Resource, WorkflowDesign


mode = os.environ.get('BIOTOOLS_BACKUP_FIXTURE')
expected_database = {'seed': 'backup_source', 'verify': 'backup_restored'}.get(mode)
if (os.environ.get('BIOTOOLS_BACKUP_REHEARSAL') != 'isolated' or not expected_database or
        connection.settings_dict['HOST'] != 'backup-mysql' or connection.settings_dict['NAME'] != expected_database):
    raise RuntimeError('Backup fixture may only run on the isolated rehearsal database.')

draft_id = uuid.UUID('1ecf7259-a09e-4f45-bf71-3bbb7047d453')
revision = uuid.UUID('71332ce1-0524-4b07-bf75-16d02fe5e183')
graph = {'version': 1, 'steps': [], 'connections': []}
if mode == 'seed':
    owner = User.objects.create_user('backup-rehearsal-owner')
    permission = EditPermission.objects.create(type='private')
    resource = Resource.objects.create(biotoolsID='backup-rehearsal', biotoolsCURIE='biotools:backup-rehearsal',
        name='Backup rehearsal', homepage='https://example.invalid/', description='Disposable backup fixture.',
        owner=owner, editPermission=permission)
    function = Function.objects.create(resource=resource)
    Operation.objects.create(function=function, uri='http://edamontology.org/operation_0292')
    item = Input.objects.create(function=function, data=Data.objects.create(uri='http://edamontology.org/data_0863'))
    Format.objects.create(input=item, uri='http://edamontology.org/format_1929')
    DomainNameLock.objects.create(name='backup-rehearsal')
    domain = Domain.objects.create(name='backup-rehearsal', title='Backup domain', owner=owner)
    domain.editors.add(owner)
    WorkflowDesign.objects.create(id=draft_id, owner=owner, title='Backup draft', graph=graph,
                                  revision=revision, share_digest='a' * 64)
else:
    owner = User.objects.get(username='backup-rehearsal-owner')
    resource = Resource.objects.get(biotoolsID='backup-rehearsal', owner=owner)
    assert resource.function.get().operation.get().uri == 'http://edamontology.org/operation_0292'
    item = resource.function.get().input.get()
    assert item.data.uri == 'http://edamontology.org/data_0863'
    assert item.format.get().uri == 'http://edamontology.org/format_1929'
    assert DomainNameLock.objects.filter(name='backup-rehearsal').exists()
    assert Domain.objects.get(name='backup-rehearsal').editors.filter(pk=owner.pk).exists()
    draft = WorkflowDesign.objects.get(pk=draft_id, owner=owner)
    assert draft.graph == graph and draft.revision == revision and draft.share_digest == 'a' * 64
    assert connection.introspection.table_names()
print('Backup fixture ' + mode + ' passed.')
