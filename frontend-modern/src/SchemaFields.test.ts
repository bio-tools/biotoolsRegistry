import { afterEach, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import ResourceEditor from './ResourceEditor.vue';
import descriptor from '../../backend/elixir/biotoolsSchema/resource-ui.generated.json';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';
import { editorToResource, editorToSubmission, resourceToEditor, type Field, type ResourceSchema } from './resource-editor';

const fetchMock = vi.fn();
let wrapper: VueWrapper | undefined;
const field = (kind: string, label: string): Field => ({ kind, label, writable: true, public: true,
  required: false, nullable: false, readOnly: false });
function open(schema: ResourceSchema | null = structuredClone(descriptor)) {
  vi.stubGlobal('fetch', fetchMock);
  document.head.innerHTML = '<meta name="csrf-token" content="' + 'a'.repeat(64) + '">';
  wrapper = mount(ResourceEditor, { props: { resource: structuredClone(fixtures.rich), revision: 'record', schema,
    schemaRevision: schema?.revision, endpoint: '/save/', detailUrl: '/tool/', editUrl: '/edit/',
    edamEndpoint: '/edam/', toolTypes: [] }, global: { stubs: { EdamSelector: true } } });
  return wrapper;
}
afterEach(() => { wrapper?.unmount(); vi.unstubAllGlobals(); fetchMock.mockReset(); });

it('renders newly advertised nested fields inside the unchanged function diagram and submits them', async () => {
  const schema: ResourceSchema = structuredClone(descriptor);
  schema.revision = 'activated-fixture';
  const fields = schema.contract.fields!.function.item!.fields!;
  fields.extra = { ...field('object', 'Additional annotation'), fields: {
    enabled: field('boolean', 'Enabled'), score: { ...field('number', 'Score'), minimum: 0, maximum: 10 },
    labels: { ...field('array', 'Labels'), itemLabel: 'Label', item: field('string', 'Label') },
  } };
  fields.cmd = { ...fields.cmd, label: 'Invocation', help: 'Command for this annotation.' };
  const view = open(schema);
  expect(view.findAll('.function-diagram').length).toBe(fixtures.rich.function.length);
  expect(view.text()).toContain('Invocation');
  expect(view.text()).toContain('Command for this annotation.');
  const entry = view.findAll('.function-entry')[0];
  await entry.findAll('button').find(button => button.text() === 'Add Additional annotation')!.trigger('click');
  const enabledIcon = entry.get('label[for$="-extra-enabled"] svg');
  expect(enabledIcon.attributes('aria-hidden')).toBe('true');
  expect(enabledIcon.get('use').attributes('href')).toContain('#boolean');
  expect(entry.text()).toContain('Additional annotation');
  await entry.get('input[id$="-extra-enabled"]').setValue(true);
  await entry.get('input[id$="-extra-score"]').setValue('2.5');
  await entry.findAll('button').find(button => button.text() === 'Add label')!.trigger('click');
  await entry.get('input[id*="-extra-labels-"]').setValue('New value');
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ function: [{ extra: { score: ['Review score.'] } }] }), { status: 400 }));
  await view.get('form').trigger('submit');
  await flushPromises();
  const body = JSON.parse(fetchMock.mock.calls[0][1].body);
  expect(body.schemaRevision).toBe('activated-fixture');
  expect(body.resource.function[0].extra).toEqual({ enabled: true, score: 2.5, labels: ['New value'] });
  expect(entry.text()).toContain('Review score.');
  const link = view.get('.editor-errors a').attributes('href')!;
  expect(view.get(link).element).toBe(entry.get('input[id$="-extra-score"]').element);
});

it('shows added choice labels without changing their stable values', async () => {
  const schema: ResourceSchema = structuredClone(descriptor);
  schema.contract.fields!.maturity.choices!.push({ value: 'preview-id', label: 'Preview release' });
  const view = open(schema);
  expect(view.get('#nested-maturity').text()).toContain('Preview release');
  await view.get('#nested-maturity').setValue('preview-id');
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Captured' }), { status: 400 }));
  await view.get('form').trigger('submit');
  await flushPromises();
  expect(JSON.parse(fetchMock.mock.calls[0][1].body).resource.maturity).toBe('preview-id');
});

it('initializes required repeated fields without selecting an enum value', async () => {
  const view = open();
  await view.findAll('button').find(button => button.text() === 'Add link')!.trigger('click');
  const links = view.get('#nested-link');
  const labels = links.findAll('label');
  expect(labels.some(label => label.text() === 'URL')).toBe(true);
  expect(labels.some(label => label.text() === 'Type 1')).toBe(true);
  const choice = links.findAll('select').at(-1)!;
  expect(choice.element.value).toBe('');
});

it('retains removed choices visibly and losslessly but requires correction before saving', async () => {
  const schema: ResourceSchema = structuredClone(descriptor);
  schema.contract.fields!.license.choices = [{ value: 'new-license', label: 'New license' }];
  const view = open(schema);
  expect(view.get('#nested-license').element).toHaveProperty('value', fixtures.rich.license);
  expect(view.get('#nested-license option:disabled').text()).toContain('no longer allowed');
  expect(view.get('button[type="submit"]').attributes()).toHaveProperty('disabled');
  await view.get('form').trigger('submit');
  expect(fetchMock).not.toHaveBeenCalled();
  const draft = resourceToEditor(fixtures.rich);
  expect(editorToSubmission(draft, schema.contract).blockers.some(item => item.reason === 'removed-choice')).toBe(true);
  expect(editorToResource(draft)).toEqual(fixtures.rich);
  await view.get('#nested-license').setValue('new-license');
  expect(view.get('button[type="submit"]').attributes()).not.toHaveProperty('disabled');
});

it('keeps missing, mismatched and unsupported metadata read-only with export available', async () => {
  for (const schema of [null, { ...descriptor, protocol: 99 },
    { ...descriptor, contract: { ...descriptor.contract, fields: { unsupported: field('executable', 'Invalid') } } }]) {
    wrapper?.unmount();
    const view = open(schema);
    expect(view.get('[role="alert"]').text()).toContain('Editing is disabled');
    expect(view.get('.editor-fields').attributes()).toHaveProperty('disabled');
    expect(view.get('button[type="submit"]').attributes()).toHaveProperty('disabled');
    expect(view.findAll('button').find(button => button.text() === 'Export draft')!.attributes()).not.toHaveProperty('disabled');
    await view.get('form').trigger('submit');
  }
  expect(fetchMock).not.toHaveBeenCalled();
});

it('does not delete empty repeated values or coerce primitive arrays during draft mapping', () => {
  const contract: Field = { ...field('object', 'Root'), fields: {
    values: { ...field('array', 'Values'), item: field('number', 'Value') },
    flags: { ...field('array', 'Flags'), item: field('boolean', 'Flag') },
    labels: { ...field('array', 'Labels'), item: field('string', 'Label') },
  } };
  const record = { values: [0, 2.5], flags: [false, true], labels: [''] };
  expect(editorToSubmission(resourceToEditor(record), contract).payload).toEqual(record);
});

it('submits stable EDAM URIs while retaining old labels in the draft and export', () => {
  const resource = { topic: [{ uri: 'http://edamontology.org/topic_0091', term: 'Old label' }, { term: 'Term only' }],
    otherID: [{ value: 'http://edamontology.org/topic_0091', type: 'doi' }] };
  const draft = resourceToEditor(resource);
  const submitted = editorToSubmission(draft, descriptor.contract);
  expect(submitted.payload.topic).toEqual([{ uri: 'http://edamontology.org/topic_0091' }, { term: 'Term only' }]);
  expect(submitted.payload.otherID).toEqual(resource.otherID);
  expect(submitted.normalizations.map(item => item.reason)).toEqual(['edam-label-from-uri']);
  expect(editorToResource(draft)).toEqual(resource);
});

it('does not discard malformed EDAM labels during submission', () => {
  const resource = { topic: [{ uri: 'http://edamontology.org/topic_0091', term: { unexpected: true } }] };
  const submitted = editorToSubmission(resourceToEditor(resource), descriptor.contract);
  expect(submitted.payload.topic).toEqual(resource.topic);
  expect(submitted.normalizations).toEqual([]);
});
