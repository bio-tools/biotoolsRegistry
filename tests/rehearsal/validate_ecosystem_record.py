"""Validate an RSEc tool record against an explicitly supplied bio.tools JSON schema."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft4Validator


REGISTRY_METADATA = {
    'additionDate', 'confidence_flag', 'editPermission', 'elixir_badge',
    'homepage_status', 'lastUpdate', 'owner', 'validated',
}


def errors(schema, record):
    if not isinstance(record, dict):
        return ['A tool record must be a JSON object.']
    schema = deepcopy(schema)
    def normalize_enums(node):
        if isinstance(node, dict):
            if isinstance(node.get('enum'), list):
                # The official schema has duplicate license values; JSON Schema requires unique enums.
                unique = {}
                for value in node['enum']:
                    unique.setdefault(json.dumps(value, sort_keys=True), value)
                node['enum'] = list(unique.values())
            for value in node.values():
                normalize_enums(value)
        elif isinstance(node, list):
            for value in node:
                normalize_enums(value)
    normalize_enums(schema)
    schema_fields = schema['definitions']['tool']['properties']
    record = {key: value for key, value in record.items()
              if key not in REGISTRY_METADATA or key in schema_fields}
    Draft4Validator.check_schema(schema)
    return [f"{'/'.join(map(str, error.absolute_path))}: {error.message}"
            for error in Draft4Validator(schema).iter_errors([record])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('schema', type=Path, help='Official bio.tools JSON schema file')
    parser.add_argument('record', type=Path, help='One exported .biotools.json record')
    args = parser.parse_args()
    with args.schema.open() as file:
        schema = json.load(file)
    with args.record.open() as file:
        record = json.load(file)
    problems = errors(schema, record)
    for problem in problems:
        print(problem)
    if problems:
        raise SystemExit(1)
    print('Record conforms to the supplied bio.tools schema.')


if __name__ == '__main__':
    main()
