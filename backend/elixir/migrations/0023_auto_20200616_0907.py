# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0022_credit_fundrefid'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='accessibility',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='accessibility',
            name='resource',
            field=models.ForeignKey(related_name='accessibility_old', blank=True, to='elixir.Resource', null=True),
        ),
    ]
