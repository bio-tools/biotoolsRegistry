from html.parser import HTMLParser
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import get_script_prefix, set_script_prefix
from elasticsearch import Elasticsearch

from elixir.models import (Resource, EditPermission, Function, Operation, Input, Data,
                           Format, Relation, Publication, PublicationMetadata,
                           PublicationAuthor, PublicationType, Credit, CreditTypeRole, OtherID)
from elixir.queries import get_tool_detail
from elixir.templatetags.detail_tags import field_icon
from elixirapp.tests.detail_fixtures import create_detail_fixture


class Links(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.urls = []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for name, value in attrs if name in ('href', 'src'))


@override_settings(DEBUG=False)
class ToolDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('detail-owner')
        cls.rich = create_detail_fixture(cls.owner)
        cls.sparse = Resource.objects.create(
            biotoolsID='migration-fixture', name='Sparse Tool', owner=cls.owner,
            editPermission=EditPermission.objects.create(type='private'))
        cls.hidden = Resource.objects.create(
            biotoolsID='hidden-detail', name='Hidden Tool', visibility=0, owner=cls.owner,
            editPermission=EditPermission.objects.create(type='public'))

    def setUp(self):
        self.addCleanup(set_script_prefix, get_script_prefix())
        set_script_prefix('')

    def page(self, identifier='detail-demo', **kwargs):
        return self.client.get('/tool/' + identifier + '/', **{'biotools.html': True, **kwargs})

    def test_rich_content_links_metadata_and_no_backend_http(self):
        with patch.object(Elasticsearch, 'search', side_effect=AssertionError('No search needed')), \
                patch('requests.get', side_effect=AssertionError('No internal or enrichment HTTP')):
            response = self.page()
        self.assertEqual(response.status_code, 200)
        for text in ('Sequence Workbench (demo)', 'biotools:detail-demo', 'Sequence analysis',
                     'Sequence alignment', 'FASTA', 'ClustalW', 'Example Research Team',
                     'Example Methods', 'Fictional citation', 'User manual', 'Source code',
                     'Issue tracker', 'Maintainer', 'Local demonstration', 'Proteomics',
                     'MIT', '2.4.0', 'Linux', 'Added', 'Updated'):
            self.assertContains(response, text)
        links = Links(response.content.decode()).urls
        for href in ('/api/t/detail-demo?format=json', '/api/t/detail-demo?format=xml',
                     '/api/t/detail-demo?format=jsonld', 'http://testserver/detail-demo',
                     '/tool/migration-fixture/', 'https://doi.org/10.5555/detail-demo',
                     '/t?topicID=%22topic_0080%22', '/t?inputDataFormatID=%22format_1929%22'):
            self.assertIn(href, links)
        self.assertContains(response, 'noindex, nofollow')
        self.assertContains(response, '<details>')
        self.assertContains(response, 'class="bip-embed"')
        self.assertContains(response, 'class="altmetric-embed"')
        self.assertContains(response, 'class="__dimensions_badge_embed__"')
        self.assertContains(response, 'https://badge.dimensions.ai/static/ai/badge.js')
        self.assertContains(response, '/static/html/field-icons.svg#function')
        self.assertContains(response, '/static/html/field-icons.svg#publication')
        self.assertContains(response, 'title="Open this term in the EDAM ontology"')
        self.assertContains(response, 'title="Search bio.tools for tools annotated with Sequence analysis"')
        self.assertContains(response, 'title="Search bio.tools for tools credited to Example Research Team"')
        self.assertNotContains(response, '<object')

    def test_unknown_field_type_uses_a_generic_decorative_icon(self):
        self.assertEqual(field_icon('number'), 'number')
        self.assertEqual(field_icon('new-schema-type'), 'object')

    def test_sparse_record_omits_optional_sections(self):
        response = self.page('migration-fixture')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Sparse Tool</h1>')
        for absent in ('id="functions"', 'id="publications"', 'id="credits"',
                       'id="downloads"', 'id="relationships"', '>None<'):
            self.assertNotContains(response, absent)

    def test_publication_without_enrichment_keeps_identifier_and_heading(self):
        publication = self.rich.publication.first()
        publication.metadata = None
        Publication.objects.filter(pk=publication.pk).update(metadata=None)
        response = self.page()
        self.assertContains(response, '<h3>Publication 1</h3>')
        self.assertContains(response, 'https://doi.org/10.5555/detail-demo')

    def test_publication_badges_use_valid_identifiers_and_fall_back(self):
        publication = self.rich.publication.first()
        PublicationMetadata.objects.filter(pk=publication.metadata_id).update(citationCount=330)
        Publication.objects.filter(pk=publication.pk).update(doi='https://doi.org/10.5555/detail-demo', pmid='12345')
        response = self.page()
        self.assertContains(response, 'data-doi="10.5555/detail-demo"', count=3)
        self.assertNotContains(response, 'Citation count')
        self.assertContains(response, 'https://europepmc.org/search?query=CITES%3A12345_MED')
        self.assertContains(response, 'https://cdn.jsdelivr.net/gh/athenarc/bip-plugin@main/embed.min.js')

        Publication.objects.filter(pk=publication.pk).update(doi='', pmid='12345')
        response = self.page()
        self.assertContains(response, 'data-pmid="12345"', count=2)
        self.assertNotContains(response, 'class="bip-embed"')
        self.assertNotContains(response, 'bip-plugin@main')

        Publication.objects.filter(pk=publication.pk).update(doi='invalid"doi', pmid='bad-123')
        response = self.page()
        self.assertNotContains(response, 'class="bip-embed"')
        self.assertNotContains(response, 'class="altmetric-embed"')
        self.assertNotContains(response, 'badge.dimensions.ai')
        self.assertNotContains(response, 'CITES%3A')
        self.assertContains(response, 'invalid&quot;doi')

    def test_partner_branding_and_identifiers_are_visible_when_present(self):
        self.rich.elixir_badge = 7
        self.rich.save(update_fields=['elixir_badge'])
        OtherID.objects.create(resource=self.rich, type='RRID', value='RRID:SCR_000001')
        response = self.page()
        for text in ('/img/opeb_logo.gif', '/img/tess_logo.png', '/img/edd.png', '/img/cdr.png',
                     '/img/rir.png', '/img/scicrunch.png', 'https://scicrunch.org/resolver/RRID%3ASCR_000001',
                     'https://openebench.bsc.es/tool/detail-demo', 'Version 2.4.0', 'Command-line tool'):
            self.assertContains(response, text)
        sparse = self.page('migration-fixture')
        self.assertNotContains(sparse, '/img/scicrunch.png')

    def test_missing_hidden_and_malformed_identifiers(self):
        for identifier in ('missing-detail', 'hidden-detail', 'bad:id', 'x' * 101, '<script>'):
            with self.subTest(identifier=identifier):
                response = self.page(identifier)
                self.assertEqual(response.status_code, 404)
                self.assertTemplateUsed(response, 'html/404.html')
        self.client.force_login(self.owner)
        self.assertEqual(self.page('hidden-detail').status_code, 404)

    def test_case_prefix_refresh_head_and_mutations(self):
        for identifier in ('DETAIL-DEMO', 'biotools:detail-demo'):
            self.assertContains(self.page(identifier), '<h1>Sequence Workbench (demo)</h1>')
        # CSRF masks intentionally change per render; freeze only their randomness here.
        with patch('django.middleware.csrf._get_new_csrf_string', return_value='a' * 32):
            self.assertEqual(self.page().content, self.page().content)
        response = self.client.head('/tool/detail-demo/', **{'biotools.html': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
        self.assertEqual(self.client.post('/tool/detail-demo/', **{'biotools.html': True}).status_code, 405)

    def test_migration_mount_and_api_stay_distinct(self):
        set_script_prefix('/_migration/html')
        response = self.page(SCRIPT_NAME='/_migration/html')
        self.assertContains(response, 'href="/_migration/html/tool/migration-fixture/"')
        api = self.client.get('/t/detail-demo', HTTP_ACCEPT='application/json')
        self.assertEqual(api.status_code, 200)
        self.assertEqual(api.json()['name'], self.rich.name)
        self.assertNotIn('text/html', api['Content-Type'])

    def test_untrusted_text_urls_and_incomplete_nested_metadata(self):
        self.rich.name = '<script>alert(1)</script>'
        self.rich.description = '<img src=x onerror=alert(1)>'
        self.rich.homepage = 'javascript:alert(1)'
        self.rich.save()
        self.rich.link.update(url='data:text/html,<script>alert(1)</script>')
        self.rich.credit.update(url='javascript:alert(1)', orcidid='javascript:alert(2)')
        self.rich.topic.update(uri='javascript:alert(3)', term='<b>unsafe label</b>')
        Relation.objects.create(resource=self.rich, biotoolsID='bad/id', type='related')
        function = Function.objects.create(resource=self.rich)
        Input.objects.create(function=function, data=None)
        Publication.objects.bulk_create([Publication(resource=self.rich, pmid='123', metadata=None)])
        response = self.page()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<img src=x')
        self.assertNotContains(response, '<b>unsafe label</b>')
        self.assertFalse(any(url.startswith(('javascript:', 'data:')) for url in Links(response.content.decode()).urls))

    def test_prefetch_cost_does_not_grow_with_nested_functions(self):
        with CaptureQueriesContext(connection) as baseline:
            self.assertEqual(self.page().status_code, 200)
        for _ in range(8):
            function = Function.objects.create(resource=self.rich, note='Another function')
            Operation.objects.create(function=function, term='Operation', uri='http://edamontology.org/operation_0004')
            input_data = Input.objects.create(function=function, data=Data.objects.create(term='Data'))
            Format.objects.create(input=input_data, term='Format')
            metadata = PublicationMetadata.objects.create(title='Another publication')
            Publication.objects.bulk_create([Publication(resource=self.rich, metadata=metadata)])
            publication = Publication.objects.get(metadata=metadata)
            PublicationType.objects.create(publication=publication, type='Other')
            PublicationAuthor.objects.create(metadata=metadata, name='Another author')
            credit = Credit.objects.create(resource=self.rich, name='Another contributor')
            CreditTypeRole.objects.create(credit=credit, typeRole='Developer')
        with CaptureQueriesContext(connection) as expanded:
            self.assertEqual(self.page().status_code, 200)
        self.assertEqual(len(expanded), len(baseline))
        self.assertLessEqual(len(expanded), 35)
        resource_queries = [q for q in expanded if 'FROM `elixir_resource`' in q['sql']]
        self.assertEqual(len(resource_queries), 1)
        tool = get_tool_detail(self.rich.biotoolsID)
        with self.assertNumQueries(0):
            for function in tool.function.all():
                for input_data in function.input.all():
                    list(input_data.format.all())
                    self.assertIsNotNone(input_data.data)
