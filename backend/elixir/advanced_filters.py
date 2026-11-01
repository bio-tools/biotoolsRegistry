"""Allow-listed, conjunctive search conditions shared by workspace reads."""
import json
import math
import re
from datetime import date, timedelta

from django.conf import settings


MAX_FILTERS = 8
MAX_FILTER_BYTES = 4096
PUBLICATION_FIELDS = ('doi', 'pmid', 'pmcid')
SOURCE_FIELDS = ['topic.uri', *['publication.' + key for key in PUBLICATION_FIELDS]]


def score_definitions():
    # No production model is implied. Deployments must provision versioned numeric fields.
    return getattr(settings, 'SEARCH_WORKSPACE_SCORES', [])


def score_metadata():
    return [{key: score[key] for key in ('key', 'label', 'version', 'min', 'max')}
            for score in score_definitions()]


def validate_filters(filters, scope='server'):
    if not isinstance(filters, list) or len(filters) > MAX_FILTERS:
        raise ValueError('Use at most eight advanced filters.')
    scores = {score['key']: score for score in score_definitions()}
    result = []
    for condition in filters:
        if not isinstance(condition, dict) or condition.get('scope') != scope:
            raise ValueError('Invalid advanced filter scope.')
        kind, field = condition.get('type'), condition.get('field')
        keys = {'type', 'field', 'scope'}
        if kind == 'boolean' and field == 'hasPublication':
            keys.add('value')
            valid = type(condition.get('value')) is bool
        elif kind in ('categorical', 'ontology') and field == {'categorical': 'toolType', 'ontology': 'topic'}[kind]:
            keys.add('values')
            values = condition.get('values')
            valid = isinstance(values, list) and 1 <= len(values) <= 10 and all(
                isinstance(value, str) and 0 < len(value) <= 256 and not re.search(r'[\x00-\x1f\x7f]', value)
                and (kind != 'ontology' or re.fullmatch(r'http://edamontology.org/topic_[0-9]{4}', value))
                for value in values)
        elif (kind == 'range' and field == 'added') or (kind == 'score' and isinstance(field, str) and field in scores):
            keys.update(('min', 'max'))
            bounds = [condition[key] for key in ('min', 'max') if key in condition]
            valid = bool(bounds)
            if kind == 'range':
                for value in bounds:
                    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
                        valid = False
                    else:
                        try:
                            valid = valid and date.fromisoformat(value) < date.max
                        except ValueError:
                            valid = False
            else:
                keys.add('version')
                score = scores[field]
                valid = valid and condition.get('version') == score['version'] and all(
                    type(value) in (int, float) and math.isfinite(value) and score['min'] <= value <= score['max']
                    for value in bounds)
            if valid and len(bounds) == 2:
                valid = bounds[0] <= bounds[1]
        else:
            raise ValueError('Unsupported advanced filter type or field.')
        if not valid or set(condition) - keys:
            raise ValueError('Invalid advanced filter value, bounds, version or operator.')
        normalized = {key: condition[key] for key in sorted(condition)}
        if 'values' in normalized:
            normalized['values'] = sorted(set(normalized['values']))
        result.append(normalized)
    return result


def parse_filters(raw):
    if len(raw.encode('utf-8')) > MAX_FILTER_BYTES:
        raise ValueError('Advanced filters exceed 4096 bytes.')
    try:
        return validate_filters(json.loads(raw))
    except (ValueError, TypeError, RecursionError) as exc:
        raise ValueError('Invalid advanced filters: use supported fields, bounds and score versions.') from exc


def filter_clauses(filters):
    scores = {score['key']: score for score in score_definitions()}
    clauses = []
    for condition in validate_filters(filters):
        kind, field = condition['type'], condition['field']
        if kind == 'boolean':
            presence = {'bool': {'should': [{'exists': {'field': 'publication.' + key}}
                                            for key in PUBLICATION_FIELDS], 'minimum_should_match': 1}}
            clauses.append(presence if condition['value'] else {'bool': {'must_not': [presence]}})
        elif kind in ('categorical', 'ontology'):
            clauses.append({'terms': { 'toolType.raw' if kind == 'categorical' else 'topic.uri.keyword': condition['values']}})
        else:
            bounds = {}
            if 'min' in condition:
                bounds['gte'] = condition['min']
            if 'max' in condition:
                if kind == 'range':
                    bounds['lt'] = (date.fromisoformat(condition['max']) + timedelta(days=1)).isoformat()
                else:
                    bounds['lte'] = condition['max']
            if kind == 'range':
                bounds['format'] = 'strict_date'
            clauses.append({'range': {'additionDate' if kind == 'range' else scores[field]['field']: bounds}})
    return clauses


def filter_values(item):
    scores = {}
    for definition in score_definitions():
        value = item.get(definition['field'])
        if type(value) in (int, float) and math.isfinite(value):
            scores[definition['key']] = value
    return {
        'hasPublication': any(publication.get(key) is not None for publication in item.get('publication', [])
                              for key in PUBLICATION_FIELDS),
        'added': (item.get('additionDate') or '')[:10],
        'toolType': item.get('toolType', []),
        'topic': [topic['uri'] for topic in item.get('topic', []) if topic.get('uri')],
        'scores': scores,
    }
