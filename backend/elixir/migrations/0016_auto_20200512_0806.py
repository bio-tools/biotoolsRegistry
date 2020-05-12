# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0015_copy_link_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RenameField(
            model_name='documentation',
            old_name='type',
            new_name='type_old',
        ),
        migrations.AddField(
            model_name='documentationtype',
            name='documentation',
            field=models.ForeignKey(related_name='type', blank=True, to='elixir.Documentation', null=True),
        ),
    ]
