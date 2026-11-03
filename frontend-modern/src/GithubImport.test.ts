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

it('defaults to keep and applies selected changes directly, without saving', async () => {
  fetchMock.mockResolvedValue(response()); await request();
  expect(wrapper.text()).toContain('0 pending field changes');
  expect(wrapper.emitted('apply')).toBeUndefined();
  await wrapper.get('select').setValue('replace');
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
  expect(wrapper.text()).toContain('Owner: Protected');
  expect(wrapper.text()).toContain('0 pending field changes');
});

it('renders readable list suggestions and adds selected items', async () => {
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ suggestions: { language: ['R', 'Python'] },
    rejected: [], raw: {}, schemaRevision: schema.revision })));
  await request();
  expect(wrapper.text()).toContain('R; Python');
  await wrapper.get('select').setValue('merge');
  const checkboxes = wrapper.findAll('input[type="checkbox"]');
  expect(checkboxes).toHaveLength(2);
  await checkboxes[1].setValue(false);
  await button('Apply to draft').trigger('click');
  expect(wrapper.emitted('apply')).toEqual([[{ language: ['R'] }]]);
});

it('sorts EDAM comparisons by term, hides URIs and empty values, and preserves selection identity', async () => {
  const alpha = { term: 'Alpha topic', uri: 'http://edamontology.org/topic_0001' };
  const zeta = { term: 'Zeta topic', uri: 'http://edamontology.org/topic_0002' };
  await wrapper.setProps({ current: { topic: [zeta, null, alpha], name: null } });
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ suggestions: {
    topic: [zeta, null, alpha], name: 'New name', description: null,
  }, rejected: [], raw: {}, schemaRevision: schema.revision })));
  await request();
  const topic = wrapper.findAll('.import-field').find(field => field.text().includes('Topic'))!;
  expect(topic.findAll('.import-value').map(item => item.text())).toEqual([
    'Alpha topic; Zeta topic', 'Alpha topic; Zeta topic',
  ]);
  expect(topic.text()).not.toContain('edamontology.org');
  expect(wrapper.text()).not.toContain('None');
  expect(wrapper.findAll('.import-field')).toHaveLength(2);
  expect(wrapper.findAll('.import-field').find(field => field.text().includes('Name'))!.find('h4').text()).toBe('Suggested');
  await topic.get('select').setValue('merge');
  expect(topic.findAll('.import-item span').map(item => item.text())).toEqual(['Alpha topic', 'Zeta topic']);
  expect(topic.get('select').text()).toContain('Select items');
  await topic.findAll('input[type="checkbox"]')[0].setValue(false);
  await wrapper.get('.import-field:nth-of-type(2) select').setValue('replace');
  await button('Apply to draft').trigger('click');
  expect(wrapper.emitted('apply')).toEqual([[{ name: 'New name' }]]);
});

it('keeps the correct EDAM item when sorted selection is applied', async () => {
  const alpha = { term: 'Alpha', uri: 'http://edamontology.org/topic_0001' };
  const zeta = { term: 'Zeta', uri: 'http://edamontology.org/topic_0002' };
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ suggestions: { topic: [zeta, alpha] }, rejected: [], raw: {}, schemaRevision: schema.revision })));
  await request();
  await wrapper.get('select').setValue('merge');
  await wrapper.findAll('input[type="checkbox"]')[0].setValue(false);
  await button('Apply to draft').trigger('click');
  expect(wrapper.emitted('apply')).toEqual([[{ topic: [zeta] }]]);
});

it('lets users select individual nested operations and formats without losing their function', async () => {
  const operationA = { term: 'Alpha operation', uri: 'http://edamontology.org/operation_0001' };
  const operationB = { term: 'Beta operation', uri: 'http://edamontology.org/operation_0002' };
  const data = { term: 'Sequence', uri: 'http://edamontology.org/data_0006' };
  const formatA = { term: 'FASTA', uri: 'http://edamontology.org/format_1929' };
  const formatB = { term: 'FASTQ', uri: 'http://edamontology.org/format_1930' };
  const annotation = { operation: [operationB, operationA], input: [{ data, format: [formatB, formatA] }] };
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ suggestions: { function: [annotation] }, rejected: [], raw: {}, schemaRevision: schema.revision })));
  await request();
  await wrapper.get('select').setValue('merge');
  const row = (text: string) => wrapper.findAll('.import-nested label').find(item => item.text().includes(text))!;
  await row('Alpha operation').get('input').setValue(false);
  await row('FASTA').get('input').setValue(false);
  await button('Apply to draft').trigger('click');
  expect(wrapper.emitted('apply')).toEqual([[{ function: [{ operation: [operationB], input: [{ data, format: [formatB] }] }] }]]);
});

it('prevents applying a selected function without its required operation', async () => {
  const operation = { term: 'Operation', uri: 'http://edamontology.org/operation_0001' };
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ suggestions: { function: [{ operation: [operation] }] }, rejected: [], raw: {}, schemaRevision: schema.revision })));
  await request();
  await wrapper.get('select').setValue('merge');
  await wrapper.findAll('.import-nested input')[0].setValue(false);
  expect(wrapper.get('[role="alert"]').text()).toContain('required terms');
  expect(button('Apply to draft').attributes()).toHaveProperty('disabled');
});

it('compares publication identifiers and suggested titles without displaying abstracts', async () => {
  await wrapper.setProps({ current: { publication: [{ doi: '10.1234/current', pmid: '12345', metadata: { abstract: 'Long abstract', title: 'Old title' } }] } });
  const suggested = { doi: '10.1234/new', pmcid: 'PMC1234' };
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ suggestions: { publication: [suggested] }, rejected: [],
    raw: { publication: [{ ...suggested, metadata: { title: 'Suggested title', abstract: 'New abstract' } }] }, schemaRevision: schema.revision })));
  await request();
  const values = wrapper.findAll('.import-value').map(item => item.text());
  expect(values).toEqual(['DOI: 10.1234/current · PMID: 12345', 'Suggested title · DOI: 10.1234/new · PMCID: PMC1234']);
  await wrapper.get('select').setValue('merge');
  expect(wrapper.get('.import-item span').text()).toContain('Suggested title');
  expect(wrapper.get('.import-comparison').text()).not.toContain('abstract');
});
