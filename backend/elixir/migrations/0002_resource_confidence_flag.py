# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='confidence_flag',
            field=models.TextField(null=True, blank=True),
        ),
    ]
