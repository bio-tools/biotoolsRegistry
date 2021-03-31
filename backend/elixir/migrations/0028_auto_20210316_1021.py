# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0027_domaincollection_additiondate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domainresource',
            name='domain',
            field=models.ForeignKey(related_name='resource', to='elixir.Domain'),
        ),
    ]
