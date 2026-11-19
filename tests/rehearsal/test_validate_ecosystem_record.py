import unittest

from validate_ecosystem_record import errors


SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'array', 'items': {'$ref': '#/definitions/tool'},
    'definitions': {'tool': {'type': 'object', 'properties': {
        'name': {'type': 'string', 'minLength': 1}, 'homepage': {'type': 'string'},
    }, 'required': ['name', 'homepage'], 'additionalProperties': False}},
}


class EcosystemValidationTests(unittest.TestCase):
    def test_accepts_known_registry_metadata(self):
        self.assertEqual(errors(SCHEMA, {'name': 'Tool', 'homepage': 'https://example.org', 'owner': 'editor'}), [])

    def test_rejects_missing_schema_fields_and_unknown_fields(self):
        self.assertTrue(errors(SCHEMA, {'homepage': 'https://example.org'}))
        self.assertTrue(errors(SCHEMA, {'name': 'Tool', 'homepage': 'https://example.org', 'typo': True}))

    def test_accepts_duplicate_values_in_upstream_enum(self):
        schema = {**SCHEMA, 'definitions': {'tool': {**SCHEMA['definitions']['tool'],
            'properties': {'name': {'enum': ['Tool', 'Tool']}, 'homepage': {'type': 'string'}}}}}
        self.assertEqual(errors(schema, {'name': 'Tool', 'homepage': 'https://example.org'}), [])

    def test_registry_metadata_is_validated_if_schema_adds_it(self):
        schema = {**SCHEMA, 'definitions': {'tool': {**SCHEMA['definitions']['tool'],
            'properties': {**SCHEMA['definitions']['tool']['properties'], 'owner': {'type': 'integer'}}}}}
        self.assertTrue(errors(schema, {'name': 'Tool', 'homepage': 'https://example.org', 'owner': 'editor'}))


if __name__ == '__main__':
    unittest.main()
