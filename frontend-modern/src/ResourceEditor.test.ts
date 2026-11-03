import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import ResourceEditor from './ResourceEditor.vue';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';
import { richSubmission } from './resource-editor.fixtures';
import type { Resource } from './resource-editor';
import schema from '../../backend/elixir/biotoolsSchema/resource-ui.generated.json';

const fetchMock = vi.fn();
vi.mock('./EdamSelector.vue', () => ({ default: { template: '<div />' } }));
const initial = { resource: fixtures.rich as Resource, revision: 'original', endpoint: '/editor/tool/contract-rich/save/',
  previewEndpoint: '/editor/tool/contract-rich/record-preview/',
  schema, schemaRevision: schema.revision,
  editUrl: '/editor/tool/contract-rich/', detailUrl: '/tool/contract-rich/', toolTypes: ['Command-line tool', 'Web application'], edamEndpoint: '/edam/terms/' };
let wrapper: VueWrapper;
beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock);
  document.head.innerHTML = '<meta name="csrf-token" content="' + 'a'.repeat(64) + '">';
  vi.spyOn(window, 'confirm').mockReturnValue(false);
  wrapper = mount(ResourceEditor, { props: initial, attachTo: document.body });
});
afterEach(() => { wrapper.unmount(); document.body.innerHTML = ''; vi.restoreAllMocks(); vi.unstubAllGlobals(); fetchMock.mockReset(); });

async function save() { await wrapper.get('form').trigger('submit'); await flushPromises(); }
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

describe('basic resource editor', () => {
  it('previews the unsaved record and indicates when the preview needs refreshing', async () => {
    await wrapper.get('#editor-name').setValue('Unsaved preview name');
    fetchMock.mockResolvedValueOnce(new Response('<h1>Unsaved preview name</h1>', { status: 200, headers: { 'Content-Type': 'text/html' } }));
    await wrapper.findAll('button').find(button => button.text() === 'Preview record')!.trigger('click');
    await flushPromises();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.resource.name).toBe('Unsaved preview name');
    expect(wrapper.get('iframe').attributes('srcdoc')).toContain('Unsaved preview name');
    expect(wrapper.get('iframe').attributes()).toHaveProperty('sandbox');
    await wrapper.get('#editor-name').setValue('Updated after preview');
    expect(wrapper.text()).toContain('Draft changed. Refresh the preview');
    expect((wrapper.get('#editor-name').element as HTMLInputElement).value).toBe('Updated after preview');
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it('keeps rich out-of-scope fields in the snapshot and adopts authoritative readback', async () => {
    await wrapper.get('#editor-name').setValue('Basic edit');
    const updated = { ...initial, revision: 'next', resource: { ...fixtures.rich, name: 'Basic edit' } };
    fetchMock.mockResolvedValueOnce(response(updated));
    await save();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.revision).toBe('original');
    expect(sent.schemaRevision).toBe(schema.revision);
    expect(sent.resource.name).toBe('Basic edit');
    for (const key of ['function', 'publication', 'credit', 'link', 'download', 'documentation', 'relation', 'editPermission']) {
      expect(sent.resource[key]).toEqual(richSubmission[key as keyof typeof richSubmission]);
    }
    expect(sent.resource.toolType).toEqual(fixtures.rich.toolType);
    expect(wrapper.get('[role="status"]').text()).toBe('Changes saved.');
    expect(wrapper.get('#editor-biotoolsID').attributes()).toHaveProperty('readonly');
    expect(fetchMock.mock.calls[0][1].headers.get('X-CSRFToken')).toBe('a'.repeat(64));
  });

  it('maps precise backend errors to controls, preserving every entered value', async () => {
    await wrapper.get('#editor-homepage').setValue('not-a-url');
    fetchMock.mockResolvedValueOnce(response({ homepage: ['Enter a valid URL.'], function: [{ general_errors: ['Unsupported annotation'] }] }, 400));
    await save();
    expect((wrapper.get('#editor-homepage').element as HTMLInputElement).value).toBe('not-a-url');
    expect(wrapper.get('#error-homepage').text()).toBe('Enter a valid URL.');
    expect(wrapper.get('#editor-homepage').attributes('aria-invalid')).toBe('true');
    expect(wrapper.get('[role="alert"]').text()).toContain('Unsupported annotation');
    expect(document.activeElement).toBe(wrapper.get('[role="alert"]').element);
    expect(wrapper.get('[role="status"]').text()).toBe('Unsaved changes');
  });

  it('retains drafts through session, CSRF, conflict, permission and network failures without retrying', async () => {
    await wrapper.get('#editor-description').setValue('An unsaved description retained across failures.');
    for (const status of [401, 403, 409, 503]) {
      fetchMock.mockResolvedValueOnce(response(status === 401 ? { error: { code: 'authentication_required', loginUrl: '/auth/login/' } }
        : status === 403 ? { error: { code: 'csrf_failed' } } : { detail: 'Please check the record.' }, status));
      await save();
      expect((wrapper.get('#editor-description').element as HTMLTextAreaElement).value).toContain('unsaved description');
      expect(wrapper.get('[role="status"]').text()).toBe('Unsaved changes');
    }
    fetchMock.mockRejectedValueOnce(new TypeError('Network error'));
    await save();
    expect(wrapper.get('[role="alert"]').text()).toContain('Save could not be confirmed');
    expect(fetchMock).toHaveBeenCalledTimes(5);
  });

  it('warns on unsaved navigation and explicit discard restores the loaded data', async () => {
    const clean = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(clean);
    expect(clean.defaultPrevented).toBe(false);
    await wrapper.get('#editor-name').setValue('Draft name');
    const dirty = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(dirty);
    expect(dirty.defaultPrevented).toBe(true);
    const link = wrapper.get('.editor-heading a');
    const click = new MouseEvent('click', { bubbles: true, cancelable: true });
    link.element.dispatchEvent(click);
    expect(click.defaultPrevented).toBe(true);
    await wrapper.findAll('button').find(button => button.text() === 'Discard changes')!.trigger('click');
    expect((wrapper.get('#editor-name').element as HTMLInputElement).value).toBe('Draft name');
    vi.mocked(window.confirm).mockReturnValue(true);
    await wrapper.findAll('button').find(button => button.text() === 'Discard changes')!.trigger('click');
    expect((wrapper.get('#editor-name').element as HTMLInputElement).value).toBe(fixtures.rich.name);
    expect(wrapper.get('[role="status"]').text()).toBe('No unsaved changes');
  });

  it('blocks unsupported fields before transport but retains export and editing', async () => {
    wrapper.unmount();
    wrapper = mount(ResourceEditor, { props: { ...initial, resource: { ...initial.resource, futureField: 'Unknown' } } });
    expect(wrapper.get('[role="alert"]').text()).toContain('cannot yet be saved');
    expect(wrapper.get('button[type="submit"]').attributes()).toHaveProperty('disabled');
    await save();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('prevents duplicate pending saves and aborts outstanding transport on teardown', async () => {
    fetchMock.mockReturnValue(new Promise(() => {}));
    await wrapper.get('form').trigger('submit');
    await wrapper.get('form').trigger('submit');
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(wrapper.get('.editor-fields').attributes()).toHaveProperty('disabled');
    const signal = fetchMock.mock.calls[0][1].signal;
    wrapper.unmount();
    expect(signal.aborted).toBe(true);
    const event = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(false);
  });

  it('creates with explicit identity and omits empty optional tool types', async () => {
    wrapper.unmount();
    wrapper = mount(ResourceEditor, { props: { ...initial, revision: null, resource: { ...fixtures.minimal, toolType: [] } } });
    expect(wrapper.get('#editor-biotoolsID').attributes()).not.toHaveProperty('readonly');
    fetchMock.mockResolvedValueOnce(response({ ...initial, resource: fixtures.minimal }));
    await save();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.revision).toBeNull();
    expect(sent.resource.biotoolsID).toBe(fixtures.minimal.biotoolsID);
    expect(sent.resource).not.toHaveProperty('toolType');
  });
});
