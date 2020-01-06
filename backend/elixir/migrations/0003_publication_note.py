# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0002_resource_confidence_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='note',
            field=models.TextField(null=True, blank=True),
        ),
    ]
