import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import ResourceEditor from './ResourceEditor.vue';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';
import { richSubmission } from './resource-editor.fixtures';
import schema from '../../backend/elixir/biotoolsSchema/resource-ui.generated.json';

const config = { resource: fixtures.rich, revision: 'initial', endpoint: '/save/', editUrl: '/edit/', detailUrl: '/tool/',
  schema, schemaRevision: schema.revision,
  toolTypes: ['Command-line tool'], edamEndpoint: '/edam/', canManagePermissions: true };
let wrapper: VueWrapper;
const fetchMock = vi.fn();
const submit = () => wrapper.get('form').trigger('submit');
const scope = () => wrapper.get('#nested-editPermission');
beforeEach(() => {
  vi.useFakeTimers();
  vi.stubGlobal('fetch', fetchMock);
  document.head.innerHTML = '<meta name="csrf-token" content="' + 'a'.repeat(64) + '">';
  wrapper = mount(ResourceEditor, { props: config, global: { stubs: { EdamSelector: true } } });
});
afterEach(() => { wrapper.unmount(); vi.useRealTimers(); vi.unstubAllGlobals(); fetchMock.mockReset(); });

it('changes access mode and users without losing schema fields or hidden group membership', async () => {
  await scope().get('input[value="private"]').setValue();
  await scope().get('input[value="group"]').setValue();
  expect(scope().text()).toContain('contract-author');
  await scope().get('[aria-label="Remove contract-author"]').trigger('click');
  await scope().get('#permission-user').setValue('new-editor');
  await scope().get('#permission-user').trigger('keydown.enter');
  await scope().get('#permission-user').setValue('new-editor');
  expect(scope().findAll('button').find(button => button.text() === 'Add user')!.attributes()).toHaveProperty('disabled');
  await scope().get('#permission-user').setValue('');
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ ...config, resource: { ...fixtures.rich,
    editPermission: { type: 'group', authors: ['new-editor'] } } })));
  await submit();
  await flushPromises();
  const sent = JSON.parse(fetchMock.mock.calls[0][1].body).resource;
  expect(sent.editPermission).toEqual({ type: 'group', authors: ['new-editor'] });
  expect(sent.function).toEqual(richSubmission.function);
  expect(sent.publication).toEqual(fixtures.rich.publication);
  expect(wrapper.get('[role="status"]').text()).toBe('Changes saved.');
});

it('keeps permission controls read-only for nonowners', async () => {
  wrapper.unmount();
  wrapper = mount(ResourceEditor, { props: { ...config, canManagePermissions: false }, global: { stubs: { EdamSelector: true } } });
  expect(scope().get('fieldset').attributes()).toHaveProperty('disabled');
  expect(scope().get('[aria-label="Remove contract-author"]').attributes()).toHaveProperty('disabled');
  expect(scope().find('#permission-user').exists()).toBe(false);
  expect(scope().text()).toContain('contract-author');
});

it('maps invalid usernames to their stable list item and retains the draft', async () => {
  await scope().get('#permission-user').setValue('unknown-editor');
  await scope().get('#permission-user').trigger('keydown.enter');
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ editPermission: { authors: [{}, { general_errors: ['Specified user does not exist.'] }] } }), { status: 400 }));
  await submit();
  await flushPromises();
  const link = wrapper.get('[role="alert"] a');
  expect(wrapper.get(link.attributes('href')!).text()).toContain('unknown-editor');
  expect(scope().text()).toContain('Specified user does not exist.');
  await scope().get('[aria-label="Remove unknown-editor"]').trigger('click');
  expect(wrapper.get('[role="alert"]').text()).toContain('Removed item');
  expect(wrapper.get('[role="alert"]').find('a').exists()).toBe(false);
});

it('debounces the existing username lookup, ignores stale results and permits recovery', async () => {
  let first!: (response: Response) => void;
  fetchMock.mockReturnValueOnce(new Promise(resolve => { first = resolve; }));
  await scope().get('#permission-user').setValue('first');
  await vi.advanceTimersByTimeAsync(250);
  const signal = fetchMock.mock.calls[0][1].signal;
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify([{ username: 'second-user' }, { username: 'contract-author' }])));
  await scope().get('#permission-user').setValue('second');
  await vi.advanceTimersByTimeAsync(250);
  await flushPromises();
  expect(signal.aborted).toBe(true);
  first(new Response(JSON.stringify([{ username: 'stale-user' }])));
  await flushPromises();
  expect(scope().findAll('datalist option').map(option => option.attributes('value'))).toEqual(['second-user']);
  expect(fetchMock.mock.calls[1][0]).toContain('/api/user-list/?format=json&term=second');
  expect(fetchMock.mock.calls[1][1].headers.has('Authorization')).toBe(false);
  fetchMock.mockRejectedValueOnce(new TypeError('Offline'));
  await scope().get('#permission-user').setValue('offline');
  await vi.advanceTimersByTimeAsync(250);
  await flushPromises();
  expect(scope().text()).toContain('User search unavailable.');
  fetchMock.mockResolvedValueOnce(new Response('[]'));
  await scope().get('#permission-user').setValue('missing');
  await vi.advanceTimersByTimeAsync(250);
  await flushPromises();
  expect(scope().text()).toContain('No matching users.');
});
