# -*- coding: utf-8 -*-
# Migrations to change Documentation type data
# 'Manual' becomes 'User manual'

from __future__ import unicode_literals

from django.db import migrations, models

def change_manual_to_user_manual(apps, schema_editor):
    Documentation = apps.get_model("elixir", "Documentation")

    for documentation in Documentation.objects.all():
        if documentation.type == 'Manual':
            documentation.type = 'User manual'
            documentation.save()

class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0009_auto_20200118_0948'),
    ]

    operations = [
        migrations.RunPython(change_manual_to_user_manual),
    ]
