"""Bounded selector reads over the ontology already used by API validators."""
import json
import re

from django.db import DatabaseError
from rest_framework.exceptions import ValidationError

from elixir.models import Ontology
from elixir.validators import OntologyValidator
from elixir.resource_schema import digest


SCOPES = ('topic', 'operation', 'data', 'format')
LIMIT = 20


class EdamUnavailable(Exception):
    pass


def check_scope(scope):
    if scope not in SCOPES:
        raise ValueError('Choose topic, operation, data or format.')


def check_uri(uri, scope):
    if not isinstance(uri, str) or not re.fullmatch(r'http://edamontology.org/' + scope + r'_[0-9]{4}', uri):
        raise ValueError('Use a canonical EDAM identifier in the declared concept scope.')


def nodes(root):
    pending = [root]
    while pending:
        node = pending.pop()
        yield node
        pending.extend(reversed(node.get('children', [])))


def term(node, obsolete=False):
    return {'uri': node['data']['uri'], 'term': node['text'],
            'definition': node.get('definition', '')[:600],
            'synonyms': list(dict.fromkeys(node.get('exact_synonyms', []) + node.get('narrow_synonyms', [])))[:8],
            'obsolete': obsolete}


class EdamVocabulary:
    def __init__(self, scope, branch=''):
        check_scope(scope)
        if branch:
            check_uri(branch, scope)
        self.scope = scope
        try:
            self.validator = OntologyValidator('EDAM_' + scope)
            self.revision = digest({'scope': scope, 'current': self.validator.EDAM_Ontology,
                                    'obsolete': self.validator.EDAM_Obsolete})
            root = self.validator.EDAM_Ontology
            if branch:
                root = next((node for node in nodes(root) if node['data']['uri'] == branch), None)
                if root is None:
                    raise ValueError('Unknown EDAM branch.')
            self.current = {node['data']['uri']: node for node in nodes(root)}
            self.obsolete = {node['data']['uri']: node for node in nodes(self.validator.EDAM_Obsolete)
                             if node['data']['uri'].startswith('http://edamontology.org/' + scope + '_')} if not branch else {}
        except (Ontology.DoesNotExist, Ontology.MultipleObjectsReturned, DatabaseError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise EdamUnavailable('EDAM terms are temporarily unavailable.') from exc

    def resolve(self, identifiers, multiple=True):
        if not isinstance(identifiers, list) or len(identifiers) > (LIMIT if multiple else 1):
            raise ValueError('Choose at most 20 terms.' if multiple else 'Choose one term only.')
        for uri in identifiers:
            check_uri(uri, self.scope)
        resolved = []
        for uri in dict.fromkeys(identifiers):
            node = self.current.get(uri) or self.obsolete.get(uri)
            if node is None:
                raise ValueError('Unknown EDAM identifier or identifier outside the permitted branch.')
            # Resolve IDs only: stale or manipulated client labels never enter the validator.
            try:
                self.validator(uri, None)
            except ValidationError as exc:
                raise ValueError('Invalid EDAM identifier.') from exc
            resolved.append({**term(node, uri in self.obsolete), 'term': self.validator.get_term()})
        return resolved

    def search(self, query, suggestions):
        suggested = self.resolve(suggestions)
        words = query.casefold().split()
        def matches(node):
            text = ' '.join([node['text'], node['data']['uri'], *node.get('exact_synonyms', []), *node.get('narrow_synonyms', [])]).casefold()
            return all(word in text for word in words)
        choices = [node for node in self.current.values() if matches(node)]
        choices.sort(key=lambda node: (node['data']['uri'] not in suggestions,
                                      node['text'].casefold() != query.casefold(), node['text'].casefold(), node['data']['uri']))
        return {'items': [term(node) for node in choices[:LIMIT]], 'more': len(choices) > LIMIT,
                'suggestions': suggested}
