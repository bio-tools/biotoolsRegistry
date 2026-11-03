import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { flushPromises } from '@vue/test-utils';
import source from './home-search.js?raw';

beforeEach(() => {
  vi.useFakeTimers();
  document.body.innerHTML = '<form data-home-search data-edam-url="/_edam/terms/"><input id="home-query"><ul id="home-suggestions" hidden></ul><p id="home-suggestion-status"></p></form>';
  Object.defineProperty(Element.prototype, 'scrollIntoView', { configurable: true, value: vi.fn() });
});
afterEach(() => {
  document.body.replaceChildren(); vi.useRealTimers(); vi.unstubAllGlobals();
  Reflect.deleteProperty(Element.prototype, 'scrollIntoView');
});
const response = (scope: string, term: string) => ({ ok: true, json: async () => ({ items: [{ uri: `http://edamontology.org/${scope}_1929`, term }] }) });
function input(value: string) {
  const field = document.querySelector<HTMLInputElement>('#home-query')!;
  field.value = value; field.dispatchEvent(new Event('input', { bubbles: true }));
  return field;
}
it('offers grouped concept links, preserves text safely and supports keyboard navigation', async () => {
  vi.stubGlobal('fetch', vi.fn((url: URL) => Promise.resolve(response(url.searchParams.get('scope')!, '<FASTA>'))));
  new Function(source)();
  const field = input('fasta');
  await vi.advanceTimersByTimeAsync(350); await flushPromises();
  const options = document.querySelectorAll<HTMLAnchorElement>('[role="option"]');
  expect(options).toHaveLength(4);
  expect(options[3].textContent).toContain('Format<FASTA>');
  expect(options[3].getAttribute('href')).toBe('/t?dataFormatID=%22format_1929%22');
  expect(document.querySelector('#home-suggestions img')).toBeNull();
  field.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }));
  expect(field.getAttribute('aria-activedescendant')).toBe(options[3].id);
  field.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  expect(field.getAttribute('aria-expanded')).toBe('false');
});
it('ignores stale responses and allows plain search when lookup fails', async () => {
  const releases: ((value: unknown) => void)[] = [];
  const fetcher = vi.fn((url: URL) => releases.length < 4
    ? new Promise(resolve => { releases.push(resolve); })
    : Promise.resolve(response(url.searchParams.get('scope')!, 'New result')));
  vi.stubGlobal('fetch', fetcher);
  new Function(source)();
  input('old'); await vi.advanceTimersByTimeAsync(350);
  input('new'); await vi.advanceTimersByTimeAsync(350); await flushPromises();
  releases.forEach((resolve, i) => resolve(response(['topic', 'operation', 'data', 'format'][i], 'Old result')));
  await flushPromises();
  expect(document.querySelector('#home-suggestions')!.textContent).toContain('New result');
  expect(document.querySelector('#home-suggestions')!.textContent).not.toContain('Old result');
  fetcher.mockRejectedValue(new Error('offline'));
  input('offline'); await vi.advanceTimersByTimeAsync(350); await flushPromises();
  expect(document.querySelector('#home-suggestion-status')!.textContent).toContain('still search by text');
  expect(document.querySelector<HTMLFormElement>('form')!.getAttribute('data-home-search')).not.toBeNull();
});
