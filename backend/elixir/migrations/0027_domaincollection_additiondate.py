# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0026_auto_20210310_0705'),
    ]

    operations = [
        migrations.AddField(
            model_name='domaincollection',
            name='additionDate',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
