# -*- coding: utf-8 -*-
# Migrations to change Link type data
# 'Registry' becomes 'Software catalogue'

from __future__ import unicode_literals

from django.db import migrations, models

def change_registry_to_software_catalogue(apps, schema_editor):
    Link = apps.get_model("elixir", "Link")

    for link in Link.objects.all():
        if link.type == 'Registry':
            link.type = 'Software catalogue'
            link.save()


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0007_auto_20200118_0914'),
    ]

    operations = [
        migrations.RunPython(change_registry_to_software_catalogue),
    ]
