# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0025_auto_20200622_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='DomainTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(max_length=50, null=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='domain',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='domaintag',
            name='domain',
            field=models.ForeignKey(related_name='tag', blank=True, to='elixir.Domain', null=True),
        ),
        migrations.AddField(
            model_name='domaincollection',
            name='domain',
            field=models.ForeignKey(related_name='collection', blank=True, to='elixir.Domain', null=True),
        ),
    ]
