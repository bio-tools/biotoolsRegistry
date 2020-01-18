# -*- coding: utf-8 -*-
# Migrations to change Publication type data
# 'Comparison' becomes 'Benchmarking study'

from __future__ import unicode_literals

from django.db import migrations, models

def change_comparison_to_benchmarking_study(apps, schema_editor):
    Publication = apps.get_model("elixir", "Publication")

    for publication in Publication.objects.all():
        if publication.type == 'Comparison':
            publication.type = 'Benchmarking study'
            publication.save()

class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0008_auto_20200118_0937'),
    ]

    operations = [
        migrations.RunPython(change_comparison_to_benchmarking_study),
    ]
