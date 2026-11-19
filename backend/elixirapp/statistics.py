"""Growth charts and estimates from the registry's existing dated records."""
from collections import defaultdict
from datetime import date, timedelta

from django.db.models import Count
from django.db.models.functions import TruncMonth

from elixir.models import Data, Format, Operation, Resource, Topic


def estimated_growth(as_of):
    # shortcut: deleted or replaced records cannot be recovered from creation dates; use saved snapshots when available.
    sources = (
        ('entriesCount', Resource.objects.filter(visibility=1)),
        ('topicAnnotationsCount', Topic.objects.filter(resource__visibility=1)),
        ('functionAnnotationsCount', Operation.objects.filter(function__resource__visibility=1)),
        ('dataTypeAnnotationsCount', Data.objects.filter(input__function__resource__visibility=1)),
        ('dataTypeAnnotationsCount', Data.objects.filter(output__function__resource__visibility=1)),
        ('formatAnnotationsCount', Format.objects.filter(input__function__resource__visibility=1)),
        ('formatAnnotationsCount', Format.objects.filter(output__function__resource__visibility=1)),
    )
    monthly = defaultdict(lambda: defaultdict(int))
    for key, queryset in sources:
        counts = (queryset.filter(additionDate__lt=as_of).annotate(month=TruncMonth('additionDate'))
                  .values('month').annotate(total=Count('pk')).order_by('month'))
        for row in counts:
            if row['month']:
                monthly[row['month'].date()][key] += row['total']
    if not monthly:
        return []

    month = min(monthly)
    last = as_of.date().replace(day=1)
    totals = defaultdict(int)
    rows = []
    while month <= last:
        for key, value in monthly[month].items():
            totals[key] += value
        rows.append({'date': month, 'entriesCount': totals['entriesCount'],
                     'topicAnnotationsCount': totals['topicAnnotationsCount'],
                     'functionAnnotationsCount': totals['functionAnnotationsCount'],
                     'dataTypeAnnotationsCount': totals['dataTypeAnnotationsCount'],
                     'formatAnnotationsCount': totals['formatAnnotationsCount'],
                     'edamAnnotationsCount': sum(totals[key] for key in (
                         'topicAnnotationsCount', 'functionAnnotationsCount',
                         'dataTypeAnnotationsCount', 'formatAnnotationsCount'))})
        month = date(month.year + (month.month == 12), month.month % 12 + 1, 1)
    return rows


def line_chart(rows, fields):
    """Prepare a responsive SVG and a table from the same measured values."""
    def day(value):
        return value.date() if hasattr(value, 'date') else date.fromisoformat(str(value)[:10])

    rows = sorted(rows, key=lambda row: day(row['date']))
    dates = [day(row['date']) for row in rows]
    maximum = max([1, *(row[key] for row in rows for key, _ in fields if key in row)])
    if any(isinstance(row[key], bool) or not isinstance(row[key], int) or row[key] < 0
           for row in rows for key, _ in fields if key in row):
        raise ValueError('Invalid statistics count')
    span = max(1, (dates[-1] - dates[0]).days)
    series = []
    for index, (key, label) in enumerate(fields):
        points = []
        for row, measured in zip(rows, dates):
            if key in row:
                x = round(70 + (measured - dates[0]).days * 700 / span, 2)
                y = round(205 - row[key] * 170 / maximum, 2)
                points.append({'x': x, 'y': y, 'date': measured, 'value': row[key]})
        if points:
            series.append({'label': label, 'index': index, 'points': points,
                           'coordinates': ' '.join(f"{point['x']},{point['y']}" for point in points)})
    ticks = sorted({dates[0] + timedelta(days=round((dates[-1] - dates[0]).days * i / 4)) for i in range(5)})
    return {'series': series, 'rows': rows,
            'y_ticks': [{'y': 205 - i * 42.5, 'value': round(maximum * i / 4)} for i in range(5)],
            'x_ticks': [{'x': round(70 + (tick - dates[0]).days * 700 / span, 2),
                         'date': tick} for tick in ticks]}


def contributor_months(rows):
    by_month = {date.fromisoformat(str(row['date'])[:10]).replace(day=1): row for row in rows}
    month = min(by_month)
    last = max(by_month)
    total = 0
    result = []
    while month <= last:
        if month in by_month:
            total = by_month[month]['totalUsersCount']
            new = by_month[month]['newUsersCount']
        else:
            new = 0
        result.append({'date': month, 'totalUsersCount': total, 'newUsersCount': new})
        month = date(month.year + (month.month == 12), month.month % 12 + 1, 1)
    return result
