"""Effective UI contract: selected schema metadata plus explicit registry policy."""
from collections.abc import Mapping
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from defusedxml.common import DefusedXmlException
from xml.etree.ElementTree import ParseError

from django.conf import settings

from elixir.resource_schema import digest, flatten, ingest, label


DIRECTORY = Path(__file__).parent / 'biotoolsSchema'


class SchemaUnavailable(ValueError):
    pass


@lru_cache(maxsize=8)
def sources(schema_path, policy_path, version):
    try:
        schema = ingest(schema_path, version)
        policy = json.loads(Path(policy_path).read_text())
        if not isinstance(policy, dict) or policy.get('version') != 1:
            raise ValueError('Unsupported registry policy.')
        for key in ('registryPaths', 'writePaths', 'publicPaths'):
            if not isinstance(policy.get(key), list) or not all(isinstance(path, str) for path in policy[key]):
                raise ValueError('Invalid registry policy: ' + key)
        for key in ('extraChoices', 'excludedChoices', 'search'):
            if not isinstance(policy.get(key), dict) or not all(isinstance(values, list) and all(isinstance(value, str) for value in values) for values in policy[key].values()):
                raise ValueError('Invalid registry policy: ' + key)
        if not isinstance(policy.get('presentation', {}), dict) or not all(isinstance(value, dict) for value in policy.get('presentation', {}).values()):
            raise ValueError('Invalid registry presentation policy.')
        return schema, policy
    except (OSError, ValueError, KeyError, ParseError, DefusedXmlException) as exc:
        raise SchemaUnavailable('Resource schema metadata is unavailable.') from exc


def selected_sources():
    schema, policy = sources(str(getattr(settings, 'RESOURCE_SCHEMA_PATH', DIRECTORY / 'biotools_3.3.0-singletool.xsd')),
                             str(getattr(settings, 'RESOURCE_UI_POLICY_PATH', DIRECTORY / 'registry-ui-policy.json')),
                             getattr(settings, 'RESOURCE_SCHEMA_VERSION', '3.3.0'))
    approved = approved_descriptor()
    if approved.get('schema') != {key: value for key, value in schema.items() if key != 'fields'} or approved.get('policyRevision') != digest(policy):
        raise SchemaUnavailable('Resource schema sources have not passed descriptor activation checks.')
    return schema, policy


@lru_cache(maxsize=8)
def read_descriptor(path):
    try:
        value = json.loads(Path(path).read_text())
        if not isinstance(value, dict) or value.get('protocol') != 1:
            raise ValueError('Unsupported descriptor protocol.')
        return value
    except (OSError, ValueError) as exc:
        raise SchemaUnavailable('Approved resource descriptor is unavailable.') from exc


def approved_descriptor():
    return read_descriptor(str(getattr(settings, 'RESOURCE_UI_DESCRIPTOR_PATH', DIRECTORY / 'resource-ui.generated.json')))


def options(schema, policy):
    if policy.get('version') != 1:
        raise SchemaUnavailable('Unsupported registry policy version.')
    result = {}
    for path, field in flatten({'fields': schema['fields']}).items():
        values = field.get('item', field).get('choices')
        if values is not None:
            excluded = set(policy['excludedChoices'].get(path, []))
            result[path] = [item for item in values if item['value'] not in excluded]
    for path, values in policy['extraChoices'].items():
        if path not in result:
            raise SchemaUnavailable('Registry choice extension has no schema field: ' + path)
        known = {item['value'] for item in result[path]}
        result[path] += [{'value': value, 'label': value} for value in values if value not in known]
    if set(policy['excludedChoices']) - set(result):
        raise SchemaUnavailable('Registry choice exclusion has no schema enum field.')
    return result


class SchemaChoices(Mapping):
    """Validators resolve the same selected source as UI metadata, including tests."""
    def __getitem__(self, path):
        return [item['value'] for item in options(*selected_sources())[path]]

    def __iter__(self):
        return iter(options(*selected_sources()))

    def __len__(self):
        return len(options(*selected_sources()))


def build_descriptor(schema, policy, contract=None):
    if contract is None:
        from elixir.editor_contract import resource_contract
        contract = resource_contract(constraints=True)
    fields = flatten(contract)
    schema_fields = flatten({'fields': schema['fields']})
    missing = set(schema_fields) - set(fields)
    if missing:
        raise SchemaUnavailable('Schema fields lack backend support: ' + ', '.join(sorted(missing)))
    registry = set(policy['registryPaths'])
    unknown = set(fields) - set(schema_fields) - registry
    if unknown:
        raise SchemaUnavailable('Unclassified registry fields: ' + ', '.join(sorted(unknown)))
    approved = set(policy['writePaths']) | set(policy['publicPaths'])
    if approved - set(fields):
        raise SchemaUnavailable('Policy names fields absent from the backend.')
    choices = options(schema, policy)
    result = deepcopy(contract)
    for path, field in flatten(result).items():
        source = schema_fields.get(path, {})
        if source and source['kind'] != field['kind']:
            raise SchemaUnavailable('Schema/backend type mismatch: ' + path)
        if source and source.get('item', {}).get('kind') != field.get('item', {}).get('kind'):
            raise SchemaUnavailable('Schema/backend array item mismatch: ' + path)
        hint = policy.get('presentation', {}).get(path, {})
        field.update(path=path, label=source.get('label') if source.get('explicitLabel') else
                     hint.get('label', source.get('label', label(path.split('.')[-1]))),
                     help=source.get('help', ''), public=path in policy['publicPaths'],
                     writable=path in policy['writePaths'] and not field['readOnly'],
                     search=policy.get('search', {}).get(path, []))
        allowed_hints = {'label', 'itemLabel', 'multiline', 'section'}
        if set(hint) - allowed_hints:
            raise SchemaUnavailable('Unsupported presentation hint: ' + path)
        field.update({key: value for key, value in hint.items() if key != 'label'})
        for target, origin in ((field, source), (field.get('item', {}), source.get('item', {}))):
            for key in ('required', 'minLength', 'maxLength', 'minInclusive', 'maxInclusive', 'minItems', 'maxItems', 'patterns', 'choiceGroup'):
                if key in origin:
                    target['schema' + key[0].upper() + key[1:]] = origin[key]
        if path in choices:
            field['choices'] = choices[path]
    descriptor = {'protocol': 1, 'schema': {key: value for key, value in schema.items() if key != 'fields'},
                  'policyRevision': digest(policy), 'contract': result,
                  'removedValuePolicy': 'correction-required'}
    descriptor['revision'] = digest(descriptor)
    return descriptor


def resource_descriptor():
    try:
        result = build_descriptor(*selected_sources())
    except (ValueError, KeyError, TypeError) as exc:
        raise SchemaUnavailable('Resource schema/backend metadata could not be verified.') from exc
    if result != approved_descriptor():
        raise SchemaUnavailable('Resource serializer changed without a reviewed descriptor update.')
    return result


def public_fields(value, contract, *, handled=()):
    """Project approved public values; absent/unknown/private fields never leak."""
    result = []
    if not isinstance(value, dict):
        return result
    for name, field in contract.get('fields', {}).items():
        item = value.get(name)
        if not field.get('public') or field['path'] in handled or item is None or item == '' or item == []:
            continue
        node = {'name': name, 'path': field['path'], 'label': field['label'], 'kind': field['kind'], 'value': item}
        if field['path'] == 'otherID.value':
            node['identifierType'] = value.get('type')
        shape = field.get('item', field)
        if shape['kind'] == 'object':
            entries = item if field['kind'] == 'array' and isinstance(item, list) else [item]
            node['entries'] = [children for entry in entries if (children := public_fields(entry, shape, handled=handled))]
            if not node['entries']:
                continue
        else:
            labels = {choice['value']: choice['label'] for choice in field.get('choices', [])}
            values = item if isinstance(item, list) else [item]
            node['values'] = [{'value': entry, 'label': labels.get(entry, entry)} for entry in values if not isinstance(entry, (dict, list))]
        result.append(node)
    return result


def search_metadata(descriptor, supported):
    from elixir.search_settings import search_struct

    fields = flatten(descriptor['contract'])
    metadata = {name: {'label': field['label'], 'choices': field.get('choices', [])}
                for field in fields.values() if field['public']
                for name in field['search'] if name in supported}
    if set(metadata) != set(supported):
        raise SchemaUnavailable('Search capabilities do not match supported query fields.')
    repeated = {item['label'] for item in metadata.values()
                if sum(other['label'] == item['label'] for other in metadata.values()) > 1}
    for name, item in metadata.items():
        if item['label'] not in repeated:
            continue
        paths = []
        for path in search_struct.get(name, {}).get('search_field', []):
            path = path.removesuffix('.raw').removesuffix('.term')
            parts = path.split('.')
            title = ' › '.join(fields['.'.join(parts[:index])]['label'] for index in range(1, len(parts) + 1)
                               if '.'.join(parts[:index]) in fields)
            if title and title not in paths:
                paths.append(title)
        if paths:
            item['label'] = ' / '.join(paths)
    return metadata


def compatibility(previous, candidate):
    """Never infer semantic aliases or silently migrate saved wire identifiers."""
    if previous.get('protocol') != candidate.get('protocol'):
        return ['Descriptor protocol changed.']
    before, after = flatten(previous['contract']), flatten(candidate['contract'])
    errors = []
    for path, old in before.items():
        new = after.get(path)
        if new is None:
            errors.append(path + ': removed/renamed field needs a migration.')
            continue
        for key in ('kind', 'nullable', 'empty', 'blank', 'readOnly', 'writable', 'public'):
            if old.get(key) != new.get(key):
                errors.append(path + ': changed ' + key + ' needs review.')
        if ((new.get('required') and not old.get('required')) or
                (new.get('schemaRequired') and not old.get('schemaRequired'))):
            errors.append(path + ': new required constraint needs a default/migration.')
        old_item, new_item = old.get('item', {}), new.get('item', {})
        if old_item.get('kind') != new_item.get('kind'):
            errors.append(path + ': changed array item type needs a migration.')
        for key in ('nullable', 'blank', 'empty', 'readOnly'):
            if old_item.get(key) != new_item.get(key):
                errors.append(path + ': changed array item ' + key + ' needs review.')
        for key in ('minLength', 'maxLength', 'minimum', 'maximum',
                    'schemaMinItems', 'schemaMaxItems', 'schemaMinLength', 'schemaMaxLength',
                    'schemaMinInclusive', 'schemaMaxInclusive', 'schemaPatterns', 'schemaChoiceGroup'):
            if old.get(key) != new.get(key) or old_item.get(key) != new_item.get(key):
                errors.append(path + ': changed schema constraint needs backend review.')
        old_values = {item['value'] for item in old.get('choices', [])}
        new_values = {item['value'] for item in new.get('choices', [])}
        if old_values - new_values and new_values - old_values:
            errors.append(path + ': simultaneous value removal/addition may be a wire-ID rename; migrate explicitly.')
    for path in after.keys() - before.keys():
        if after[path].get('required') or after[path].get('schemaRequired'):
            errors.append(path + ': required addition needs a migration.')
    return errors
