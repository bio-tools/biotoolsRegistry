# -*- coding: utf-8 -*-
# Migrations to change Downloads type data
# 'CWL file' becomes 'Tool wrapper (CWL)'
# upercase Galaxy , Taverna and Other for the rest of the available tool wrappers
# Replace in the data values, 'Binary package' and 'Source package' with 'Software package'	
#   note here that there might be tools which have both binary package
#   and source package and we only want one instance of software package
#   it's not a big deal if it's twice but keep in mind
from __future__ import unicode_literals

from django.db import migrations, models

# do all in one function to limit number of reads and saves
def change_downloads(apps, schema_editor):
    Download = apps.get_model("elixir", "Download")

    for download in Download.objects.all():
        changed = False
        if download.type == 'CWL file':
            download.type = 'Tool wrapper (CWL)'
            changed = True
        
        if download.type == 'Tool wrapper (galaxy)':
            download.type = 'Tool wrapper (Galaxy)'
            changed = True
        
        if download.type == 'Tool wrapper (taverna)':
            download.type = 'Tool wrapper (Taverna)'
            changed = True

        if download.type == 'Tool wrapper (other)':
            download.type = 'Tool wrapper (Other)'
            changed = True
        
        if download.type == 'Binary package' or download.type == 'Source package':
            download.type = 'Software package'
            changed = True
        
        if changed:
            download.save()

class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0005_auto_20200118_0800'),
    ]

    operations = [
        migrations.RunPython(change_downloads),
    ]
