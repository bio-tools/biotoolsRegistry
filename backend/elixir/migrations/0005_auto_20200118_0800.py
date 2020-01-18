# -*- coding: utf-8 -*-
# Change data for license value of 'Unlicensed' to 'Not licensed'
from __future__ import unicode_literals

from django.db import migrations, models

def change_unlicensed_to_not_licensed(apps, schema_editor):
    Resource = apps.get_model("elixir", "Resource")

    for resource in Resource.objects.all():
        if resource.license == 'Unlicensed':
            resource.license = 'Not licensed'
            resource.save()

class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0004_credit_gridid'),
    ]

    operations = [
        migrations.RunPython(change_unlicensed_to_not_licensed),
    ]
