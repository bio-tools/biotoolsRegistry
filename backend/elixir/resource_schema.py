"""Read the selected local XSD as metadata, not as a replacement JSON validator."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

from defusedxml import ElementTree
from lxml import etree


XS = '{http://www.w3.org/2001/XMLSchema}'
SUPPORTED = {'schema', 'element', 'annotation', 'documentation', 'appinfo', 'complexType',
             'simpleType', 'sequence', 'choice', 'complexContent', 'restriction',
             'enumeration', 'pattern', 'whiteSpace', 'maxLength', 'minLength',
             'minInclusive', 'maxInclusive'}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def label(name):
    return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', name).replace('_', ' ').capitalize()


def ingest(path, version):
    content = Path(path).read_bytes()
    root = ElementTree.fromstring(content)
    if root.tag != XS + 'schema':
        raise ValueError('Expected an XML Schema document.')
    for node in root.iter():
        if node.tag.startswith(XS) and node.tag[len(XS):] not in SUPPORTED:
            raise ValueError('Unsupported schema construct: ' + node.tag)
        if node.tag in {XS + 'sequence', XS + 'choice'} and node.attrib:
            raise ValueError('Group cardinality requires an explicit JSON mapping.')
        if node.tag == XS + 'element' and set(node.attrib) - {'name', 'ref', 'type', 'minOccurs', 'maxOccurs'}:
            raise ValueError('Unsupported element attributes: ' + str(node.attrib))
    try:
        etree.XMLSchema(etree.fromstring(content, etree.XMLParser(resolve_entities=False, no_network=True)))
    except etree.XMLSchemaParseError as exc:
        raise ValueError('Invalid XML Schema: ' + str(exc)) from exc
    definitions = {node.get('name'): node for node in root if node.get('name')}

    def annotation(node):
        result = {}
        for child in node.findall(XS + 'annotation'):
            for item in [*child.findall(XS + 'documentation'), *child.findall(XS + 'appinfo/*')]:
                name = item.tag.split('}')[-1]
                text = ' '.join(''.join(item.itertext()).split())
                if name == 'uiLabel':
                    result['label'] = text
                elif name == 'uiTip':
                    result['help'] = text
                elif name == 'documentation':
                    result.setdefault('help', text)
        return result

    def named(name, stack):
        if name.startswith('xs:'):
            primitive = name[3:]
            if primitive not in {'string', 'token', 'anyURI', 'integer', 'decimal', 'boolean', 'dateTime'}:
                raise ValueError('Unsupported primitive: ' + name)
            return {'kind': 'boolean' if primitive == 'boolean' else
                    'number' if primitive in {'integer', 'decimal'} else 'string'}
        name = name.split(':')[-1]
        if name in stack or name not in definitions:
            raise ValueError('Unresolved or recursive schema type: ' + name)
        return shape(definitions[name], (*stack, name))

    def shape(node, stack=()):
        if node.tag == XS + 'element':
            reference = node.get('ref')
            if reference:
                result = named(reference, stack)
            elif node.get('type'):
                result = named(node.get('type'), stack)
            else:
                child = next((item for item in node if item.tag in {XS + 'simpleType', XS + 'complexType'}), None)
                if child is None:
                    raise ValueError('Element without a supported type: ' + str(node.get('name')))
                result = shape(child, stack)
            result = deepcopy(result)
            metadata = annotation(node)
            result.update(metadata)
            result['explicitLabel'] = 'label' in metadata or result.get('explicitLabel', False)
            result.setdefault('label', label(node.get('name') or reference))
            result['required'] = node.get('minOccurs', '1') != '0'
            maximum = node.get('maxOccurs', '1')
            if maximum != '1':
                result = {'kind': 'array', 'item': result, 'label': result['label'],
                          'explicitLabel': result['explicitLabel'],
                          'help': result.get('help', ''), 'required': result['required'],
                          'minItems': int(node.get('minOccurs', '1')),
                          'maxItems': None if maximum == 'unbounded' else int(maximum)}
            return result
        restriction = node.find(XS + 'restriction')
        if restriction is not None and node.tag == XS + 'simpleType':
            result = named(restriction.get('base'), stack)
            enums = restriction.findall(XS + 'enumeration')
            if enums:
                if result['kind'] != 'string':
                    raise ValueError('Non-string enumerations need an explicit JSON mapping.')
                result['choices'] = [{'value': item.get('value'),
                                      'label': annotation(item).get('label', item.get('value'))} for item in enums]
            for key in ('minLength', 'maxLength', 'minInclusive', 'maxInclusive'):
                item = restriction.find(XS + key)
                if item is not None:
                    result[key] = int(item.get('value'))
            patterns = restriction.findall(XS + 'pattern')
            if patterns:
                result['patterns'] = [item.get('value') for item in patterns]
            return {**result, **annotation(node)}
        result = {'kind': 'object', 'fields': {}}

        def members(parent, choice=False):
            for item in parent:
                if item.tag == XS + 'element':
                    name = item.get('name') or item.get('ref').split(':')[-1]
                    field = shape(item, stack)
                    if choice:
                        field['required'] = False
                        field['choiceGroup'] = True
                    previous = result['fields'].get(name)
                    if previous and previous['kind'] != field['kind']:
                        raise ValueError('Ambiguous choice field: ' + name)
                    # Choice alternatives may repeat a field with less documentation.
                    result['fields'][name] = previous or field
                elif item.tag in {XS + 'sequence', XS + 'choice', XS + 'complexContent', XS + 'restriction'}:
                    members(item, choice or item.tag == XS + 'choice')
        members(node)
        if not result['fields']:
            raise ValueError('Empty or unsupported complex type: ' + str(node.get('name')))
        return {**result, **annotation(node)}

    if 'tool' not in definitions:
        raise ValueError('The selected schema has no tool element.')
    return {'version': version, 'sha256': sha256(content).hexdigest(),
            'artifact': Path(path).name, 'fields': shape(definitions['tool'])['fields']}


def flatten(field, path=''):
    """Stable JSON paths omit array indices; item cardinality stays in the node."""
    result = {path: field} if path else {}
    item = field.get('item', field)
    for name, child in item.get('fields', {}).items():
        result.update(flatten(child, '.'.join(filter(None, (path, name)))))
    return result
