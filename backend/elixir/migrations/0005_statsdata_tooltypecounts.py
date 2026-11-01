from django.db import migrations
from jsonfield import JSONField


class Migration(migrations.Migration):
    dependencies = [('elixir', '0004_domain_editors')]

    operations = [
        migrations.AddField(
            model_name='statsdata', name='toolTypeCounts',
            field=JSONField(null=True, blank=True),
        ),
    ]
