import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import { nextTick } from 'vue';
import EdamSelector from './EdamSelector.vue';
import EdamField from './EdamField.vue';
import { edamPayload, type EdamTerm } from './edam';

const term = (uri: string, name: string): EdamTerm => ({ uri: 'http://edamontology.org/' + uri,
  term: name, definition: 'Definition of ' + name, synonyms: ['Synonym'], obsolete: false });
const bio = term('topic_0091', 'Bioinformatics');
const seq = term('topic_0080', 'Sequence analysis');
const success = (items = [bio, seq], suggestions: EdamTerm[] = []) => ({ ok: true, json: async () => ({ items, more: false, suggestions }) });
const props = { scope: 'topic' as const, endpoint: '/edam/terms/', label: 'Topics', multiple: true, modelValue: [] as string[] };
let wrapper: VueWrapper;
beforeEach(() => {
  vi.useFakeTimers();
  Object.defineProperty(HTMLDialogElement.prototype, 'showModal', { configurable: true,
    value: function (this: HTMLDialogElement) { this.open = true; } });
  Object.defineProperty(HTMLDialogElement.prototype, 'close', { configurable: true,
    value: function (this: HTMLDialogElement) { this.open = false; this.dispatchEvent(new Event('close')); } });
  Object.defineProperty(Element.prototype, 'scrollIntoView', { configurable: true, value: vi.fn() });
});
afterEach(() => {
  if (wrapper?.exists()) wrapper.unmount();
  document.body.innerHTML = ''; vi.useRealTimers(); vi.unstubAllGlobals(); vi.restoreAllMocks();
  Reflect.deleteProperty(Element.prototype, 'scrollIntoView');
  Reflect.deleteProperty(HTMLDialogElement.prototype, 'showModal');
  Reflect.deleteProperty(HTMLDialogElement.prototype, 'close');
});
async function settle(delay = 0) { await vi.advanceTimersByTimeAsync(delay); await flushPromises(); }
async function begin() {
  await wrapper.findAll('button').find(button => button.text() === 'Choose topics')!.trigger('click');
  await settle();
}
function button(name: string) { return wrapper.findAll('button').find(button => button.text() === name)!; }

it('stages keyboard multiple selection, commits IDs only, and keeps cancel separate', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(success()));
  wrapper = mount(EdamSelector, { props, attachTo: document.body });
  await begin();
  const input = wrapper.get('[role="combobox"]');
  await input.trigger('keydown', { key: 'ArrowDown' });
  expect(input.attributes('aria-activedescendant')).toBe(wrapper.findAll('[role="option"]')[0].attributes('id'));
  await input.trigger('keydown', { key: 'Enter' });
  await input.trigger('keydown', { key: 'ArrowDown' });
  await input.trigger('keydown', { key: 'Enter' });
  expect(wrapper.emitted('update:modelValue')).toBeUndefined();
  await button('Cancel').trigger('click');
  expect(wrapper.emitted('update:modelValue')).toBeUndefined();
  await begin();
  await input.trigger('keydown', { key: 'End' });
  await input.trigger('keydown', { key: 'Enter' });
  await button('Apply selection').trigger('click');
  expect(wrapper.emitted('update:modelValue')).toEqual([[[seq.uri]]]);
});

it('single selection replaces only on apply and removal serializes no label', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(success()));
  wrapper = mount(EdamField, { props: { ...props, initial: [bio.uri], initialTerms: [bio], name: 'topic', multiple: false } });
  expect(wrapper.get('input[type="hidden"]').attributes('value')).toBe(bio.uri);
  await begin();
  const input = wrapper.get('[role="combobox"]');
  await input.trigger('keydown', { key: 'ArrowUp' });
  await input.trigger('keydown', { key: 'Enter' });
  expect(wrapper.get('input[type="hidden"]').attributes('value')).toBe(bio.uri);
  await button('Apply selection').trigger('click');
  expect(wrapper.findAll('input[type="hidden"]')).toHaveLength(1);
  expect(wrapper.get('input[type="hidden"]').attributes('value')).toBe(seq.uri);
  await wrapper.get('button[aria-label="Remove Sequence analysis"]').trigger('click');
  expect(wrapper.findAll('input[type="hidden"]')).toHaveLength(0);
});

it('compact annotation opens the same keyboard selector and retains cancel, clear and disabled behavior', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(success()));
  wrapper = mount(EdamSelector, { props: { ...props, compact: true, multiple: false, modelValue: [bio.uri], initialTerms: [bio] } });
  const opener = wrapper.get('button[aria-haspopup="dialog"]');
  expect(opener.text()).toBe('Bioinformatics');
  expect(opener.attributes('aria-label')).toBe('Choose topics: Bioinformatics');
  expect(wrapper.find('.edam-label').exists()).toBe(false);
  await opener.trigger('click'); await settle();
  await wrapper.get('button[aria-label="Remove Bioinformatics"]').trigger('click');
  await button('Cancel').trigger('click');
  expect(wrapper.emitted('update:modelValue')).toBeUndefined();
  await opener.trigger('click'); await settle();
  await wrapper.get('button[aria-label="Remove Bioinformatics"]').trigger('click');
  await button('Apply selection').trigger('click');
  expect(wrapper.emitted('update:modelValue')).toEqual([[[]]]);
  await wrapper.setProps({ modelValue: [], disabled: true });
  expect(opener.text()).toBe('Choose topics');
  expect(opener.attributes()).toHaveProperty('disabled');
});

it('retains selected terms outside results and preserves distinct editor payload shapes', async () => {
  const fetcher = vi.fn().mockResolvedValueOnce(success([bio])).mockResolvedValueOnce(success([seq]));
  vi.stubGlobal('fetch', fetcher);
  wrapper = mount(EdamSelector, { props: { ...props, modelValue: [bio.uri] } });
  await flushPromises();
  expect(new URL(fetcher.mock.calls[0][0]).searchParams.get('id')).toBe(bio.uri);
  await begin();
  expect(wrapper.get('[aria-label="Pending selection"]').text()).toContain('Bioinformatics');
  expect(wrapper.get('[role="option"]').text()).toContain('Sequence analysis');
  const data = term('data_0863', 'Sequence');
  expect(edamPayload('data', [data])).toEqual({ data: { uri: data.uri, term: data.term } });
  expect(edamPayload('operation', [bio])).toEqual([{ uri: bio.uri, term: bio.term }]);
  expect(edamPayload('format', [])).toEqual([]);
});

it('ignores a late response after newer input even when transport ignores abort', async () => {
  let release!: (value: ReturnType<typeof success>) => void;
  const stale = new Promise(resolve => { release = resolve; });
  const fetcher = vi.fn().mockResolvedValueOnce(success()).mockReturnValueOnce(stale).mockResolvedValueOnce(success([seq]));
  vi.stubGlobal('fetch', fetcher);
  wrapper = mount(EdamSelector, { props });
  await begin();
  const input = wrapper.get('[role="combobox"]');
  await input.setValue('bio'); await settle(300);
  const signal = fetcher.mock.calls[1][1].signal;
  await input.setValue('sequence');
  expect(signal.aborted).toBe(true);
  expect(wrapper.findAll('[role="option"]')).toHaveLength(0);
  await settle(300);
  release(success([bio])); await flushPromises();
  expect(wrapper.get('[role="option"]').text()).toContain('Sequence analysis');
  expect(wrapper.get('[role="option"]').text()).not.toContain('Bioinformatics');
});

it('supports suggestion hints, empty results, error and retry without changing selection', async () => {
  const fetcher = vi.fn().mockResolvedValueOnce(success([seq], [seq])).mockResolvedValueOnce(success([]))
    .mockResolvedValueOnce({ ok: false, json: async () => ({ error: { message: 'Service unavailable' } }) }).mockResolvedValueOnce(success());
  vi.stubGlobal('fetch', fetcher);
  wrapper = mount(EdamSelector, { props: { ...props, suggestions: [seq.uri] } });
  await begin();
  expect(new URL(fetcher.mock.calls[0][0]).searchParams.get('suggest')).toBe(seq.uri);
  await button('Sequence analysis').trigger('click');
  expect(wrapper.emitted('update:modelValue')).toBeUndefined();
  await settle(300);
  expect(wrapper.text()).toContain('No matching terms');
  await wrapper.get('[role="combobox"]').setValue('another'); await settle(300);
  expect(wrapper.get('[role="alert"]').text()).toContain('Service unavailable');
  await button('Retry lookup').trigger('click'); await settle();
  expect(wrapper.findAll('[role="option"]')).toHaveLength(2);
});

it('disabled/read-only modes prevent mutation and keep read-only form values', async () => {
  const fetcher = vi.fn(); vi.stubGlobal('fetch', fetcher);
  wrapper = mount(EdamSelector, { props: { ...props, modelValue: [bio.uri], initialTerms: [bio], name: 'topic', disabled: true } });
  expect(button('Choose topics').attributes()).toHaveProperty('disabled');
  expect(wrapper.get('input[type="hidden"]').attributes()).toHaveProperty('disabled');
  await wrapper.setProps({ readonly: true, disabled: false });
  expect(wrapper.find('button[aria-label="Remove Bioinformatics"]').exists()).toBe(false);
  expect(wrapper.get('input[type="hidden"]').attributes()).not.toHaveProperty('disabled');
  expect(fetcher).not.toHaveBeenCalled();
});

it('closes on Escape, scope changes and unmount; aborts outstanding requests', async () => {
  const fetcher = vi.fn().mockResolvedValue(success()); vi.stubGlobal('fetch', fetcher);
  wrapper = mount(EdamSelector, { props });
  await begin();
  const input = wrapper.get('[role="combobox"]');
  await input.trigger('keydown', { key: 'Escape' });
  expect(input.attributes('aria-expanded')).toBe('false');
  await input.trigger('keydown', { key: 'Escape' });
  expect(wrapper.get('dialog').element).toHaveProperty('open', false);
  await begin();
  await wrapper.setProps({ scope: 'data' });
  expect(wrapper.get('dialog').element).toHaveProperty('open', false);
  await begin();
  const signal = fetcher.mock.calls.at(-1)![1].signal;
  wrapper.unmount();
  expect(signal.aborted).toBe(true);
});

it('renders markup-like labels as text and enforces the selection limit', async () => {
  const escaped = term('topic_0091', '<img src=x onerror=alert(1)>');
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(success([escaped, seq])));
  wrapper = mount(EdamSelector, { props: { ...props, maxSelections: 1 } });
  await begin();
  expect(wrapper.find('img').exists()).toBe(false);
  await wrapper.findAll('[role="option"]')[0].trigger('click');
  await wrapper.get('[role="option"]').trigger('click');
  await nextTick();
  expect(wrapper.text()).toContain('Selection limit reached');
  await button('Apply selection').trigger('click');
  expect(wrapper.emitted('update:modelValue')).toEqual([[[escaped.uri]]]);
});

it('invalidates cached labels after vocabulary activation while preserving selected URIs', async () => {
  const updated = { ...bio, term: 'Activated label', obsolete: true };
  const revision = (items: EdamTerm[], value: string) => ({ ok: true,
    json: async () => ({ items, more: false, suggestions: [], vocabulary: { revision: value } }) });
  const fetcher = vi.fn().mockResolvedValueOnce(revision([bio], 'before'))
    .mockResolvedValueOnce(revision([seq], 'after')).mockResolvedValue(revision([updated], 'after'));
  vi.stubGlobal('fetch', fetcher);
  wrapper = mount(EdamSelector, { props: { ...props, modelValue: [bio.uri] } });
  await flushPromises();
  expect(wrapper.get('[aria-label="Topics"]').text()).toContain('Bioinformatics');
  await begin();
  await flushPromises();
  expect(wrapper.get('[aria-label="Topics"]').text()).toContain('Activated label');
  expect(wrapper.get('[aria-label="Topics"]').text()).toContain('(obsolete)');
  expect(wrapper.emitted('update:modelValue')).toBeUndefined();
  expect(fetcher.mock.calls.at(-1)![1].cache).toBe('no-store');
});
