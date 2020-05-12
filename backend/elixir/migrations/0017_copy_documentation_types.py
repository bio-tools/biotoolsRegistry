# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models

def copy_documentation_types(apps, schema_editor):
    Documentation = apps.get_model("elixir", "Documentation")
    DocumentationType = apps.get_model("elixir", "DocumentationType")

    print('Starting')

    documentation_rids_with_same_urls = []

    distinct_r_ids = [ r['resource_id'] for r in Documentation.objects.values('resource_id').distinct() ]

    for r_id in distinct_r_ids:
        distinct_documentations_rid_urls = [l['url'] for l in Documentation.objects.filter(resource_id=r_id).values('url').distinct()]
        non_distinct_documentations_rid_urls = [l['url'] for l in Documentation.objects.filter(resource_id=r_id).values('url')]
        
        if len(distinct_documentations_rid_urls) != len(non_distinct_documentations_rid_urls):
            documentation_rids_with_same_urls.append(r_id)



            
    for r_id in documentation_rids_with_same_urls:
        url_ids = dict()
        for documentation in Documentation.objects.filter(resource_id=r_id):
            if url_ids.get(documentation.url) == None:
                url_ids[documentation.url] = [documentation.id]
            else:
                url_ids[documentation.url].append(documentation.id)
        print("Creating DocumentationType objects")
        for k in url_ids.keys():
            # only keep the first from the list of Documentation ids since we will delete the others
            kept_documentation_id = url_ids[k][0]
            for d_id in url_ids[k]:
                d = Documentation.objects.get(id=d_id)
                print("Created DocumentationType from:", d.id,d.url,d.type_old, d.resource_id)
                dt = DocumentationType()
                dt.type = d.type_old
                dt.additionDate = d.additionDate
                dt.documentation_id = kept_documentation_id
                dt.save()
            print("-------")
        
        
        
        print("Deleting duplicate Documentation objects")
        for k in url_ids.keys():
            kept_documentation = Documentation.objects.get(id=url_ids[k][0])
            if url_ids[k] > 1:
                for d_id in url_ids[k][1:]:
                    d_note = Documentation.objects.get(id=d_id).note
                    if d_note:
                        kept_documentation.note = kept_documentation.note + " " + d_note
                        print("note updated")
                    print("deleting Documentation with id:", d_id)
                    Documentation.objects.get(id=d_id).delete()
                    if kept_documentation.note:
                        print("saving documentation with new note:", kept_documentation.note)
                        kept_documentation.save()
                
        
        print("!!!!!!!!!!")
        
    print("Copying regular simple documentations...")
    for d in Documentation.objects.all():
        if(d.resource_id not in documentation_rids_with_same_urls):
            dt = DocumentationType()
            dt.type = d.type_old
            dt.additionDate = d.additionDate
            dt.documentation_id = d.id
            dt.save()
    print("Done")

class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0016_auto_20200512_0806'),
    ]

    operations = [
        migrations.RunPython(copy_documentation_types),
    ]
