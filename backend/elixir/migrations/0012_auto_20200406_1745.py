# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0011_auto_20200118_1007'),
    ]

    operations = [
        migrations.CreateModel(
            name='BioLib',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_id', models.TextField(null=True)),
                ('author_name', models.TextField(null=True)),
                ('author_username', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('biolib', models.ForeignKey(to='elixir.BioLib', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='resource',
            name='community',
            field=models.ForeignKey(to='elixir.Community', null=True),
        ),
    ]
