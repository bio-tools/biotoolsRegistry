# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0020_elixircommunity'),
    ]

    operations = [
        migrations.AddField(
            model_name='credit',
            name='rorid',
            field=models.TextField(null=True, blank=True),
        ),
    ]
