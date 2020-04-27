# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0013_auto_20200407_0755'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RenameField(
            model_name='link',
            old_name='type',
            new_name='type_old',
        ),
        migrations.AddField(
            model_name='linktype',
            name='link',
            field=models.ForeignKey(related_name='type', blank=True, to='elixir.Link', null=True),
        ),
    ]
