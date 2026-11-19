from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('elixir', '0009_resource_identifier')]
    operations = [migrations.AlterField(
        model_name='resourceidentifier', name='identifier',
        field=models.CharField(max_length=100, primary_key=True, serialize=False, db_collation='utf8mb4_unicode_ci'),
    )]
