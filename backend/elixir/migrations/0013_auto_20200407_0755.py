# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0012_auto_20200406_1745'),
    ]

    operations = [
        migrations.RenameField(
            model_name='biolib',
            old_name='app_id',
            new_name='app_name',
        ),
    ]
