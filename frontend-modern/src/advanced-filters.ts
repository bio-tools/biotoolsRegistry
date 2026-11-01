export type FilterScope = 'candidate' | 'server';
export type AdvancedFilter = { scope: FilterScope } & (
  { type: 'boolean'; field: 'hasPublication'; value: boolean } |
  { type: 'range'; field: 'added'; min?: string; max?: string } |
  { type: 'categorical'; field: 'toolType'; values: string[] } |
  { type: 'ontology'; field: 'topic'; values: string[] } |
  { type: 'score'; field: string; version: string; min?: number; max?: number }
);
export interface ScoreDefinition { key: string; label: string; version: string; min: number; max: number }
export interface FilterValues {
  hasPublication: boolean; added: string; toolType: string[]; topic: string[]; scores: Record<string, number>;
}

function validDate(value: unknown): value is string {
  if (typeof value !== 'string' || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value) || value < '0001-01-01' || value >= '9999-12-31') return false;
  const date = new Date(`${value}T00:00:00Z`);
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
}

export function parseAdvanced(raw: string, scores: ScoreDefinition[] = [], scope: FilterScope = 'server'): AdvancedFilter[] {
  const fail = () => { throw new Error('Invalid advanced filters: use supported fields, bounds and score versions.'); };
  if (new TextEncoder().encode(raw).length > 4096) return fail();
  let filters: unknown;
  try { filters = JSON.parse(raw); } catch { return fail(); }
  if (!Array.isArray(filters) || filters.length > 8) return fail();
  return filters.map(filter => {
    if (!filter || typeof filter !== 'object' || Array.isArray(filter) || filter.scope !== scope) return fail();
    let keys = ['type', 'field', 'scope'];
    if (filter.type === 'boolean' && filter.field === 'hasPublication') {
      keys.push('value');
      if (typeof filter.value !== 'boolean') return fail();
    } else if ((filter.type === 'categorical' && filter.field === 'toolType') || (filter.type === 'ontology' && filter.field === 'topic')) {
      keys.push('values');
      if (!Array.isArray(filter.values) || !filter.values.length || filter.values.length > 10 || filter.values.some((value: unknown) =>
        typeof value !== 'string' || !value.length || value.length > 256 || /[\x00-\x1f\x7f]/.test(value) ||
        (filter.type === 'ontology' && !/^http:\/\/edamontology.org\/topic_[0-9]{4}$/.test(value)))) return fail();
      filter.values = [...new Set(filter.values)].sort();
    } else if ((filter.type === 'range' && filter.field === 'added') || filter.type === 'score') {
      keys.push('min', 'max');
      const bounds = ['min', 'max'].filter(key => Object.hasOwn(filter, key)).map(key => filter[key]);
      if (!bounds.length) return fail();
      if (filter.type === 'range') {
        if (!bounds.every(validDate)) return fail();
      } else {
        keys.push('version');
        const score = scores.find(score => score.key === filter.field && score.version === filter.version);
        if (!score || bounds.some(value => typeof value !== 'number' || !Number.isFinite(value) || value < score.min || value > score.max)) return fail();
      }
      if (bounds.length === 2 && bounds[0] > bounds[1]) return fail();
    } else return fail();
    if (Object.keys(filter).some(key => !keys.includes(key))) return fail();
    return Object.fromEntries(Object.keys(filter).sort().map(key => [key, filter[key]])) as AdvancedFilter;
  });
}

export function matchesFilters(values: FilterValues | undefined, filters: AdvancedFilter[]): boolean {
  return filters.every(filter => {
    if (!values) return false;
    if (filter.type === 'boolean') return values.hasPublication === filter.value;
    if (filter.type === 'categorical' || filter.type === 'ontology') return filter.values.some(value => values[filter.field].includes(value));
    if (filter.type === 'range') return !!values.added && (filter.min === undefined || values.added >= filter.min) && (filter.max === undefined || values.added <= filter.max);
    const value = values.scores[filter.field];
    return Number.isFinite(value) && (filter.min === undefined || value >= filter.min) && (filter.max === undefined || value <= filter.max);
  });
}

export function filterLabel(filter: AdvancedFilter, scores: ScoreDefinition[] = []): string {
  if (filter.type === 'boolean') return filter.value ? 'Has publication' : 'No publication';
  if (filter.type === 'categorical' || filter.type === 'ontology') return `${filter.field === 'topic' ? 'Topic URI' : 'Tool type'}: ${filter.values.join(', ')}`;
  const label = filter.type === 'range' ? 'Added' : `${scores.find(score => score.key === filter.field)?.label || filter.field} (${filter.version})`;
  return `${label}: ${filter.min ?? 'any'} to ${filter.max ?? 'any'}`;
}
