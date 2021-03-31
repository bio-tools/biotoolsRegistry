# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0028_auto_20210316_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='visibility',
            field=models.IntegerField(default=1, choices=[(0, b'NO'), (1, b'YES')]),
        ),
    ]
