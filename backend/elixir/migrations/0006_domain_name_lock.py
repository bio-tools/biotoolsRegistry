from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('elixir', '0005_statsdata_tooltypecounts')]

    operations = [
        migrations.CreateModel(
            name='DomainNameLock',
            fields=[('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                    ('name', models.CharField(max_length=50, unique=True))],
        ),
    ]
