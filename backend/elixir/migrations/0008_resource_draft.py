import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('elixir', '0007_workflow_design'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [migrations.CreateModel(name='ResourceDraft', fields=[
        ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
        ('target', models.CharField(blank=True, default='', max_length=100)),
        ('record_revision', models.CharField(blank=True, default='', max_length=64)),
        ('resource', models.JSONField()),
        ('revision', models.UUIDField(default=uuid.uuid4, editable=False)),
        ('created', models.DateTimeField(auto_now_add=True)),
        ('updated', models.DateTimeField(auto_now=True)),
        ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_drafts', to=settings.AUTH_USER_MODEL)),
    ])]
