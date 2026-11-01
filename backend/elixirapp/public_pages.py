"""Read-only public pages; the public REST API remains unchanged."""
import logging
import re
from urllib.parse import urlencode

from django import forms
from django.db import DatabaseError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_safe
from elasticsearch.exceptions import TransportError

from elixir.queries import public_domains
from elixir.stats import StatsInfo


logger = logging.getLogger(__name__)
REDIRECTS = {
    'schema': 'https://github.com/bio-tools/biotoolsSchema',
    'governance': 'https://biotools.readthedocs.io/en/latest/governance.html',
    'events': 'https://docs.google.com/document/d/1K-6IG_7a-4amstSSOxYjjJ3uDUEg4-WGSSt9jvvO7Ik/edit#heading=h.twop51kvyu80',
    'mail': 'http://elixirmail.cbs.dtu.dk/mailman/listinfo',
    'faq': 'https://docs.google.com/document/d/1WdcY0WQJVdRHz0BAhII7s8gygxKRJaHZC4gOnAC1eqs/edit',
    'apidoc': 'https://docs.google.com/document/d/1c1zridWLBNSrWcYyR2fnBfgjWfrUSrT7HJ6Ql6ZCkS4/edit#heading=h.9a2zbl9ka0z0',
    'changelog': 'https://docs.google.com/document/d/1C5KFu2t4OIAuUpx6dS7Djsa9y3zgicd8naOsAs9QPAY/edit#heading=h.eu5jkfa77et',
    'helpdesk': 'https://elixir-registry.atlassian.net/servicedesk/customer/portal/2/user/login?destination=portal%2F2',
    'projects': 'https://docs.google.com/document/d/1QBIZHBzHxxmvSnOG3xK6t3SCeft5g4AH2rVICLRLmDw/edit#heading=h.a6i4b9p7xdw7',
    'roadmap': 'https://docs.google.com/document/d/17iH72hmwVo205QVEkptv7GTMlqFojatIwMmxVOyuPy8/edit#heading=h.m1jhkecru8xq',
}
PAGES = {'', 'about', 'community', 'communities', 'domains', 'stats', '404', *REDIRECTS}
DOMAIN_FIELDS = [('title', 'Title'), ('sub_title', 'Subtitle'), ('collection', 'Collection'),
                 ('tag', 'Tags'), ('description', 'Description'), ('resources', 'Tools')]


class DomainSearchForm(forms.Form):
    q = forms.CharField(label='Search domains', required=False, max_length=256)
    field = forms.MultipleChoiceField(label='Search in', choices=DOMAIN_FIELDS, required=False,
                                      widget=forms.CheckboxSelectMultiple,
                                      initial=['title', 'sub_title', 'collection', 'tag'])


def domain_matches(domain, query, fields):
    values = [domain['domain']]
    for field in fields:
        value = domain.get(field) or ''
        if field == 'resources':
            values.extend(str(item.get(key) or '') for item in value for key in ('name', 'biotoolsID'))
        elif isinstance(value, list):
            values.extend(value)
        else:
            values.append(value)
    text = ' '.join(values).casefold()
    return all(term in text for term in query.casefold().split())


def metadata(request, name):
    canonical = 'communities' if name == 'community' else name
    return {'canonical_url': request.build_absolute_uri('/' + canonical),
            'public_indexable': getattr(request, 'canonical', False) and name in ('', 'about', 'community', 'communities', 'stats')}


@require_safe
def page(request, name=''):
    if name in REDIRECTS:
        # Only fixed reviewed destinations; never forward visitor query data.
        return HttpResponseRedirect(REDIRECTS[name])
    if name not in PAGES or name == '404':
        raise Http404
    if request.path != '/' and request.path.endswith('/'):
        query = request.META.get('QUERY_STRING', '')
        return HttpResponseRedirect(request.path.rstrip('/') + ('?' + query if query else ''))
    context = metadata(request, name)
    if name == 'domains':
        return domains(request, context)
    if name == 'stats':
        return statistics(request, context)
    template = 'home' if not name else 'communities' if name == 'community' else name
    return render(request, 'html/public/' + template + '.html', context)


def domains(request, context):
    form = DomainSearchForm(request.GET if request.GET else None)
    context.update(domain_form=form, domains=[], domain_count=0)
    if form.is_bound and not form.is_valid():
        return render(request, 'html/public/domains.html', context, status=400)
    try:
        entries = public_domains()
    except (TransportError, TimeoutError, ValueError, KeyError, TypeError):
        logger.exception('Public domain directory unavailable')
        context['unavailable'] = True
        return render(request, 'html/public/domains.html', context, status=503)
    query = form.cleaned_data['q'] if form.is_bound else ''
    fields = form.cleaned_data['field'] if form.is_bound else form.fields['field'].initial
    for entry in entries:
        entry['url'] = '/t?' + urlencode({'domain': entry['domain']})
        entry['collections'] = [{'name': value, 'url': '/t?' + urlencode({'collectionID': '"' + value + '"'})}
                                for value in entry.get('collection', [])]
    context.update(domains=[entry for entry in entries if domain_matches(entry, query, fields)],
                   domain_count=len(entries))
    return render(request, 'html/public/domains.html', context)


def label(key):
    key = re.sub(r'Counts?$', '', key)
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', key).strip().capitalize().replace('Edam', 'EDAM')


def count(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError('Invalid statistics count')
    return value


def series(rows):
    """Keep every returned measure and date; never invent missing measurements."""
    keys = list(dict.fromkeys(key for row in rows for key in row if key != 'date'))
    result = []
    for key in keys:
        values = [{'date': row['date'], 'value': count(row[key])} for row in rows if key in row]
        result.append({'label': label(key), 'values': values, 'maximum': max([1, *(row['value'] for row in values)])})
    return result


def statistics(request, context):
    source = StatsInfo()
    sections = []
    failed = False
    for title, read in (
            ('Current registry', lambda: source.statsData(10, timezone.now())),
            ('Content and EDAM growth', lambda: source.totalEntriesForLast(24)),
            ('Contributor growth', source.userGrowthByMonth),
            ('Annotation history', lambda: source.totalAnnotationsCountForLast(24))):
        section = {'title': title}
        try:
            data = read()
            if title == 'Current registry':
                section['date'] = data['date']
                section['counts'] = [{'label': label(key), 'value': count(value)} for key, value in data.items()
                                     if isinstance(value, int)]
                section['annotations'] = [{'label': label(key), 'value': count(value)}
                                          for key, value in data['totalAnnotationCount'].items()]
                section['annotation_total'] = sum(row['value'] for row in section['annotations'])
                section['breakdowns'] = []
                for key, values in data.items():
                    if isinstance(values, list):
                        entries = [{'label': str(next(value for field, value in item.items() if field != 'count')),
                                    'value': count(item['count'])} for item in values]
                        section['breakdowns'].append({'label': label(key), 'values': entries,
                            'maximum': max([1, *(row['value'] for row in entries)])})
            else:
                section['series'] = series(data)
                section['empty'] = not data
        except (DatabaseError, ValueError, KeyError, TypeError, StopIteration):
            logger.exception('Public statistics unavailable: %s', title)
            section = {'title': title, 'unavailable': True}
            failed = True
        sections.append(section)
    context['sections'] = sections
    if failed:
        context['public_indexable'] = False
    return render(request, 'html/public/stats.html', context, status=503 if failed else 200)
