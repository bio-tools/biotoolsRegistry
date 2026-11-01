import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import ResourceEditor from './ResourceEditor.vue';
import DomainEditors from './DomainEditors.vue';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';
import schema from '../../backend/elixir/biotoolsSchema/resource-ui.generated.json';
import type { Resource } from './resource-editor';

const fetchMock = vi.fn();
let wrapper: VueWrapper;
beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock);
  document.head.innerHTML = '<meta name="csrf-token" content="' + 'a'.repeat(64) + '">';
  wrapper = mount(ResourceEditor, { props: { resource: fixtures.rich as Resource, revision: 'original',
    endpoint: '/save/', validateEndpoint: '/validate/', schema, schemaRevision: schema.revision,
    editUrl: '/edit', detailUrl: '/tool', toolTypes: [], edamEndpoint: '/edam' }, global: { stubs: { EdamSelector: true } } });
});
afterEach(() => { wrapper.unmount(); vi.unstubAllGlobals(); fetchMock.mockReset(); });
async function click(label: string) {
  await wrapper.findAll('button').find(button => button.text() === label)!.trigger('click');
  await flushPromises();
}

it('validates without writing and retains hidden metadata in raw edits', async () => {
  fetchMock.mockResolvedValue(new Response('{"valid":true}'));
  await click('Validate without saving');
  expect(fetchMock.mock.calls[0][0]).toMatch(/\/validate\/$/);
  expect(wrapper.text()).toContain('Validation passed. Nothing was saved.');
  await click('Load current draft as JSON');
  const raw = JSON.parse((wrapper.get('#editor-json').element as HTMLTextAreaElement).value);
  raw.name = 'Raw JSON edit';
  await wrapper.get('#editor-json').setValue(JSON.stringify(raw));
  await click('Validate and apply JSON');
  expect(fetchMock.mock.calls[1][0]).toMatch(/\/validate\/$/);
  expect(JSON.parse(fetchMock.mock.calls[1][1].body).resource.publication).toEqual(fixtures.rich.publication);
  expect(wrapper.get('#editor-name').element).toHaveProperty('value', 'Raw JSON edit');
  expect(wrapper.text()).toContain('JSON applied to the draft. Nothing was saved.');
});

it('retains invalid JSON and prevents form saving over unapplied text', async () => {
  await click('Load current draft as JSON');
  await wrapper.get('#editor-json').setValue('{broken');
  await click('Validate and apply JSON');
  expect(wrapper.get('#editor-json').element).toHaveProperty('value', '{broken');
  expect(wrapper.get('#editor-name').element).toHaveProperty('value', fixtures.rich.name);
  await wrapper.get('form').trigger('submit');
  expect(fetchMock).not.toHaveBeenCalled();
  await wrapper.get('#editor-json').setValue(JSON.stringify({ ...fixtures.rich, name: 'Invalid homepage', homepage: 'broken' }));
  fetchMock.mockResolvedValue(new Response('{"homepage":["Invalid URL"]}', { status: 400 }));
  await click('Validate and apply JSON');
  expect(wrapper.text()).toContain('Invalid URL');
  expect(wrapper.get('#editor-name').element).toHaveProperty('value', fixtures.rich.name);
});

it('refuses to replace a form draft changed after opening JSON', async () => {
  await click('Load current draft as JSON');
  await wrapper.get('#editor-json').setValue(JSON.stringify({ ...fixtures.rich, name: 'Old JSON' }));
  await wrapper.get('#editor-name').setValue('New form edit');
  await click('Validate and apply JSON');
  expect(wrapper.text()).toContain('The form draft changed');
  expect(fetchMock).not.toHaveBeenCalled();
  expect(wrapper.get('#editor-name').element).toHaveProperty('value', 'New form edit');
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
