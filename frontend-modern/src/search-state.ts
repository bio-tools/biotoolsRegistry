import { parseAdvanced, type AdvancedFilter, type FilterValues, type ScoreDefinition } from './advanced-filters';

export interface SearchFilterGroup {
  id: string;
  label: string;
  keys: string[];
  children: SearchFilterGroup[];
}

export interface SearchConfig {
  endpoint: string;
  filters: Record<string, string>;
  filterChoices?: Record<string, { value: string; label: string }[]>;
  filterGroups?: SearchFilterGroup[];
  schemaRevision?: string;
  sorts: Record<string, string>;
  pageSizes: number[];
  maxWindow: number;
  scores?: ScoreDefinition[];
  edamEndpoint?: string;
  comparisonFields?: Record<string, string>;
}

export interface SearchState {
  q: string;
  sort: string;
  ord: 'asc' | 'desc';
  page: number;
  per_page: number;
  filters: Record<string, string>;
  advanced: AdvancedFilter[];
  view: 'cards' | 'table';
}

export function defaultState(): SearchState {
  return { q: '', sort: 'lastUpdate', ord: 'desc', page: 1, per_page: 50, filters: {}, advanced: [], view: 'cards' };
}

export function parseSearch(search: string, config: SearchConfig): SearchState {
  const params = new URLSearchParams(search);
  const allowed = new Set(['q', 'sort', 'ord', 'page', 'per_page', 'advanced', 'view', ...Object.keys(config.filters)]);
  for (const key of params.keys()) {
    if (!allowed.has(key)) throw new Error(`Unsupported search parameter: ${key}`);
  }
  // Django QueryDict and the public search use the last repeated value.
  for (const key of new Set(params.keys())) params.set(key, params.getAll(key).at(-1)!);
  const state = defaultState();
  const view = params.get('view') ?? 'cards';
  if (!['cards', 'table'].includes(view)) throw new Error('Choose cards or table.');
  state.view = view as SearchState['view'];
  for (const key of ['page', 'per_page'] as const) {
    const value = params.get(key) ?? String(state[key]);
    if (!/^[0-9]{1,5}$/.test(value) || Number(value) < 1) throw new Error(`Invalid ${key}. Use a positive whole number.`);
    state[key] = Number(value);
  }
  if (!config.pageSizes.includes(state.per_page)) throw new Error('Choose 10, 25, 50 or 100 results per page.');
  if (state.page * state.per_page > config.maxWindow) throw new Error('Narrow the search to browse beyond 10,000 results.');
  state.sort = params.get('sort') ?? state.sort;
  const order = params.get('ord') ?? state.ord;
  if (!Object.hasOwn(config.sorts, state.sort) || !['asc', 'desc'].includes(order)) throw new Error('Choose a supported sort and direction.');
  state.ord = order as SearchState['ord'];
  for (const key of ['q', ...Object.keys(config.filters)]) {
    const value = (params.get(key) ?? '').trim();
    if (value.length > 256 || /[\x00-\x1f\x7f\\]/.test(value)) throw new Error(`Invalid ${key}: use at most 256 characters without control characters or backslashes.`);
    if (value && key !== 'domain' && !/[\p{L}\p{N}_]/u.test(value)) throw new Error(`Invalid ${key}: include a searchable word or identifier.`);
    if (key === 'q') state.q = value;
    else if (value) state.filters[key] = value;
  }
  state.advanced = parseAdvanced(params.get('advanced') ?? '[]', config.scores);
  return state;
}

export function serializeSearch(state: SearchState): string {
  const params = new URLSearchParams();
  if (state.q.trim()) params.set('q', state.q.trim());
  for (const key of Object.keys(state.filters).sort()) {
    if (state.filters[key].trim()) params.set(key, state.filters[key].trim());
  }
  if (state.sort !== 'lastUpdate') params.set('sort', state.sort);
  if (state.ord !== 'desc') params.set('ord', state.ord);
  if (state.per_page !== 50) params.set('per_page', String(state.per_page));
  if (state.page !== 1) params.set('page', String(state.page));
  if (state.advanced.length) params.set('advanced', JSON.stringify(state.advanced));
  if (state.view === 'table') params.set('view', 'table');
  return params.toString();
}

export interface ToolSummary {
  id: string; name: string; description: string; url: string;
  toolTypes: string[]; topics: string[]; operations: string[]; added: string; updated: string;
  filterValues?: FilterValues;
  comparison?: Record<string, string>;
}

export interface SearchResponse {
  items: ToolSummary[];
  count: number;
  scores?: ScoreDefinition[];
  candidates?: { scope: 'candidate'; size: number; limit: number; complete: boolean };
  facets: Record<string, { values: { value: string; count: number }[]; truncated: boolean }>;
  pagination: { page: number; perPage: number; pages: number; next: number | null; previous: number | null; limited: boolean };
}
