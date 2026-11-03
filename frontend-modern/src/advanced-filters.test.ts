import { afterEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import fixtureJSON from '../../backend/elixirapp/tests/data/AdvancedSearch.json?raw';
import { matchesFilters, parseAdvanced, type AdvancedFilter, type FilterValues, type ScoreDefinition } from './advanced-filters';
import { defaultState, parseSearch, serializeSearch, type SearchConfig, type SearchResponse } from './search-state';
import SearchWorkspace from './SearchWorkspace.vue';

const fixture: { score: ScoreDefinition; cases: { filter: AdvancedFilter; ids: string[] }[];
  items: { biotoolsID: string; toolType: string[]; topic: { uri: string }[]; additionDate?: string;
    publication: Record<string, unknown>[]; fixtureQualityV1?: number | null }[] } = JSON.parse(fixtureJSON);
const config: SearchConfig = { endpoint: '/search/data/', filters: {}, sorts: { lastUpdate: 'Updated' },
  pageSizes: [10, 25, 50, 100], maxWindow: 10000, scores: [fixture.score] };
const values = (item: typeof fixture.items[number]): FilterValues => ({
  hasPublication: (item.publication ?? []).some((publication: Record<string, unknown>) => ['doi', 'pmid', 'pmcid'].some(key => publication[key] != null)),
  added: (item.additionDate ?? '').slice(0, 10), toolType: item.toolType, topic: item.topic.map((topic: {uri: string}) => topic.uri),
  scores: typeof item.fixtureQualityV1 === 'number' ? { fixtureQuality: item.fixtureQualityV1 } : {},
});
const body: SearchResponse = {
  items: fixture.items.map((item: typeof fixture.items[number]) => ({ id: item.biotoolsID, name: item.biotoolsID,
    description: 'Fixture', url: '/tool/' + item.biotoolsID, toolTypes: item.toolType.slice(0, 4),
    topics: [], operations: [], added: values(item).added, updated: '', filterValues: values(item) })),
  count: 125, facets: {}, candidates: { scope: 'candidate', size: 6, limit: 100, complete: false },
  scores: [fixture.score], pagination: { page: 1, perPage: 50, pages: 3, previous: null, next: 2, limited: false },
};
let wrapper: VueWrapper | undefined;
afterEach(() => {
  wrapper?.unmount(); wrapper = undefined; vi.useRealTimers(); vi.unstubAllGlobals(); vi.restoreAllMocks();
  history.replaceState(null, '', '/');
});

describe('structured filters', () => {
  it.each(fixture.cases)('matches shared server fixtures: $filter.type $filter.field $filter.value', (entry: {filter: AdvancedFilter; ids: string[]}) => {
    const filter = parseAdvanced(JSON.stringify([entry.filter]), config.scores);
    expect(body.items.filter(item => matchesFilters(item.filterValues, filter)).map(item => item.id)).toEqual(entry.ids);
    const state = { ...defaultState(), advanced: filter };
    expect(parseSearch(serializeSearch(state), config)).toEqual(state);
  });

  it('rejects invalid fields, operators, scopes, dates, score versions and bounds', () => {
    const range = { scope: 'server', type: 'range', field: 'added', min: '2026-01-01' };
    const invalid = [null, {}, [null], [1], [range, ...Array(8).fill(range)],
      [{ ...range, field: 'anything' }], [{ ...range, scope: 'candidate' }], [{ ...range, operator: 'script' }],
      [{ ...range, min: '2026-02-30' }], [{ ...range, min: '0000-01-01' }], [{ ...range, min: '9999-12-31' }],
      [{ ...range, min: 1 }], [{ ...range, max: '2025-01-01' }],
      [{ scope: 'server', type: 'boolean', field: 'hasPublication', value: 1 }],
      [{ scope: 'server', type: 'ontology', field: 'topic', values: ['javascript:alert(1)'] }],
      [{ scope: 'server', type: 'score', field: 'fixtureQuality', version: 'old', min: 0.5 }],
      [{ scope: 'server', type: 'score', field: 'fixtureQuality', version: 'fixture-v1', min: 2 }]];
    for (const input of invalid) expect(() => parseAdvanced(JSON.stringify(input), config.scores)).toThrow();
    expect(() => parseAdvanced(' '.repeat(4097))).toThrow();
    expect(() => parseAdvanced(JSON.stringify([fixture.cases[5].filter]))).toThrow();
    expect(matchesFilters(undefined, [fixture.cases[0].filter])).toBe(false);
  });

  it('normalizes categorical values and preserves conjunction', () => {
    const filters = parseAdvanced(JSON.stringify([{ scope: 'server', type: 'categorical', field: 'toolType', values: ['B', 'A', 'B'] }]));
    expect(filters[0]).toMatchObject({ values: ['A', 'B'] });
    const both = [fixture.cases[0].filter, fixture.cases[2].filter];
    expect(body.items.filter(item => matchesFilters(item.filterValues, both)).map(item => item.id)).toEqual(['advanced-1', 'advanced-2']);
  });
});

describe('candidate workspace', () => {
  async function start() {
    vi.useFakeTimers();
    const fetcher = vi.fn().mockResolvedValue({ ok: true, json: async () => body });
    vi.stubGlobal('fetch', fetcher);
    wrapper = mount(SearchWorkspace, { props: config });
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    return fetcher;
  }

  it('retains candidate constraints and the page when changing result representation', async () => {
    history.replaceState(null, '', '/?page=2');
    await start();
    await wrapper!.get('#candidate-added-max').setValue('2026-01-10');
    for (const view of ['table', 'cards']) {
      await wrapper!.get(`input[value="${view}"]`).setValue(true);
      await vi.advanceTimersByTimeAsync(0); await flushPromises();
      expect(wrapper!.get('.candidate-scope').text()).toContain('4 of 6 loaded tools');
      expect(wrapper!.findAll(view === 'table' ? 'tbody tr' : 'article')).toHaveLength(4);
      expect(parseSearch(location.search, config).page).toBe(2);
      expect(parseSearch(location.search, config).advanced).toEqual([]);
    }
  });

  it('recomputes locally without requests, then promotes with canonical scope and resets on history', async () => {
    const fetcher = await start();
    await wrapper!.get('#candidate-added-max').setValue('2026-01-10');
    expect(wrapper!.findAll('article')).toHaveLength(4);
    expect(wrapper!.get('.candidate-scope').text()).toContain('4 of 6 loaded tools');
    expect(wrapper!.get('.candidate-scope').text()).toContain('125 server matches');
    expect(wrapper!.get('.candidate-scope').text()).toContain('Partial candidate set');
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(location.search).toBe('');
    const apply = wrapper!.findAll('button').find(button => button.text() === 'Apply to all matches')!;
    await apply.trigger('click');
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(fetcher).toHaveBeenCalledTimes(2);
    expect(parseSearch(location.search, config).advanced).toEqual([{ scope: 'server', type: 'range', field: 'added', max: '2026-01-10' }]);
    expect(wrapper!.text()).toContain('Applied to all matches');
    expect(wrapper!.find('.candidate-scope').exists()).toBe(false);
    await wrapper!.get('#candidate-publication').setValue('yes');
    history.replaceState(null, '', '/'); window.dispatchEvent(new PopStateEvent('popstate'));
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(wrapper!.get('#candidate-publication').element).toHaveProperty('value', '');
    expect(wrapper!.find('.candidate-scope').exists()).toBe(false);
    expect(wrapper!.text()).not.toContain('Applied to all matches');
  });

  it('shows declared score controls, empty local scope, complete candidates and recoverable invalid bounds', async () => {
    const fetcher = await start();
    await wrapper!.get('#candidate-fixtureQuality-min').setValue('0.75');
    expect(wrapper!.findAll('article')).toHaveLength(2);
    expect(wrapper!.text()).toContain('Fixture quality min (fixture-v1)');
    await wrapper!.get('#candidate-fixtureQuality-max').setValue('0.5');
    expect(wrapper!.get('[role="alert"]').text()).toContain('Invalid advanced filters');
    const apply = wrapper!.findAll('button').find(button => button.text() === 'Apply to all matches')!;
    expect(apply.attributes()).toHaveProperty('disabled');
    await wrapper!.findAll('button').find(button => button.text() === 'Clear candidate filters')!.trigger('click');
    expect(wrapper!.find('[role="alert"]').exists()).toBe(false);
    await wrapper!.get('#candidate-added-min').setValue('2099-01-01');
    expect(wrapper!.text()).toContain('No candidates match');
    expect(wrapper!.get('.candidate-scope').text()).toContain('0 of 6 loaded tools');
    expect(fetcher).toHaveBeenCalledTimes(1);
    fetcher.mockResolvedValue({ ok: true, json: async () => ({ ...body, count: 6, candidates: { ...body.candidates, complete: true } }) });
    await wrapper!.findAll('button').find(button => button.text() === 'Clear all')!.trigger('click');
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    await wrapper!.get('#candidate-publication').setValue('no');
    expect(wrapper!.get('.candidate-scope').text()).toContain('All server matches loaded');
  });
});
