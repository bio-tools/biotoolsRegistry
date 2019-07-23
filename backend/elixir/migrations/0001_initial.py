# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Accessibility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CollectionID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.TextField(null=True, blank=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('tel', models.TextField(null=True, blank=True)),
                ('url', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('email', models.TextField(null=True, blank=True)),
                ('url', models.TextField(null=True, blank=True)),
                ('orcidid', models.TextField(null=True, blank=True)),
                ('typeEntity', models.TextField(null=True, blank=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CreditTypeRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typeRole', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('credit', models.ForeignKey(related_name='typeRole', blank=True, to='elixir.Credit', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.TextField(null=True, blank=True)),
                ('term', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Documentation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField()),
                ('type', models.TextField()),
                ('note', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32)),
                ('title', models.TextField(null=True, blank=True)),
                ('sub_title', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DomainResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('version', models.TextField(null=True, blank=True)),
                ('biotoolsID', models.TextField()),
                ('versionId', models.TextField()),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('domain', models.ForeignKey(to='elixir.Domain')),
            ],
        ),
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField()),
                ('type', models.TextField()),
                ('note', models.TextField(null=True, blank=True)),
                ('version', models.TextField(null=True, blank=True)),
                ('cmd', models.TextField(max_length=100, null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EditPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.TextField(default=b'private')),
            ],
        ),
        migrations.CreateModel(
            name='EditPermissionAuthor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('editPermissions', models.ManyToManyField(related_name='authors', to='elixir.EditPermission')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ElixirInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.TextField(null=True, blank=True)),
                ('node', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ElixirNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('elixirNode', models.TextField(null=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ElixirPlatform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('elixirPlatform', models.TextField(null=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.TextField(null=True, blank=True)),
                ('term', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Function',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('cmd', models.TextField(max_length=100, null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Input',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('data', models.ForeignKey(to='elixir.Data', null=True)),
                ('function', models.ForeignKey(related_name='input', blank=True, to='elixir.Function', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_name', models.TextField(null=True, blank=True)),
                ('field_value', models.TextField(null=True, blank=True)),
                ('resource_biotoolsID', models.TextField(null=True, blank=True)),
                ('resource_versionId', models.TextField(null=True, blank=True)),
                ('resolution_date', models.DateTimeField(null=True, blank=True)),
                ('resolution_actor', models.CharField(max_length=32, null=True, blank=True)),
                ('creation_actor', models.TextField(null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='IssueState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='IssueType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('weight', models.FloatField(null=True, blank=True)),
                ('attribute', models.TextField(null=True, blank=True)),
                ('field_name', models.TextField(null=True, blank=True)),
                ('field_value', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField()),
                ('type', models.TextField()),
                ('note', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ontology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('data', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.TextField(null=True, blank=True)),
                ('term', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('function', models.ForeignKey(related_name='operation', blank=True, to='elixir.Function', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OtherID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=1000)),
                ('type', models.TextField(null=True, blank=True)),
                ('version', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Output',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('data', models.ForeignKey(to='elixir.Data', null=True)),
                ('function', models.ForeignKey(related_name='output', blank=True, to='elixir.Function', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pmcid', models.TextField(null=True, blank=True)),
                ('pmid', models.TextField(null=True, blank=True)),
                ('doi', models.TextField(null=True, blank=True)),
                ('type', models.TextField(null=True, blank=True)),
                ('version', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PublicationAuthor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PublicationMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('journal', models.TextField(null=True, blank=True)),
                ('abstract', models.TextField(null=True, blank=True)),
                ('date', models.DateTimeField(null=True, blank=True)),
                ('citationCount', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('biotoolsID', models.CharField(max_length=100)),
                ('biotoolsCURIE', models.CharField(max_length=109)),
                ('name', models.TextField()),
                ('versionId', models.CharField(default=b'none', max_length=100, null=True)),
                ('homepage', models.TextField()),
                ('description', models.TextField()),
                ('short_description', models.TextField(null=True, blank=True)),
                ('canonicalID', models.TextField(null=True, blank=True)),
                ('issue_score', models.FloatField(null=True, blank=True)),
                ('version_hash', models.TextField(null=True, blank=True)),
                ('visibility', models.IntegerField(default=1, choices=[(0, b'NO'), (1, b'YES')])),
                ('latest', models.IntegerField(default=1, choices=[(0, b'NO'), (1, b'YES')])),
                ('was_id_validated', models.IntegerField(default=0, choices=[(0, b'NO'), (1, b'YES')])),
                ('homepage_status', models.IntegerField(default=0, choices=[(0, b'UP'), (1, b'DOWN'), (2, b'DEAD')])),
                ('cost', models.TextField(null=True, blank=True)),
                ('maturity', models.TextField(null=True, blank=True)),
                ('license', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(null=True, blank=True)),
                ('lastUpdate', models.DateTimeField(auto_now=True)),
                ('availability', models.TextField(null=True, blank=True)),
                ('downtime', models.TextField(null=True, blank=True)),
                ('editPermission', models.ForeignKey(to='elixir.EditPermission', blank=True)),
                ('elixirInfo', models.ForeignKey(blank=True, to='elixir.ElixirInfo', null=True)),
                ('owner', models.ForeignKey(related_name='resource', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('requestId', models.CharField(max_length=50)),
                ('type', models.TextField(null=True, blank=True)),
                ('completed', models.BooleanField(default=False)),
                ('accepted', models.BooleanField(default=False)),
                ('completedBy', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('resource', models.ForeignKey(related_name='requests', blank=True, to='elixir.Resource', null=True)),
                ('user', models.ForeignKey(related_name='requests', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SearchQueryLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SearchTermLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, null=True, blank=True)),
                ('term', models.CharField(max_length=32, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatsData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('totalEntries', models.IntegerField(default=0)),
                ('creditAffiliationCount', models.IntegerField()),
                ('edamAnnotationsCount', models.IntegerField()),
                ('formatAnnotationsCount', models.IntegerField()),
                ('functionAnnotationsCount', models.IntegerField()),
                ('topicAnnotationsCount', models.IntegerField()),
                ('dataTypeAnnotationsCount', models.IntegerField()),
                ('nameAnnotationCount', models.IntegerField(default=0)),
                ('uniqueIDAnnotationCount', models.IntegerField(default=0)),
                ('topicAnnotationCount', models.IntegerField(default=0)),
                ('operatingSystemAnnotationCount', models.IntegerField(default=0)),
                ('codeAvailabilityAnnotationCount', models.IntegerField(default=0)),
                ('operationAnnotationCount', models.IntegerField(default=0)),
                ('descriptionAnnotationCount', models.IntegerField(default=0)),
                ('downloadsAnnotationCount', models.IntegerField(default=0)),
                ('dataFormatsAnnotationCount', models.IntegerField(default=0)),
                ('accessibilityAnnotationCount', models.IntegerField(default=0)),
                ('toolTypeAnnotationCount', models.IntegerField(default=0)),
                ('documentationAnnotationCount', models.IntegerField(default=0)),
                ('inputOutputAnnotationCount', models.IntegerField(default=0)),
                ('communityAnnotationCount', models.IntegerField(default=0)),
                ('contactAnnotationCount', models.IntegerField(default=0)),
                ('homepageAnnotationCount', models.IntegerField(default=0)),
                ('publicationAnnotationCount', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ToolType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('resource', models.ForeignKey(related_name='toolType', blank=True, to='elixir.Resource', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.TextField(null=True, blank=True)),
                ('term', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('resource', models.ForeignKey(related_name='topic', blank=True, to='elixir.Resource', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Uses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('homepage', models.TextField(null=True, blank=True)),
                ('version', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('resource', models.ForeignKey(related_name='uses', blank=True, to='elixir.Resource', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.TextField(null=True, blank=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
                ('resource', models.ForeignKey(related_name='version', blank=True, to='elixir.Resource', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('biotoolsID', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('sourceURL', models.TextField(null=True, blank=True)),
                ('image', models.ImageField(height_field=b'image_height', width_field=b'image_width', upload_to=b'workflows/')),
                ('image_width', models.IntegerField(default=0)),
                ('image_height', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowAnnotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startX', models.FloatField()),
                ('startY', models.FloatField()),
                ('endX', models.FloatField()),
                ('endY', models.FloatField()),
                ('title', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('edam_term', models.TextField(null=True, blank=True)),
                ('edam_uri', models.TextField(null=True, blank=True)),
                ('url', models.TextField(null=True, blank=True)),
                ('workflow', models.ForeignKey(related_name='annotations', blank=True, to='elixir.Workflow', null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='searchtermlog',
            unique_together=set([('name', 'term')]),
        ),
        migrations.AddField(
            model_name='searchquerylog',
            name='terms',
            field=models.ManyToManyField(related_name='queries', to='elixir.SearchTermLog'),
        ),
        migrations.AddField(
            model_name='publicationauthor',
            name='metadata',
            field=models.ForeignKey(related_name='authors', blank=True, to='elixir.PublicationMetadata', null=True),
        ),
        migrations.AddField(
            model_name='publication',
            name='metadata',
            field=models.OneToOneField(related_name='publication', null=True, blank=True, to='elixir.PublicationMetadata'),
        ),
        migrations.AddField(
            model_name='publication',
            name='resource',
            field=models.ForeignKey(related_name='publication', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='otherid',
            name='resource',
            field=models.ForeignKey(related_name='otherID', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='operatingsystem',
            name='resource',
            field=models.ForeignKey(related_name='operatingSystem', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='resource',
            field=models.ForeignKey(related_name='link', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='resource',
            field=models.ForeignKey(related_name='language', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='issue_state',
            field=models.ForeignKey(to='elixir.IssueState'),
        ),
        migrations.AddField(
            model_name='issue',
            name='issue_type',
            field=models.ForeignKey(to='elixir.IssueType'),
        ),
        migrations.AddField(
            model_name='function',
            name='resource',
            field=models.ForeignKey(related_name='function', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='format',
            name='input',
            field=models.ForeignKey(related_name='format', blank=True, to='elixir.Input', null=True),
        ),
        migrations.AddField(
            model_name='format',
            name='output',
            field=models.ForeignKey(related_name='format', blank=True, to='elixir.Output', null=True),
        ),
        migrations.AddField(
            model_name='elixirplatform',
            name='resource',
            field=models.ForeignKey(related_name='elixirPlatform', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='elixirnode',
            name='resource',
            field=models.ForeignKey(related_name='elixirNode', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='download',
            name='resource',
            field=models.ForeignKey(related_name='download', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='documentation',
            name='resource',
            field=models.ForeignKey(related_name='documentation', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='credit',
            name='resource',
            field=models.ForeignKey(related_name='credit', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='resource',
            field=models.ForeignKey(related_name='contact', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='collectionid',
            name='resource',
            field=models.ForeignKey(related_name='collectionID', blank=True, to='elixir.Resource', null=True),
        ),
        migrations.AddField(
            model_name='accessibility',
            name='resource',
            field=models.ForeignKey(related_name='accessibility', blank=True, to='elixir.Resource', null=True),
        ),
    ]
