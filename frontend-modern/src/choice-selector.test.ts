import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import ChoiceSelector from './ChoiceSelector.vue';
let wrapper: VueWrapper;
beforeEach(() => {
  vi.useFakeTimers();
  Object.defineProperty(HTMLDialogElement.prototype, 'showModal', { configurable: true, value: function (this: HTMLDialogElement) { this.open = true; } });
  Object.defineProperty(HTMLDialogElement.prototype, 'close', { configurable: true, value: function (this: HTMLDialogElement) { this.open = false; } });
});
afterEach(() => {
  wrapper?.unmount(); vi.useRealTimers(); vi.unstubAllGlobals();
  Reflect.deleteProperty(HTMLDialogElement.prototype, 'showModal'); Reflect.deleteProperty(HTMLDialogElement.prototype, 'close');
});
it('searches the full choice list and selects the matching value', async () => {
  const choices = Array.from({ length: 100 }, (_, i) => ({ value: `id-${i}`, label: `Choice ${i}` }));
  wrapper = mount(ChoiceSelector, { props: { modelValue: '', label: 'License', choices } });
  await wrapper.get('.choice-opener').trigger('click');
  await wrapper.get('input[type="search"]').setValue('Choice 99');
  expect(wrapper.findAll('.choice-list button')).toHaveLength(1);
  await wrapper.get('.choice-list button').trigger('click');
  expect(wrapper.emitted('update:modelValue')).toEqual([['id-99']]);
  expect(wrapper.get('dialog').element.open).toBe(false);
});
it('searches remote names and ignores stale responses', async () => {
  let release!: (value: unknown) => void;
  const stale = new Promise(resolve => { release = resolve; });
  const fetcher = vi.fn().mockReturnValueOnce(stale).mockResolvedValueOnce({ ok: true, json: async () => ({ items: [{ value: 'New', label: 'New' }] }) });
  vi.stubGlobal('fetch', fetcher);
  wrapper = mount(ChoiceSelector, { props: { modelValue: '', label: 'Collections', endpoint: '/options/', field: 'collectionID' } });
  await wrapper.get('.choice-opener').trigger('click');
  await wrapper.get('input[type="search"]').setValue('old');
  await vi.advanceTimersByTimeAsync(300);
  await wrapper.get('input[type="search"]').setValue('new');
  await vi.advanceTimersByTimeAsync(300); await flushPromises();
  release({ ok: true, json: async () => ({ items: [{ value: 'Old', label: 'Old' }] }) });
  await flushPromises();
  expect(wrapper.get('.choice-list').text()).toBe('New');
  await wrapper.get('.choice-list button').trigger('click');
  expect(wrapper.emitted('update:modelValue')).toEqual([['New']]);
});
