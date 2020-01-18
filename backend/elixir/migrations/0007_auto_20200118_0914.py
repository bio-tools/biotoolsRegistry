# -*- coding: utf-8 -*-
# Migrations to change Documentation type data
# 'Tutorial' becomes 'Training material'
# if a tool had both tutorial and training material then the data change would have training material twice, keep in mind.

from __future__ import unicode_literals

from django.db import migrations, models

def change_tutorial_to_training_material(apps, schema_editor):
    Documentation = apps.get_model("elixir", "Documentation")

    for documentation in Documentation.objects.all():
        if documentation.type == 'Tutorial':
            documentation.type = 'Training material'
            
            if documentation.note == None or documentation.note == '':
                documentation.note = 'Tutorial material'
            else:
                documentation.note += '; Tutorial'

            documentation.save()

class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0006_auto_20200118_0831'),
    ]

    operations = [
        migrations.RunPython(change_tutorial_to_training_material),
    ]
