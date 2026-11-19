"""Translate a bounded, explicit Boolean search into existing search clauses."""
import re

from elixir.search_settings import search_struct


def boolean_query(text, build_clause):
    if len(text) > 256:
        raise ValueError('Boolean searches are limited to 256 characters.')
    tokens = re.findall(r'"[^"\\]*"|[()]|:|[^\s():"\\]+', text)
    if re.sub(r'"[^"\\]*"|[()]|:|[^\s():"\\]+|\s+', '', text) or len(tokens) > 64 or re.search(r'[\x00-\x1f\x7f]', text):
        raise ValueError('Invalid or too complex Boolean search.')
    position = 0

    def parse_expression(depth=0):
        nonlocal position
        if depth > 16:
            raise ValueError('Boolean search is nested too deeply.')

        def atom():
            nonlocal position
            if position >= len(tokens):
                raise ValueError('Expected a search term.')
            token = tokens[position]
            position += 1
            if token == 'NOT':
                return {'bool': {'must_not': [atom()]}}
            if token == '(':
                value = parse_expression(depth + 1)
                if position >= len(tokens) or tokens[position] != ')':
                    raise ValueError('Missing closing parenthesis.')
                position += 1
                return value
            if token in ('AND', 'OR', ')', ':'):
                raise ValueError('Expected a search term.')
            field = None
            if position < len(tokens) and tokens[position] == ':':
                field = token
                if field not in search_struct:
                    raise ValueError('Unknown search field: ' + field)
                position += 1
                if position >= len(tokens) or tokens[position] in ('AND', 'OR', 'NOT', '(', ')', ':'):
                    raise ValueError('Expected a field value.')
                token = tokens[position]
                position += 1
            phrase = token.startswith('"') and token.endswith('"')
            value = token[1:-1] if phrase else token
            if not re.search(r'\w', value):
                raise ValueError('Include a searchable word or identifier.')
            return build_clause(field, value, phrase)

        def conjunction():
            nonlocal position
            values = [atom()]
            while position < len(tokens) and tokens[position] == 'AND':
                position += 1
                values.append(atom())
            return values[0] if len(values) == 1 else {'bool': {'must': values}}

        values = [conjunction()]
        while position < len(tokens) and tokens[position] == 'OR':
            position += 1
            values.append(conjunction())
        return values[0] if len(values) == 1 else {'bool': {'should': values, 'minimum_should_match': 1}}

    result = parse_expression()
    if position != len(tokens):
        raise ValueError('Use AND or OR between search terms.')
    return result
