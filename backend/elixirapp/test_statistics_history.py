from datetime import datetime, timezone
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connection
from django.test import SimpleTestCase, TestCase

from elixir.models import Data, EditPermission, Format, Function, Input, Operation, Output, Resource, StatsData, Topic
from elixir.stats import StatsInfo
from elixirapp.statistics import contributor_months, estimated_growth, line_chart


class StatisticsHistoryTests(SimpleTestCase):
    def test_monthly_history_uses_the_latest_recorded_snapshot(self):
        snapshots = [
            StatsData(date=datetime(2024, 11, 1, tzinfo=timezone.utc), totalEntries=10, nameAnnotationCount=10),
            StatsData(date=datetime(2024, 11, 30, tzinfo=timezone.utc), totalEntries=15, nameAnnotationCount=15),
            StatsData(date=datetime(2025, 11, 1, tzinfo=timezone.utc), totalEntries=20, nameAnnotationCount=20),
        ]
        source = StatsInfo()
        with patch.object(source, 'statsDataForLast', return_value=snapshots):
            entries = source.totalEntriesForLast(24)
            annotations = source.totalAnnotationsCountForLast(24)
        self.assertEqual([row['entriesCount'] for row in entries], [15, 20])
        self.assertEqual([row['nameAnnotationCount'] for row in annotations], [15, 20])
        self.assertEqual([row['date'] for row in entries], [snapshots[1].date, snapshots[2].date])

    def test_line_chart_keeps_zero_and_uses_time_for_the_x_axis(self):
        chart = line_chart([
            {'date': '2024-01-01', 'count': 0},
            {'date': '2024-02-01', 'count': 1},
            {'date': '2024-04-01', 'count': 4},
        ], [('count', 'Tools')])
        points = chart['series'][0]['points']
        self.assertEqual((points[0]['y'], points[-1]['y']), (205, 35))
        self.assertLess(points[1]['x'], (points[0]['x'] + points[-1]['x']) / 2)
        self.assertEqual([point['value'] for point in points], [0, 1, 4])

    def test_contributor_chart_fills_months_without_new_accounts(self):
        rows = contributor_months([
            {'date': '2024-12-01', 'totalUsersCount': 3, 'newUsersCount': 3},
            {'date': '2025-02-01', 'totalUsersCount': 4, 'newUsersCount': 1},
        ])
        self.assertEqual([row['newUsersCount'] for row in rows], [3, 0, 1])
        self.assertEqual([row['totalUsersCount'] for row in rows], [3, 3, 4])


class EstimatedGrowthTests(TestCase):
    def test_contributing_domains_count_uses_full_domains_without_exposing_addresses(self):
        User.objects.create_user('one', email='one@example.org')
        User.objects.create_user('two', email='two@EXAMPLE.ORG')
        User.objects.create_user('three', email='three@lab.example.org')
        User.objects.create_user('invalid', email='not-an-address')
        User.objects.create_user('placeholder', email='placeholder@biotools.local')
        self.assertEqual(StatsInfo().contributingDomainsCount(datetime(2100, 1, 1, tzinfo=timezone.utc)), 2)

    def test_counts_current_public_records_by_their_creation_month(self):
        user = User.objects.create_user('growth-owner')
        permissions = EditPermission.objects.create()
        common = {'owner': user, 'editPermission': permissions, 'homepage': '', 'description': ''}
        public = Resource.objects.create(biotoolsID='public', biotoolsCURIE='biotools:public', name='Public',
                                         additionDate=datetime(2020, 1, 10, tzinfo=timezone.utc), **common)
        private = Resource.objects.create(biotoolsID='private', biotoolsCURIE='biotools:private', name='Private',
                                          visibility=0, additionDate=datetime(2020, 1, 10, tzinfo=timezone.utc), **common)
        topic = Topic.objects.create(resource=public, term='Topic')
        Topic.objects.create(resource=private, term='Excluded')
        function = Function.objects.create(resource=public)
        operation = Operation.objects.create(function=function, term='Operation')
        input_data = Data.objects.create(term='Input')
        output_data = Data.objects.create(term='Output')
        inp = Input.objects.create(function=function, data=input_data)
        out = Output.objects.create(function=function, data=output_data)
        first_format = Format.objects.create(input=inp, term='Input format')
        second_format = Format.objects.create(output=out, term='Output format')
        for item in (topic, operation, input_data, output_data, first_format, second_format):
            type(item).objects.filter(pk=item.pk).update(additionDate=datetime(2020, 2, 10, tzinfo=timezone.utc))

        rows = estimated_growth(datetime(2020, 4, 1, tzinfo=timezone.utc))
        self.assertEqual([row['date'].isoformat() for row in rows], ['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01'])
        self.assertEqual(rows[0]['entriesCount'], 1)
        self.assertEqual(rows[0]['edamAnnotationsCount'], 0)
        self.assertEqual(rows[1]['edamAnnotationsCount'], 6)
        self.assertEqual(rows[-1]['edamAnnotationsCount'], 6)


@skipUnless(connection.vendor == 'mysql', 'Contributor growth uses MySQL date extraction')
class ContributorHistoryTests(TestCase):
    def test_growth_is_chronological_even_if_users_are_created_out_of_order(self):
        User.objects.create_user('later', date_joined=datetime(2025, 2, 1, tzinfo=timezone.utc))
        User.objects.create_user('earlier', date_joined=datetime(2024, 12, 1, tzinfo=timezone.utc))
        rows = StatsInfo().userGrowthByMonth()
        self.assertEqual([row['date'] for row in rows], ['2024-12-01T00:00:00Z', '2025-02-01T00:00:00Z'])
        self.assertEqual([row['totalUsersCount'] for row in rows], [1, 2])
