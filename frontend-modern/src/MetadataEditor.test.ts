import { defineComponent } from 'vue';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { flushPromises, mount, type DOMWrapper, type VueWrapper } from '@vue/test-utils';
import ResourceEditor from './ResourceEditor.vue';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';
import { richSubmission } from './resource-editor.fixtures';
import schema from '../../backend/elixir/biotoolsSchema/resource-ui.generated.json';
const metadataFields = Object.entries(schema.contract.fields).filter(([name, field]) => field.writable &&
  !['name', 'description', 'homepage', 'toolType', 'function'].includes(name)).map(([name]) => name);

const Selector = defineComponent({ name: 'EdamSelector', props: ['scope', 'modelValue'], emits: ['update:modelValue'], template: '<div />' });
const metadataOptions = { license: ['MIT', 'Apache-2.0'], 'credit.typeEntity': ['Person', 'Project'],
  'credit.typeRole': ['Developer', 'Maintainer'], 'download.type': ['Source code', 'Software package'] };
const config = { resource: fixtures.rich, revision: 'initial', endpoint: '/save/', editUrl: '/edit/', detailUrl: '/tool/',
  schema, schemaRevision: schema.revision,
  toolTypes: ['Command-line tool'], edamEndpoint: '/edam/', metadataOptions };
const fetchMock = vi.fn();
let wrapper: VueWrapper;
const button = (scope: VueWrapper | DOMWrapper<Element>, text: string) => scope.findAll('button').find(item => item.text() === text)!;
beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock);
  vi.spyOn(window, 'confirm').mockReturnValue(true);
  document.head.innerHTML = '<meta name="csrf-token" content="' + 'a'.repeat(64) + '">';
  wrapper = mount(ResourceEditor, { props: config, global: { stubs: { EdamSelector: Selector } } });
});
afterEach(() => { wrapper.unmount(); fetchMock.mockReset(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });
async function submit(errors: unknown = { detail: 'Captured snapshot' }) {
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify(errors), { status: 400 }));
  await wrapper.get('form').trigger('submit');
  await flushPromises();
  return JSON.parse(fetchMock.mock.calls.at(-1)![1].body).resource;
}

it('renders all 19 missing schema fields and preserves rich typed payloads without client IDs', async () => {
  for (const field of metadataFields) expect(wrapper.find('#nested-' + field).exists(), field).toBe(true);
  const value = await submit();
  for (const field of metadataFields) {
    const expected = richSubmission[field as keyof typeof richSubmission];
    // Read-only null metadata and optional nulls are normalized by the existing contract.
    expect(value[field]).toEqual(expected);
  }
  expect(value.function).toEqual(richSubmission.function);
  expect(value.owner).toBe(fixtures.rich.owner);
  expect(JSON.stringify(value)).not.toContain('itemId');
});

it('edits scalar metadata and adds credits, publications and topic through their dedicated controls', async () => {
  await wrapper.get('#nested-license').setValue('Apache-2.0');
  await button(wrapper, 'Add version').trigger('click');
  await wrapper.get('#nested-version').findAll('input').at(-1)!.setValue('3.0');
  await button(wrapper, 'Add credit').trigger('click');
  const credit = wrapper.get('#nested-credit').findAll('.metadata-record').at(-1)!;
  await credit.get('input[id$="-name"]').setValue('New Contributor');
  await credit.get('input[id$="-rorid"]').setValue('03yrm5c26');
  await credit.get('select[id$="-typeEntity"]').setValue('Project');
  await button(credit, 'Add role').trigger('click');
  await credit.get('.metadata-strings select').setValue('Maintainer');
  await button(wrapper, 'Add publication').trigger('click');
  const publication = wrapper.get('#nested-publication').findAll('.metadata-record').at(-1)!;
  await publication.get('input[id$="-doi"]').setValue('10.1234/metadata');
  const topic = wrapper.findAllComponents(Selector).find(item => item.props('scope') === 'topic')!;
  topic.vm.$emit('update:modelValue', ['http://edamontology.org/topic_0080']);
  const value = await submit();
  expect(value.license).toBe('Apache-2.0');
  expect(value.version).toEqual(['1.0', '2.0', '3.0']);
  expect(value.credit.at(-1)).toEqual({ name: 'New Contributor', rorid: '03yrm5c26', typeEntity: 'Project', typeRole: ['Maintainer'] });
  expect(value.publication.at(-1)).toEqual({ doi: '10.1234/metadata' });
  expect(value.topic).toEqual([{ uri: 'http://edamontology.org/topic_0080' }]);
  expect(value.function).toEqual(richSubmission.function);
});

it('keeps a nested credit error attached through reorder and reports removal without a broken anchor', async () => {
  await button(wrapper, 'Add credit').trigger('click');
  const credits = wrapper.get('#nested-credit');
  const second = credits.findAll('.metadata-record')[1];
  await second.get('input[id$="-email"]').setValue('bad-email');
  const id = second.attributes('id');
  await submit({ credit: [{}, { email: ['Invalid email address.'] }] });
  expect(second.text()).toContain('Invalid email address.');
  await second.get('[aria-label="Move credit 2 up"]').trigger('click');
  expect(credits.findAll('.metadata-record')[0].attributes('id')).toBe(id);
  expect(wrapper.get('[role="alert"] a').text()).toContain('credit / 1 / email');
  await second.get('[aria-label="Remove credit 1"]').trigger('click');
  expect(wrapper.get('[role="alert"]').text()).toContain('Removed item');
  expect(wrapper.get('[role="alert"]').find('a').exists()).toBe(false);
});

it('keeps the identifier value field name in its error summary', async () => {
  await submit({ otherID: [{ value: ['Invalid identifier.'] }] });
  expect(wrapper.get('[role="alert"] a').text()).toContain('otherID / 1 / value');
  const target = wrapper.get('[role="alert"] a').attributes('href')!;
  expect(wrapper.get(target).element.tagName).toBe('INPUT');
});

it('saves enriched records, locks existing protected IDs and clears enrichment only on publication identity changes', async () => {
  wrapper.unmount();
  const resource = { ...fixtures.rich, elixir_badge: 4, homepage_status: 2,
    otherID: [{ value: 'BIOTOOLS:previous-id', type: 'biotoolsCURIE' }, ...fixtures.rich.otherID],
    publication: [{ ...fixtures.rich.publication[0], metadata: { title: 'Preserved title' } }] };
  wrapper = mount(ResourceEditor, { props: { ...config, resource }, global: { stubs: { EdamSelector: Selector } } });
  const identifier = wrapper.get('#nested-otherID').findAll('.metadata-record')[0];
  expect(identifier.get('input[id$="-value"]').attributes()).toHaveProperty('disabled');
  expect(identifier.get('[aria-label="Remove identifier 1"]').attributes()).toHaveProperty('disabled');
  const publication = wrapper.get('#nested-publication');
  await publication.get('input[id$="-version"]').setValue('4.0');
  const first = await submit();
  expect(first.publication[0].metadata).toEqual({ title: 'Preserved title' });
  expect(first.otherID).toEqual(resource.otherID);
  expect(first.elixir_badge).toBe(4);
  await publication.get('input[id$="-pmid"]').setValue('99999');
  expect((await submit()).publication[0]).not.toHaveProperty('metadata');
  await button(wrapper, 'Add identifier').trigger('click');
  const added = wrapper.get('#nested-otherID').findAll('.metadata-record').at(-1)!;
  await added.get('input[id$="-value"]').setValue('biotools:');
  expect(added.get('input[id$="-value"]').attributes()).not.toHaveProperty('disabled');
});

it('explicitly clears optional values while retaining untouched nested data and distinct type cardinalities', async () => {
  await wrapper.get('#nested-license').setValue('');
  const download = wrapper.get('#nested-download');
  await download.get('input[id$="-version"]').setValue('');
  await download.get('select[id$="-type"]').setValue('Software package');
  await button(wrapper.find('#nested-link'), 'Add type').trigger('click');
  await wrapper.get('#nested-link').findAll('.metadata-strings select').at(-1)!.setValue('Mirror');
  const value = await submit();
  expect(value).not.toHaveProperty('license');
  expect(value.download[0]).not.toHaveProperty('version');
  expect(value.download[0].type).toBe('Software package');
  expect(value.link[0].type).toEqual(['Repository', 'Issue tracker', 'Mirror']);
  expect(value.credit).toEqual(fixtures.rich.credit);
  expect(value.publication).toEqual(fixtures.rich.publication);
});
