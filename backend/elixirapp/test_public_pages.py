from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.db import OperationalError
from django.test import TestCase, override_settings
from django.urls import get_script_prefix, set_script_prefix

from elixir.queries import public_domains
from elixir.models import Domain
from elixirapp.html import canonical_family
from elixirapp.public_pages import PAGES, REDIRECTS
from elixirapp.test_html import HTML_REQUEST


DOMAIN = {'domain': 'public-fixture', 'title': 'Sequence analysis', 'sub_title': 'Curated tools',
          'description': '<script>unsafe()</script>', 'tag': ['genomics'], 'collection': ['A & B'],
          'resources': [{'biotoolsID': 'sample-one', 'name': 'Special application'}]}
CURRENT = {'date': '2026-10-23', 'totalEntries': 12, 'totalUsers': 3, 'edamAnnotationsCount': 7,
           'totalAnnotationCount': {'nameAnnotationCount': 12, 'topicAnnotationCount': 7},
           'topContributors': [{'domain': 'org', 'count': 3}], 'toolTypeCounts': [{'toolType': 'Web application', 'count': 5}]}


@override_settings(DEBUG=False)
class PublicPagesTests(TestCase):
    def setUp(self):
        self.addCleanup(set_script_prefix, get_script_prefix())
        set_script_prefix('')

    def get(self, path, **kwargs):
        return self.client.get(path, **{'biotools.canonical': True, **kwargs})

    def test_static_pages_content_aliases_and_metadata(self):
        for path, text in (('/', 'bio.tools'), ('/about', 'Publications and citing'),
                           ('/community', 'Systems Biology'), ('/communities', 'Rare Diseases')):
            for agent in ('Browser', 'Googlebot'):
                response = self.get(path, HTTP_USER_AGENT=agent)
                self.assertContains(response, text)
                self.assertNotContains(response, 'ng-app')
                self.assertNotContains(response, 'ng-href')
                self.assertNotContains(response, '/dist/')
                self.assertEqual(response['X-Biotools-Route'], 'django-public')
                self.assertEqual(response['X-Robots-Tag'], 'index, follow')
        self.assertContains(self.get('/community'), 'rel="canonical" href="http://testserver/communities"')
        self.assertContains(self.get('/'), 'action="/t"')
        self.assertContains(self.get('/'),
                            f'href="{settings.STATIC_URL.rstrip("/")}/html/favicon.ico"')
        self.assertIsNotNone(finders.find('html/favicon.ico'))
        self.assertEqual(settings.SPECTACULAR_SETTINGS['SWAGGER_UI_FAVICON_HREF'],
                         f"{settings.STATIC_URL.rstrip('/')}/html/favicon.ico")
        self.assertEqual(self.get('/about/?from=old')['Location'], '/about?from=old')
        self.assertContains(self.client.get('/public/about', **HTML_REQUEST), 'name="robots" content="noindex, follow"')

    def test_home_journeys_have_searchable_fallback_and_auth_aware_links(self):
        response = self.get('/')
        for text in ('Find a tool', 'Plan a workflow', 'Explore collections', 'Use tools with other services',
                     'Command-line tools for multiple sequence alignment with FASTA input', 'Sign in to create or manage a collection.',
                     'data-edam-url="/_edam/terms/"', 'inputDataFormatID=%22format_1929%22'):
            self.assertContains(response, text)
        self.assertContains(response, 'action="/t"')
        self.client.force_login(User.objects.create_user('home-test-user'))
        response = self.get('/')
        self.assertNotContains(response, 'Sign in to create or manage a collection.')
        self.assertContains(response, 'href="/edit-domain/"')

    def test_home_examples_include_only_public_domains(self):
        owner = User.objects.create_user('domain-owner')
        Domain.objects.create(name='bio-public', title='Biology', owner=owner)
        Domain.objects.create(name='bio-private', title='Private project', owner=owner, is_private=True)
        Domain.objects.create(name='bio-hidden', title='Hidden project', owner=owner, visibility=0)
        response = self.get('/')
        self.assertContains(response, 'href="/t?domain=bio-public"')
        self.assertNotContains(response, 'Private project')
        self.assertNotContains(response, 'Hidden project')

    @patch('elixirapp.public_pages.Domain.objects.filter', side_effect=OperationalError('offline'))
    def test_home_search_remains_available_without_collection_examples(self, _filter):
        with self.assertLogs('elixirapp.public_pages', level='WARNING'):
            response = self.get('/')
        self.assertContains(response, 'action="/t"')
        self.assertContains(response, 'Explore collections')

    def test_fixed_redirects_ignore_untrusted_destinations_and_keep_fragments(self):
        for path, destination in REDIRECTS.items():
            response = self.get('/' + path + '?next=https://attacker.invalid&token=secret')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], destination)
            self.assertNotIn('secret', response['Location'])

    def test_route_precedence_errors_boundaries_and_independent_rollback(self):
        for name in PAGES:
            self.assertEqual(canonical_family('/' + name), 'public')
        for path in ('/404', '/unknown/path', '/about/missing', '/about/edit', '/schema/extra'):
            response = self.get(path)
            self.assertEqual(response.status_code, 404)
            self.assertNotContains(response, 'ng-app', status_code=404)
            self.assertEqual(response['X-Robots-Tag'], 'noindex, follow')
        for path in ('/api/t', '/api/schema/', '/static/x.css', '/media/example.png', '/img/example.png', '/.well-known/example'):
            self.assertIsNone(canonical_family(path))
        for path in ('/domain-manager', '/edit-domain/example', '/workflows'):
            self.assertEqual(canonical_family(path), 'management')
        self.assertContains(self.get('/about?_legacy=1'), 'Publications and citing')
        self.assertEqual(self.client.post('/about', **{'biotools.canonical': True}).status_code, 405)

    @patch('elixirapp.public_pages.public_domains', return_value=[DOMAIN])
    def test_domain_directory_selection_encoding_and_empty_results(self, read):
        response = self.get('/domains')
        self.assertContains(response, '/t?domain=public-fixture')
        self.assertContains(response, 'collectionID=%22A+%26+B%22')
        self.assertEqual(response['X-Robots-Tag'], 'noindex, follow')
        self.assertContains(self.get('/domains?q=genomics&field=tag'), '1 of 1 domains')
        self.assertContains(self.get('/domains?q=Special&field=resources'), '1 of 1 domains')
        self.assertContains(self.get('/domains?q=Special&field=title'), 'No domains found')
        self.assertContains(self.get('/domains?q=public-fixture'), '1 of 1 domains')
        self.assertNotContains(self.get('/domains?q=unsafe&field=description'), '<script>unsafe()')
        self.assertEqual(self.get('/domains?field=owner').status_code, 400)
        self.assertEqual(self.get('/domains?q=' + 'x' * 257).status_code, 400)
        read.return_value = []
        self.assertContains(self.get('/domains'), '0 of 0 domains')

    @patch('elixirapp.public_pages.public_domains', side_effect=TimeoutError)
    def test_domain_failure_is_not_an_empty_directory(self, read):
        with self.assertLogs('elixirapp.public_pages', level='ERROR'):
            response = self.get('/domains')
        self.assertContains(response, 'temporarily unavailable', status_code=503)
        self.assertNotContains(response, 'No domains found', status_code=503)

    @patch('elixirapp.public_pages.StatsInfo')
    def test_statistics_render_all_sources_and_distinguish_empty_failure_zero(self, service):
        source = service.return_value
        source.statsData.return_value = CURRENT
        source.totalEntriesForLast.return_value = [{'date': '2026-09-01', 'entriesCount': 0, 'edamAnnotationsCount': 2}]
        source.userGrowthByMonth.return_value = [{'date': '2026-09-01', 'newUsersCount': 1, 'totalUsersCount': 3}]
        source.totalAnnotationsCountForLast.return_value = []
        response = self.get('/stats')
        self.assertContains(response, 'value="0"')
        self.assertContains(response, 'value="3"')
        self.assertContains(response, 'No historical measurements available.')
        self.assertContains(response, '<td>19</td>')
        self.assertContains(response, '<summary>Tool type</summary>')
        source.totalEntriesForLast.assert_called_once_with(24)
        source.totalAnnotationsCountForLast.assert_called_once_with(24)
        source.userGrowthByMonth.assert_called_once_with()
        source.userGrowthByMonth.side_effect = OperationalError('database unavailable')
        with self.assertLogs('elixirapp.public_pages', level='ERROR'):
            response = self.get('/stats')
        self.assertContains(response, 'This dataset is temporarily unavailable.', status_code=503)
        self.assertContains(response, 'Current registry', status_code=503)
        self.assertEqual(response['X-Robots-Tag'], 'noindex, follow')

    def test_statistics_with_real_database_services(self):
        response = self.get('/stats')
        self.assertContains(response, 'Current registry')
        self.assertContains(response, 'No historical measurements available.')
        self.assertNotContains(response, 'temporarily unavailable')

    def test_public_images_are_retained_byte_for_byte(self):
        root = Path(settings.BASE_DIR).parent
        assets = list((root / 'backend/elixir/static/public/img').rglob('*'))
        files = [path for path in assets if path.is_file()]
        self.assertEqual(len(files), 40)
        for path in files:
            relative = path.relative_to(root / 'backend/elixir/static/public')
            legacy = root / 'frontend' / relative
            if legacy.exists():
                self.assertEqual(path.read_bytes(), legacy.read_bytes())
            else:
                self.assertEqual(path.read_bytes(), (Path(settings.STATIC_ROOT) / 'public' / relative).read_bytes())

    def test_domain_read_projection_and_incomplete_response(self):
        result = {'hits': {'total': {'value': 1}, 'hits': [{'_source': DOMAIN}]}}
        with patch('elixir.queries.es.search', return_value=result) as search:
            self.assertEqual(public_domains(), [DOMAIN])
        self.assertNotIn('owner', search.call_args.kwargs['body']['_source'])
        for incomplete in ({**result, 'timed_out': True}, {**result, '_shards': {'failed': 1}},
                           {'hits': {'total': {'value': 2}, 'hits': result['hits']['hits']}}):
            with patch('elixir.queries.es.search', return_value=incomplete), self.assertRaises(TimeoutError):
                public_domains()
