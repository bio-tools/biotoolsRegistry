from django.db import migrations, models
from django.db.models.functions import Lower


def reserve_existing_identifiers(apps, schema_editor):
    Resource = apps.get_model('elixir', 'Resource')
    ResourceIdentifier = apps.get_model('elixir', 'ResourceIdentifier')
    database = schema_editor.connection.alias
    identifiers = (Resource.objects.using(database).order_by()
                   .annotate(normalized=Lower('biotoolsID'))
                   .values_list('normalized', flat=True).distinct().iterator(chunk_size=2000))
    batch = []
    for identifier in identifiers:
        batch.append(ResourceIdentifier(identifier=identifier))
        if len(batch) == 2000:
            ResourceIdentifier.objects.using(database).bulk_create(batch)
            batch.clear()
    if batch:
        ResourceIdentifier.objects.using(database).bulk_create(batch)


class Migration(migrations.Migration):
    dependencies = [('elixir', '0008_resource_draft')]
    operations = [
        migrations.CreateModel(name='ResourceIdentifier', fields=[
            ('identifier', models.CharField(max_length=100, primary_key=True, serialize=False)),
        ]),
        migrations.RunPython(reserve_existing_identifiers, migrations.RunPython.noop),
    ]
