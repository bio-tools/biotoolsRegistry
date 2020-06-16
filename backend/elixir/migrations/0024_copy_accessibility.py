# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models

def copy_accessibility_to_resource(apps, schema_editor):
    Accessibility = apps.get_model("elixir", "Accessibility")
    Resource = apps.get_model("elixir", "Resource")

    print('\nStarting...\n')

    for a in Accessibility.objects.all():
        r = Resource.objects.get(id=a.resource_id)
        r.accessibility = a.name
        r.save()

    print('\nDone.\n')

def clear_resource_of_accessibility(apps, schema_editor):
    Resource = apps.get_model("elixir", "Resource")

    print('\nStarting...\n')

    for r in Resource.objects.all():
        r.accessibility = None
        r.save()


    print('\nDone.\n')

class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0023_auto_20200616_0907'),
    ]

    operations = [
        migrations.RunPython(copy_accessibility_to_resource,clear_resource_of_accessibility),
    ]
