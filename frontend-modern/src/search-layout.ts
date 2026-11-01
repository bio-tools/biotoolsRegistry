export const layoutKey = 'biotools.search.columns.v1';
export interface Column { key: string; visible: boolean; width: number }
const defaults = ['name', 'description', 'toolType', 'additionDate', 'lastUpdate'];

export function defaultColumns(fields: Record<string, string>): Column[] {
  return Object.keys(fields).map(key => ({ key, visible: defaults.includes(key), width: key === 'description' ? 320 : 180 }));
}

export function readColumns(fields: Record<string, string>, saved: string | null, legacy: string | null): Column[] {
  const fallback = defaultColumns(fields);
  if (!saved && !legacy) return fallback;
  const value = JSON.parse((saved || legacy)!);
  const entries = saved ? value : value?.columns;
  if (!Array.isArray(entries)) throw new Error('Invalid saved columns');
  const result: Column[] = [];
  const normalized = (key: string) => key.toLowerCase().replace(/[^a-z0-9]/g, '');
  for (const item of entries) {
    if (!item || typeof item !== 'object') throw new Error('Invalid saved column');
    const name = saved ? item.key : item.name;
    if (typeof name !== 'string') throw new Error('Invalid column name');
    // Older UI-grid columns used field names; repeated function columns now share one cell.
    const legacyFunctions: Record<string, string> = { function: 'function.operation', function2: 'function.input', function3: 'function.output' };
    const legacyName = !saved ? (legacyFunctions[name] || name) : name;
    const key = Object.keys(fields).find(key => normalized(key) === normalized(legacyName));
    if (!key) continue;
    const previous = result.find(column => column.key === key);
    if (previous) { previous.visible ||= item.visible !== false; continue; }
    result.push({ key, visible: key === 'name' || item.visible !== false,
      width: typeof item.width === 'number' && Number.isFinite(item.width) ? Math.max(120, Math.min(800, item.width)) : 180 });
  }
  if (!result.length) throw new Error('No supported saved columns');
  return [...result, ...fallback.filter(column => !result.some(item => item.key === column.key)).map(column => ({ ...column, visible: column.key === 'name' }))];
}
