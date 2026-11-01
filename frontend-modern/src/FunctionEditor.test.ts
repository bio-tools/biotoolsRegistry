import { defineComponent } from 'vue';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount, type DOMWrapper, type VueWrapper } from '@vue/test-utils';
import ResourceEditor from './ResourceEditor.vue';
import functions from '../../backend/elixirapp/tests/data/NestedFunctions.json';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';
import { conceptURIs, selectConcept } from './nested-editor';
import schema from '../../backend/elixir/biotoolsSchema/resource-ui.generated.json';

const Selector = defineComponent({ name: 'EdamSelector', props: ['scope', 'label', 'modelValue', 'multiple'],
  emits: ['update:modelValue'], template: '<div class="selector-stub">{{ label }} {{ modelValue }}</div>' });
const config = { resource: { ...fixtures.rich, function: functions }, revision: 'before',
  schema, schemaRevision: schema.revision,
  endpoint: '/editor/save/', editUrl: '/editor/tool/test/', detailUrl: '/tool/test/', toolTypes: ['Web application'], edamEndpoint: '/edam/terms/' };
const fetchMock = vi.fn();
let wrapper: VueWrapper;
const button = (scope: VueWrapper | DOMWrapper<Element>, text: string) => scope.findAll('button').find(item => item.text() === text)!;
const status = () => wrapper.get('[aria-label="Save status"]');
beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock);
  vi.spyOn(window, 'confirm').mockReturnValue(true);
  document.head.innerHTML = '<meta name="csrf-token" content="' + 'a'.repeat(64) + '">';
  wrapper = mount(ResourceEditor, { props: config, global: { stubs: { EdamSelector: Selector } } });
});
afterEach(() => { wrapper.unmount(); fetchMock.mockReset(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });
async function reject(body: unknown) {
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify(body), { status: 400 }));
  await wrapper.get('form').trigger('submit');
  await flushPromises();
}
const sent = () => JSON.parse(fetchMock.mock.calls.at(-1)![1].body).resource;

describe('schema-shaped nested editor', () => {
  it('adds independent functions, inputs, outputs and repeatable scoped annotations without wire IDs', async () => {
    await button(wrapper, 'Add function').trigger('click');
    const added = wrapper.findAll('[data-function-id]')[2];
    expect(added.findAllComponents(Selector)[0].props()).toMatchObject({ scope: 'operation', multiple: false });
    added.findAllComponents(Selector)[0].vm.$emit('update:modelValue', ['http://edamontology.org/operation_0292']);
    await button(added, 'Add input').trigger('click');
    await button(added, 'Add output').trigger('click');
    const input = added.findAll('[data-io-id]')[0];
    input.findAllComponents(Selector)[0].vm.$emit('update:modelValue', ['http://edamontology.org/data_0863']);
    await button(input, 'Add format').trigger('click');
    input.findAllComponents(Selector)[1].vm.$emit('update:modelValue', ['http://edamontology.org/format_1929']);
    const output = added.findAll('[data-io-id]')[1];
    output.findAllComponents(Selector)[0].vm.$emit('update:modelValue', ['http://edamontology.org/data_2044']);
    await reject({ detail: 'Test snapshot capture' });
    const resource = sent();
    expect(resource.function[2]).toEqual({ operation: [{ uri: 'http://edamontology.org/operation_0292' }],
      input: [{ data: { uri: 'http://edamontology.org/data_0863' }, format: [{ uri: 'http://edamontology.org/format_1929' }] }],
      output: [{ data: { uri: 'http://edamontology.org/data_2044' } }] });
    expect(JSON.stringify(resource)).not.toContain(added.attributes('data-function-id'));
    expect(resource.publication).toEqual(fixtures.rich.publication);
    expect(resource.credit).toEqual(fixtures.rich.credit);
    expect(resource.function.slice(0, 2)).toEqual(functions);
  });

  it('keeps error identity with a second output and format after function/output moves', async () => {
    const first = wrapper.findAll('[data-function-id]')[0];
    const functionID = first.attributes('data-function-id');
    const outputs = first.findAll('.io-list')[1];
    const outputID = outputs.findAll('[data-io-id]')[1].attributes('data-io-id');
    await reject({ function: [{ output: [{}, { format: [{}, { uri: ['Invalid format identity.'] }] }] }, {}] });
    expect(outputs.findAll('[data-io-id]')[0].text()).not.toContain('Invalid format identity.');
    expect(outputs.findAll('[data-io-id]')[1].text()).toContain('Invalid format identity.');
    await first.get('[aria-label="Move function 1 down"]').trigger('click');
    const moved = wrapper.findAll('[data-function-id]')[1];
    expect(moved.attributes('data-function-id')).toBe(functionID);
    await moved.get('[aria-label="Move output 2 up"]').trigger('click');
    const movedOutput = moved.findAll('.io-list')[1].findAll('[data-io-id]')[0];
    expect(movedOutput.attributes('data-io-id')).toBe(outputID);
    expect(movedOutput.text()).toContain('Invalid format identity.');
    expect(wrapper.get('[role="alert"] a').text()).toContain('function / 2 / output / 1 / format / 2');
    await moved.get('[aria-label="Remove output 1"]').trigger('click');
    expect(moved.text()).not.toContain('Invalid format identity.');
    expect(wrapper.get('[role="alert"]').text()).toContain('Removed item');
    expect(wrapper.get('[role="alert"]').find('a').exists()).toBe(false);
  });

  it('requires confirmation for populated removals and never deletes a function when its final operation is removed', async () => {
    const first = wrapper.findAll('[data-function-id]')[0];
    vi.mocked(window.confirm).mockReturnValue(false);
    await first.get('[aria-label="Remove function 1"]').trigger('click');
    expect(wrapper.findAll('[data-function-id]')).toHaveLength(2);
    await first.get('[aria-label="Remove input 1"]').trigger('click');
    expect(first.findAll('.io-list')[0].findAll('[data-io-id]')).toHaveLength(2);
    vi.mocked(window.confirm).mockReturnValue(true);
    await first.get('[aria-label="Remove input 1"]').trigger('click');
    expect(first.findAll('.io-list')[0].findAll('[data-io-id]')).toHaveLength(1);
    const second = wrapper.findAll('[data-function-id]')[1];
    await second.get('[aria-label="Remove operation 1"]').trigger('click');
    expect(wrapper.findAll('[data-function-id]')).toHaveLength(2);
    await reject({ function: [{}, { operation: ['This list may not be empty.'] }] });
    expect(sent().function[1].operation).toEqual([]);
    expect(second.text()).toContain('This list may not be empty.');
  });

  it('retains notes/commands through reorder and removes optional text only on explicit clearing', async () => {
    const first = wrapper.findAll('[data-function-id]')[0];
    await first.get('textarea').setValue('A deliberately updated function note.');
    await first.get('input[type="text"]').setValue('');
    await first.get('[aria-label="Move function 1 down"]').trigger('click');
    await reject({ detail: 'Test snapshot capture' });
    expect(sent().function[1].note).toBe('A deliberately updated function note.');
    expect(sent().function[1]).not.toHaveProperty('cmd');
    expect(sent().function[0]).toEqual(functions[1]);
    expect(status().text()).toBe('Unsaved changes');
  });

  it('does not impose a schema-invented count limit on operations or formats', async () => {
    const first = wrapper.findAll('[data-function-id]')[0];
    for (let index = 0; index < 21; index++) await button(first, 'Add operation').trigger('click');
    expect(first.get('.function-operations').findAll('[data-concept-id]')).toHaveLength(23);
    const input = first.findAll('[data-io-id]')[0];
    for (let index = 0; index < 21; index++) await button(input, 'Add format').trigger('click');
    expect(input.findAll('[data-concept-id]')).toHaveLength(23);
  });

  it('preserves untouched term-only/null identity and removes stale labels only after a changed selection', () => {
    const before = { uri: 'http://edamontology.org/data_0863', term: 'Original label' };
    expect(selectConcept(before, [before.uri])).toBe(before);
    expect(selectConcept(before, ['http://edamontology.org/data_2044'])).toEqual({ uri: 'http://edamontology.org/data_2044' });
    expect(selectConcept(before, [])).toEqual({});
    expect(conceptURIs({ term: 'Term only' })).toEqual([]);
    expect(conceptURIs(null)).toEqual([]);
  });
});
