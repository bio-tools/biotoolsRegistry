# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0017_copy_documentation_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RenameField(
            model_name='publication',
            old_name='type',
            new_name='type_old',
        ),
        migrations.AddField(
            model_name='publicationtype',
            name='publication',
            field=models.ForeignKey(related_name='type', blank=True, to='elixir.Publication', null=True),
        ),
    ]
