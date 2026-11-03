import { expect, it } from 'vitest';
import { fieldIcon, sectionIcon } from './ui-icons';

it('uses field shapes and optional section decorations without depending on vocabulary values', () => {
  expect(fieldIcon('boolean')).toBe('boolean');
  expect(fieldIcon('string', true)).toBe('choice');
  expect(sectionIcon('publication', 'array')).toBe('publication');
  expect(sectionIcon('newSchemaField', 'array')).toBe('array');
  expect(sectionIcon('toString', 'string')).toBe('string');
  expect(fieldIcon('future-kind')).toBe('object');
});
