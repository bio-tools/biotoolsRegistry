import { describe, expect, it } from 'vitest';
import { defaultColumns, readColumns } from './search-layout';

const fields = { name: 'Name', description: 'Description', homepage: 'Homepage', function: 'Functions', 'function.operation': 'Operations', 'function.input': 'Inputs', operatingSystem: 'Operating systems' };
describe('saved comparison layout', () => {
  it('migrates legacy visibility, order and widths without relying on translated labels', () => {
    const result = readColumns(fields, null, JSON.stringify({ columns: [
      { name: 'homepage', width: 240, visible: true }, { name: 'operating system', width: 160, visible: false },
      { name: 'function', width: 300, visible: false }, { name: 'function2', width: 250, visible: true },
      { name: 'name', visible: false }, { name: 'removed', visible: true },
    ] }));
    expect(result.map(column => column.key)).toEqual(['homepage', 'operatingSystem', 'function.operation', 'function.input', 'name', 'description', 'function']);
    expect(result[0]).toEqual({ key: 'homepage', visible: true, width: 240 });
    expect(result[1].visible).toBe(false);
    expect(result[2].visible).toBe(false);
    expect(result[3].visible).toBe(true);
    expect(result.find(column => column.key === 'name')?.visible).toBe(true);
    expect(readColumns(fields, JSON.stringify(result), '{broken')).toEqual(result);
  });
  it('adapts to new schema fields, bounds widths and rejects unusable storage', () => {
    expect(readColumns(fields, null, null)).toEqual(defaultColumns(fields));
    const result = readColumns({ ...fields, newField: 'New label' }, JSON.stringify([{ key: 'homepage', visible: true, width: 9999 }]), null);
    expect(result[0].width).toBe(800);
    expect(result.at(-1)).toEqual({ key: 'newField', visible: false, width: 180 });
    for (const value of ['{broken', '{}', '[null]', '[{"key":"unknown"}]']) {
      expect(() => readColumns(fields, value, null)).toThrow();
    }
  });
});
