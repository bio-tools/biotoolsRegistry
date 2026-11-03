import { afterEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import { nextTick } from 'vue';
import SearchWorkspace from './SearchWorkspace.vue';
import { defaultState, parseSearch, serializeSearch, type SearchConfig, type SearchResponse } from './search-state';

const config: SearchConfig = { endpoint: '/search/data/', filters: { toolType: 'Tool type', topic: 'Topic' },
  sorts: { lastUpdate: 'Updated', name: 'Name', score: 'Relevance' }, pageSizes: [10, 25, 50, 100], maxWindow: 10000 };
const response = (name = 'Example'): SearchResponse => ({
  items: [{ id: 'example', name, description: 'A tool', url: '/tool/example/', toolTypes: ['Command-line tool'],
    topics: ['Analysis'], operations: [], added: '2026-01-01', updated: '2026-02-01' }],
  count: 1, facets: {}, pagination: { page: 1, perPage: 50, pages: 1, previous: null, next: null, limited: false },
});
const success = (body = response()) => ({ ok: true, json: async () => body });
let wrapper: VueWrapper | undefined;
afterEach(() => {
  wrapper?.unmount(); wrapper = undefined;
  vi.useRealTimers(); vi.unstubAllGlobals(); vi.restoreAllMocks();
  history.replaceState(null, '', '/');
});

describe('canonical state', () => {
  it('round trips every primary value without losing punctuation or query spaces', () => {
    const state = { ...defaultState(), q: 'gene + "sequence" & analysis', page: 4, per_page: 25,
      sort: 'name', ord: 'asc' as const, filters: { toolType: '"Command-line tool"', topic: 'A & B' } };
    expect(parseSearch(serializeSearch(state), config)).toEqual(state);
    expect(serializeSearch(defaultState())).toBe('');
    expect(serializeSearch(parseSearch('page=001&per_page=50&sort=lastUpdate', config))).toBe('');
  });
  it.each(['page=0', 'page=-1', 'page=1.5', 'per_page=bad', 'per_page=101', 'page=101&per_page=100',
    'sort=toString', 'ord=up', 'unknown=value', 'topic=%00', 'topic=%5C', 'topic=!!!', 'q=%22%22', 'q=' + 'x'.repeat(257)])('rejects %s', query => {
    expect(() => parseSearch(query, config)).toThrow();
  });
  it('uses the last repeated value like the public QueryDict contract', () => {
    const state = parseSearch('q=first&q=last&topic=old&topic=%22A+%26+B%22&page=2&page=3', config);
    expect(state.q).toBe('last');
    expect(state.filters.topic).toBe('"A & B"');
    expect(state.page).toBe(3);
    expect(parseSearch(serializeSearch(state), config)).toEqual(state);
  });
});

describe('workspace', () => {
  it('searches used values locally and toggles selected values without losing domain scope', async () => {
    vi.useFakeTimers();
    const data = { ...response(), facets: { toolType: { truncated: false, values: Array.from({ length: 8 }, (_, i) => ({ value: 'Type ' + i, count: 10 - i })) } } };
    const fetcher = vi.fn().mockResolvedValue(success(data));
    vi.stubGlobal('fetch', fetcher);
    history.replaceState(null, '', '/?domain=example');
    wrapper = mount(SearchWorkspace, { props: { ...config, filters: { ...config.filters, domain: 'Domain' } } });
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    const before = fetcher.mock.calls.length;
    await wrapper.get('#find-options-toolType').setValue('Type 7');
    expect(wrapper.findAll('.facet-option')).toHaveLength(1);
    expect(fetcher.mock.calls).toHaveLength(before);
    await wrapper.get('.facet-option').trigger('click');
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(new URLSearchParams(location.search).get('toolType')).toBe('"Type 7"');
    expect(new URLSearchParams(location.search).get('domain')).toBe('example');
    await wrapper.get('.facet-option').trigger('click');
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(new URLSearchParams(location.search).has('toolType')).toBe(false);
    expect(new URLSearchParams(location.search).get('domain')).toBe('example');
  });

  it('opens active ancestor groups and keeps nested fields wired to URL state', async () => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(success()));
    history.replaceState(null, '', '/?creditOrcidID=Example');
    wrapper = mount(SearchWorkspace, { props: { ...config, filters: { ...config.filters, creditOrcidID: 'ORCID' }, filterGroups: [
      { id: 'science', label: 'Science', keys: [], children: [
        { id: 'science.credit', label: 'Credits', keys: ['creditOrcidID'], children: [] },
      ] }, { id: 'basic', label: 'Tool details', keys: ['toolType'], children: [] },
    ] } });
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(wrapper.get('[data-filter-group="science"]').attributes('open')).toBeDefined();
    expect(wrapper.get('[data-filter-group="science.credit"]').attributes('open')).toBeDefined();
    expect(wrapper.get('[data-filter-group="basic"]').attributes('open')).toBeUndefined();
    expect(wrapper.findAll('#filter-creditOrcidID')).toHaveLength(1);
    await wrapper.get('#filter-creditOrcidID').setValue('Another');
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(new URLSearchParams(location.search).get('creditOrcidID')).toBe('Another');
    expect(wrapper.get('[data-filter-group="science"] > summary').text()).toContain('1 active');
    await wrapper.get('[aria-label="Remove creditOrcidID filter"]').trigger('click');
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(wrapper.get('[data-filter-group="science"] > summary').text()).not.toContain('active');
  });

  it('shows loading, summaries, table dates, empty state and recoverable errors', async () => {
    vi.useFakeTimers();
    const fetcher = vi.fn().mockResolvedValueOnce(success()).mockResolvedValueOnce(success()).mockResolvedValueOnce(success({ ...response(), items: [], count: 0 }))
      .mockResolvedValueOnce({ ok: false, json: async () => ({ error: { message: 'Backend unavailable' } }) })
      .mockResolvedValueOnce(success());
    vi.stubGlobal('fetch', fetcher);
    wrapper = mount(SearchWorkspace, { props: config });
    await nextTick();
    expect(wrapper.text()).toContain('Searching...');
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(wrapper.get('article h2').text()).toBe('Example');
    await wrapper.get('input[value="table"]').setValue(true);
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(wrapper.get('table').text()).toContain('2026-01-01');
    expect(wrapper.get('table').text()).toContain('2026-02-01');
    await wrapper.get('#workspace-query').setValue('missing');
    await vi.advanceTimersByTimeAsync(300); await flushPromises();
    expect(wrapper.text()).toContain('No tools found');
    await wrapper.get('#workspace-query').setValue('failure');
    await vi.advanceTimersByTimeAsync(300); await flushPromises();
    expect(wrapper.get('[role="alert"]').text()).toContain('Backend unavailable');
    await wrapper.get('[role="alert"] button').trigger('click');
    await vi.advanceTimersByTimeAsync(0); await flushPromises();
    expect(wrapper.find('[role="alert"]').exists()).toBe(false);
    expect(wrapper.get('table').text()).toContain('Example');
  });

  it('aborts in-flight searches immediately and ignores late responses even when transport ignores abort', async () => {
    vi.useFakeTimers();
    let oldResolve!: (value: ReturnType<typeof success>) => void;
    const fetcher = vi.fn().mockImplementationOnce(() => new Promise(resolve => { oldResolve = resolve; }))
      .mockResolvedValueOnce(success(response('Newest')));
    vi.stubGlobal('fetch', fetcher);
    wrapper = mount(SearchWorkspace, { props: config });
    await vi.advanceTimersByTimeAsync(0);
    const signal = fetcher.mock.calls[0][1].signal;
    await wrapper.get('#workspace-query').setValue('gene ');
    expect(signal.aborted).toBe(true);
    expect((wrapper.get('#workspace-query').element as HTMLInputElement).value).toBe('gene ');
    await wrapper.get('#workspace-query').setValue('gene analysis');
    await vi.advanceTimersByTimeAsync(299);
    expect(fetcher).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(1); await flushPromises();
    expect(wrapper.get('article h2').text()).toBe('Newest');
    oldResolve(success(response('Stale'))); await flushPromises();
    expect(wrapper.get('article h2').text()).toBe('Newest');
    expect(new URLSearchParams(location.search).get('q')).toBe('gene analysis');
  });

  it('restores URL state on popstate and releases request on unmount', async () => {
    vi.useFakeTimers();
    const fetcher = vi.fn().mockResolvedValue(success());
    vi.stubGlobal('fetch', fetcher);
    history.replaceState(null, '', '/?q=initial&per_page=25');
    wrapper = mount(SearchWorkspace, { props: config });
    await vi.advanceTimersByTimeAsync(0);
    expect(fetcher.mock.calls[0][0]).toContain('per_page=25');
    history.replaceState(null, '', '/?q=previous&sort=name&ord=asc');
    window.dispatchEvent(new PopStateEvent('popstate'));
    await vi.advanceTimersByTimeAsync(0);
    expect((wrapper.get('#workspace-query').element as HTMLInputElement).value).toBe('previous');
    expect(fetcher.mock.calls[1][0]).toContain('sort=name');
    const signal = fetcher.mock.calls[1][1].signal;
    wrapper.unmount(); wrapper = undefined;
    expect(signal.aborted).toBe(true);
    window.dispatchEvent(new PopStateEvent('popstate'));
    await vi.advanceTimersByTimeAsync(1000);
    expect(fetcher).toHaveBeenCalledTimes(2);
  });
});
