# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0019_copy_publication_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElixirCommunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('elixirCommunity', models.TextField(null=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('resource', models.ForeignKey(related_name='elixirCommunity', blank=True, to='elixir.Resource', null=True)),
            ],
        ),
    ]
