import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import GithubImport from './GithubImport.vue';
import { applySuggestions, mergeSuggestions } from './github-import';
import { editorToResource, resourceToEditor, type Json } from './resource-editor';
import schema from '../../backend/elixir/biotoolsSchema/resource-ui.generated.json';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';

let wrapper: VueWrapper;
const fetchMock = vi.fn();
const original = { name: 'Curated name', description: 'Curated description retained.' };
const response = () => new Response(JSON.stringify({ suggestions: { name: 'Suggested name' }, rejected: [], raw: { name: 'Suggested name' }, schemaRevision: schema.revision }));
const button = (text: string) => wrapper.findAll('button').find(item => item.text() === text)!;
beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock);
  document.head.innerHTML = '<meta name="csrf-token" content="' + 'a'.repeat(64) + '">';
  wrapper = mount(GithubImport, { props: { endpoint: '/github-to-biotools', schema, current: original, identifier: null, disabled: false } });
});
afterEach(() => { wrapper.unmount(); vi.unstubAllGlobals(); fetchMock.mockReset(); });
async function request() {
  await wrapper.get('#github-repository').setValue('https://github.com/bio-tools/registry');
  await button('Get suggestions').trigger('click'); await flushPromises();
}

it('defaults to keep and applies only after confirmation, without saving', async () => {
  fetchMock.mockResolvedValue(response()); await request();
  expect(wrapper.text()).toContain('0 pending field changes');
  expect(wrapper.emitted('apply')).toBeUndefined();
  await wrapper.get('select').setValue('replace');
  await button('Review selected changes').trigger('click');
  expect(wrapper.emitted('apply')).toBeUndefined();
  await button('Apply to draft').trigger('click');
  expect(wrapper.emitted('apply')).toEqual([[{ name: 'Suggested name' }]]);
  expect(fetchMock).toHaveBeenCalledTimes(1);
  expect(original.name).toBe('Curated name');
});

it('requires a new review when selected draft values change', async () => {
  fetchMock.mockResolvedValue(response()); await request();
  await wrapper.get('select').setValue('replace');
  await wrapper.setProps({ current: { ...original, name: 'Edited while reviewing' } });
  expect(wrapper.text()).toContain('Your draft changed');
  expect(button('Apply to draft')).toBeUndefined();
  await button('Refresh comparison').trigger('click');
  expect(wrapper.text()).toContain('0 pending field changes');
  expect(wrapper.emitted('apply')).toBeUndefined();
});

it('discards and ignores cancelled late provider responses', async () => {
  let resolve!: (value: Response) => void;
  fetchMock.mockImplementation(() => new Promise<Response>(done => { resolve = done; }));
  await request(); await button('Cancel import').trigger('click');
  resolve(response()); await flushPromises();
  expect(wrapper.find('select').exists()).toBe(false);
  expect(wrapper.emitted('apply')).toBeUndefined();
});

it('keeps distinct function IO and repeated-item identities when merging', () => {
  const first = { operation: [{ uri: 'http://edamontology.org/operation_0004' }], input: [{ data: { uri: 'http://edamontology.org/data_0006' } }] };
  const second = { ...first, note: 'Different annotation' };
  expect(mergeSuggestions([first], [first, second])).toEqual([first, second]);
  expect(mergeSuggestions([first, first], [first])).toEqual([first, first]);
  const draft = resourceToEditor(fixtures.rich);
  const old = draft.function![0];
  const existing = editorToResource(draft).function as Json[];
  applySuggestions(draft, { function: mergeSuggestions(existing, [second]) });
  expect(draft.function![0]).toBe(old);
  expect(editorToResource(draft).function).toEqual([...existing, second]);
  expect(editorToResource(draft).publication).toEqual(fixtures.rich.publication);
});

it('escapes raw provider output and allows keep-all without mutation', async () => {
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ suggestions: { name: 'Suggested' },
    rejected: [{ path: 'owner', reason: 'Protected' }], raw: { name: '<img src=x onerror=alert(1)>' }, schemaRevision: schema.revision })));
  await request(); await wrapper.get('select').setValue('replace');
  await button('Keep all current values').trigger('click');
  expect(wrapper.find('img').exists()).toBe(false);
  expect(wrapper.text()).toContain('owner: Protected');
  expect(wrapper.text()).toContain('0 pending field changes');
});
