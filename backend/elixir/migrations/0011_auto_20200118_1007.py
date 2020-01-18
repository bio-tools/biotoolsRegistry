# -*- coding: utf-8 -*-
# accessibility / license
#	-> remove 'Freeware', 'Proprietary' from accessibility
#	-> if the tool has 'Freeware' acc and no license then License becomes 'Freeware'
#	-> if the tool has 'Proprietary' acc and no license then License becomes 'Proprietary'
# note that if a tool has both Freeware and Proprietary acc 
# then the license becomes the last one it encounters
# but this is wrong data anyway, so should be fine

from __future__ import unicode_literals

from django.db import migrations, models

def change_accessibility_and_license(apps, schema_editor):
    Accessibility = apps.get_model("elixir", "Accessibility")
    Resource = apps.get_model("elixir", "Resource")

    for accessibility in Accessibility.objects.all():

        if accessibility.name == 'Proprietary' or accessibility.name == 'Freeware':
            r = None

            # get resource (use filter to avoid errors)
            r_set = Resource.objects.filter(id=accessibility.resource_id, visibility=1)

            # if resource is in bio.tools
            if len(r_set) == 1:
                r = r_set[0]
                # if there is no license then set the license to 'Freeware' or 'Proprietary'
                if r.license == None or r.license == '':
                    r.license = accessibility.name
                    r.save()
            
            # delete accessibility
            accessibility.delete()
        



class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0010_auto_20200118_0954'),
    ]

    operations = [
        migrations.RunPython(change_accessibility_and_license),
    ]
