from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [('elixir', '0010_resource_identifier_collation')]

    operations = [
        migrations.AddField(model_name='resourcerequest', name='relationship', field=models.CharField(blank=True, default='', max_length=200)),
        migrations.AddField(model_name='resourcerequest', name='reason', field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='resourcerequest', name='supporting_url', field=models.URLField(blank=True, default='', max_length=500)),
        migrations.AddField(model_name='resourcerequest', name='created_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AlterField(model_name='resourcerequest', name='created_at', field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
        migrations.AddField(model_name='resourcerequest', name='withdrawn', field=models.BooleanField(default=False)),
    ]
