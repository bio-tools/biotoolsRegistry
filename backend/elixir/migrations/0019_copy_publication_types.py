# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models

def copy_publication_types(apps, schema_editor):
    Publication = apps.get_model("elixir", "Publication")
    PublicationType = apps.get_model("elixir", "PublicationType")

    print(" Working on publication types ...")
    for p in Publication.objects.all():
        if p.type_old:
            pt = PublicationType()
            pt.type = p.type_old
            pt.additionDate = p.additionDate
            pt.publication_id = p.id
            pt.save()
    print("Done")


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0018_auto_20200512_1024'),
    ]

    operations = [
        migrations.RunPython(copy_publication_types),
    ]
