import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import ResourceEditor from './ResourceEditor.vue';
import DomainEditors from './DomainEditors.vue';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';
import schema from '../../backend/elixir/biotoolsSchema/resource-ui.generated.json';
import type { Resource } from './resource-editor';

const fetchMock = vi.fn();
let wrapper: VueWrapper;
const props = { resource: fixtures.rich as Resource, revision: 'original', endpoint: '/save/', validateEndpoint: '/validate/',
  schema, schemaRevision: schema.revision, editUrl: '/edit', detailUrl: '/tool', toolTypes: [], edamEndpoint: '/edam' };
beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock);
  document.head.innerHTML = '<meta name="csrf-token" content="' + 'a'.repeat(64) + '">';
  wrapper = mount(ResourceEditor, { props, global: { stubs: { EdamSelector: true } } });
});
afterEach(() => { wrapper.unmount(); vi.unstubAllGlobals(); fetchMock.mockReset(); });
async function click(label: string) {
  await wrapper.findAll('button').find(button => button.text() === label)!.trigger('click');
  await flushPromises();
}
function jsonText() { return (wrapper.get('#editor-json').element as HTMLTextAreaElement).value; }

it('starts with the full record and keeps JSON current as form fields change', async () => {
  expect(JSON.parse(jsonText())).toEqual(fixtures.rich);
  expect(wrapper.get('.editor-json-panel summary').text()).toContain('JSON record');
  expect(wrapper.get('.editor-help').attributes('title')).toContain('current record in JSON format');
  await wrapper.get('#editor-name').setValue('Form edit');
  expect(JSON.parse(jsonText()).name).toBe('Form edit');
  const contributor = wrapper.get('#nested-credit').get('input[id$="-name"]');
  await contributor.setValue('Updated contributor');
  expect(JSON.parse(jsonText()).credit[0].name).toBe('Updated contributor');
  expect(fetchMock).not.toHaveBeenCalled();
});

it('updates form fields immediately from JSON and preserves untouched identities', async () => {
  const functionId = wrapper.find('.function-entry').attributes('data-function-id');
  const value = JSON.parse(jsonText());
  value.name = 'JSON edit'; value.credit[0].name = 'JSON contributor';
  await wrapper.get('#editor-json').setValue(JSON.stringify(value, null, 2));
  await flushPromises();
  expect(wrapper.get('#editor-name').element).toHaveProperty('value', 'JSON edit');
  expect(wrapper.get('#nested-credit').get('input[id$="-name"]').element).toHaveProperty('value', 'JSON contributor');
  expect(wrapper.find('.function-entry').attributes('data-function-id')).toBe(functionId);
  expect(JSON.parse(jsonText()).publication).toEqual(fixtures.rich.publication);
  expect(fetchMock).not.toHaveBeenCalled();
  await wrapper.get('#editor-description').setValue('Form after JSON');
  expect(JSON.parse(jsonText()).description).toBe('Form after JSON');
});

it('retains incomplete or incompatible JSON and prevents conflicting form changes', async () => {
  await wrapper.get('#editor-name').setValue('Last valid name');
  await wrapper.get('#editor-json').setValue('{broken');
  expect(jsonText()).toBe('{broken');
  expect(wrapper.get('.json-error').text()).toContain('JSON is incomplete or invalid');
  expect(wrapper.get('.editor-fields').attributes()).toHaveProperty('disabled');
  await wrapper.get('form').trigger('submit');
  expect(fetchMock).not.toHaveBeenCalled();
  await wrapper.get('#editor-json').setValue(JSON.stringify({ ...fixtures.rich, function: 'not a list' }));
  expect(wrapper.get('.json-error').text()).toContain('function must be a list');
  await wrapper.get('#editor-json').setValue('{"__proto__":{"polluted":true}}');
  expect(wrapper.get('.json-error').text()).toContain('unsupported field');
  await click('Restore JSON from form');
  expect(JSON.parse(jsonText()).name).toBe('Last valid name');
  expect(wrapper.get('#editor-name').element).toHaveProperty('value', 'Last valid name');
  expect(wrapper.find('.json-error').exists()).toBe(false);
});

it('preserves unsupported JSON fields until the user removes them', async () => {
  const value = { ...JSON.parse(jsonText()), futureField: { value: 'retained' } };
  await wrapper.get('#editor-json').setValue(JSON.stringify(value));
  await flushPromises();
  expect(JSON.parse(jsonText()).futureField.value).toBe('retained');
  expect(wrapper.get('button[type="submit"]').attributes()).toHaveProperty('disabled');
  delete value.futureField;
  await wrapper.get('#editor-json').setValue(JSON.stringify(value));
  await flushPromises();
  expect(wrapper.get('button[type="submit"]').attributes()).not.toHaveProperty('disabled');
});

it('lets the backend validate edits and refreshes JSON after an authoritative save', async () => {
  const value = JSON.parse(jsonText()); value.name = 'Edited name'; value.homepage = 'broken';
  await wrapper.get('#editor-json').setValue(JSON.stringify(value));
  expect(wrapper.get('#editor-homepage').element).toHaveProperty('value', 'broken');
  fetchMock.mockResolvedValueOnce(new Response('{"homepage":["Invalid URL"]}', { status: 400 }));
  await click('Validate without saving');
  expect(wrapper.text()).toContain('Invalid URL');
  expect(JSON.parse(jsonText()).homepage).toBe('broken');
  await wrapper.get('#editor-homepage').setValue('https://example.org/fixed');
  const saved = { ...value, name: 'Canonical name', homepage: 'https://example.org/fixed' };
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ ...props, resource: saved, revision: 'new' })));
  await wrapper.get('form').trigger('submit'); await flushPromises();
  expect(wrapper.get('#editor-name').element).toHaveProperty('value', 'Canonical name');
  expect(JSON.parse(jsonText()).name).toBe('Canonical name');
  expect(JSON.parse(jsonText()).homepage).toBe('https://example.org/fixed');
});

it('submits domain editors through the native form and excludes duplicates', async () => {
  wrapper.unmount();
  wrapper = mount(DomainEditors, { props: { initial: ['existing-user'] } });
  await wrapper.get('#domain-user').setValue('new-user');
  await wrapper.get('#domain-user').trigger('keydown.enter');
  expect(wrapper.get('input[name="editors"]').attributes('value')).toBe('existing-user\nnew-user');
  await wrapper.get('#domain-user').setValue('new-user');
  expect(wrapper.findAll('button').find(button => button.text() === 'Add user')!.attributes()).toHaveProperty('disabled');
  await wrapper.get('[aria-label="Remove existing-user"]').trigger('click');
  expect(wrapper.get('input[name="editors"]').attributes('value')).toBe('new-user');
});
