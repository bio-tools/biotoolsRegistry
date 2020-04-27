# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models

def copy_link_types(apps, schema_editor):
    Link = apps.get_model("elixir", "Link")
    LinkType = apps.get_model("elixir", "LinkType")


    link_rids_with_same_urls = []
        
    distinct_r_ids = [ r['resource_id'] for r in Link.objects.values('resource_id').distinct() ]
    for r_id in distinct_r_ids:
        distinct_links_rid_urls = [l['url'] for l in Link.objects.filter(resource_id=r_id).values('url').distinct()]
        non_distinct_links_rid_urls = [l['url'] for l in Link.objects.filter(resource_id=r_id).values('url')]
        
        if len(distinct_links_rid_urls) != len(non_distinct_links_rid_urls):
            link_rids_with_same_urls.append(r_id)



            
    for r_id in link_rids_with_same_urls:
        url_ids = dict()
        for link in Link.objects.filter(resource_id=r_id):
            if url_ids.get(link.url) == None:
                url_ids[link.url] = [link.id]
            else:
                url_ids[link.url].append(link.id)
        print("Creating LinkType objects")
        for k in url_ids.keys():
            # only keep the first from the list of Link ids since we will delete the others
            kept_link_id = url_ids[k][0]
            for l_id in url_ids[k]:
                l  = Link.objects.get(id=l_id)
                print("Created LinkType from:", l.id,l.url,l.type_old, l.resource_id)
                lt = LinkType()
                lt.type = l.type_old
                lt.additionDate = l.additionDate
                lt.link_id = kept_link_id
                lt.save()
            print("-------")
        
        
        
        print("Deleting duplicate Link objects")
        for k in url_ids.keys():
            kept_link = Link.objects.get(id=url_ids[k][0])
            if url_ids[k] > 1:
                for l_id in url_ids[k][1:]:
                    l_note = Link.objects.get(id=l_id).note
                    if l_note:
                        kept_link.note = kept_link.note + " " + l_note
                        print("note updated")
                    print("deleting Link with id:", l_id)
                    Link.objects.get(id=l_id).delete()
                    if kept_link.note:
                        print("saving link with new note:", kept_link.note)
                        kept_link.save()
                
        
        print("!!!!!!!!!!")
        
    print("Copying regular simple links...")
    for link in Link.objects.all():
        if(link.resource_id not in link_rids_with_same_urls):
            lt = LinkType()
            lt.type = l.type_old
            lt.additionDate = l.additionDate
            lt.link_id = link.id
            lt.save()
    print("Done")


class Migration(migrations.Migration):

    dependencies = [
        ('elixir', '0014_auto_20200426_1213'),
    ]

    operations = [
        migrations.RunPython(copy_link_types),
    ]
