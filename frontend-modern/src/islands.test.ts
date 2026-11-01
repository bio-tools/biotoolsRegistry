import { afterEach, describe, expect, it, vi } from 'vitest';
import { defineComponent, h, nextTick, onUnmounted } from 'vue';
import { mount } from '@vue/test-utils';
import CounterDemo from './CounterDemo.vue';
import { createIslandRuntime } from './islands';

const runtime = createIslandRuntime({ counter: CounterDemo });

function root(id: string, props = '{"label":"Counter","initial":3}', name = 'counter') {
  const container = document.createElement('section');
  const template = document.createElement('template');
  template.id = `${id}-props`;
  const script = document.createElement('script');
  script.type = 'application/json';
  script.textContent = props;
  template.content.append(script);
  const element = document.createElement('div');
  element.id = id;
  element.dataset.vueIsland = name;
  element.dataset.vueProps = template.id;
  element.textContent = 'Fallback';
  container.append(template, element);
  document.body.append(container);
  return element;
}

afterEach(() => {
  runtime.stop();
  document.body.replaceChildren();
  vi.restoreAllMocks();
});

describe('island runtime', () => {
  it('leaves unrelated, unknown and nested roots alone', () => {
    document.body.innerHTML = '<p>Ordinary HTML</p>';
    runtime.mount();
    expect(document.body.innerHTML).toBe('<p>Ordinary HTML</p>');
    const unknown = root('unknown', '{}', 'toString');
    const nested = root('nested');
    unknown.append(nested);
    runtime.mount();
    expect(unknown.textContent).toBe('FallbackFallback');
    expect(document.querySelector('output')).toBeNull();
  });

  it('mounts independent roots once, including a scan of a root itself', async () => {
    const first = root('first');
    const second = root('second', '{"label":"Second","initial":7}');
    runtime.mount(first);
    const firstButton = first.querySelector('button');
    runtime.mount();
    runtime.mount();
    expect(first.querySelector('button')).toBe(firstButton);
    first.querySelectorAll('button')[1].click();
    await nextTick();
    expect(first.querySelector('output')?.textContent).toBe('4');
    expect(second.querySelector('output')?.textContent).toBe('7');
  });

  it('treats markup-like props as text', () => {
    const label = '</script></template><img src=x onerror=alert(1)> & "text"';
    const element = root('safe', JSON.stringify({ label, initial: 2 }));
    runtime.mount();
    expect(element.querySelector('h2')?.textContent).toBe(label);
    expect(document.querySelector('img')).toBeNull();
  });

  it.each(['{', 'null', '[]', '42', '"text"'])('keeps fallback on invalid props %s, without blocking other roots', props => {
    const report = vi.spyOn(console, 'error').mockImplementation(() => {});
    const invalid = root('invalid', props);
    const valid = root('valid');
    runtime.mount();
    expect(invalid.textContent).toBe('Fallback');
    expect(valid.querySelector('output')?.textContent).toBe('3');
    expect(report).toHaveBeenCalledOnce();
  });

  it('rejects missing or executable containers and permits omitted props', () => {
    const report = vi.spyOn(console, 'error').mockImplementation(() => {});
    const element = root('missing');
    document.getElementById('missing-props')?.remove();
    runtime.mount();
    const script = document.createElement('script');
    script.id = 'missing-props';
    script.type = 'application/json';
    script.textContent = '{}';
    document.body.append(script);
    runtime.mount();
    expect(element.textContent).toBe('Fallback');
    expect(report).toHaveBeenCalledTimes(2);
    const noProps = createIslandRuntime({ empty: defineComponent({ render: () => h('p', 'No props') }) });
    element.dataset.vueIsland = 'empty';
    delete element.dataset.vueProps;
    noProps.mount();
    expect(element.textContent).toBe('No props');
    noProps.stop();
  });

  it('bridges insertion and cleanup once, unmounts before removal, and detaches listeners on stop', () => {
    const cleanups = vi.fn();
    const tracked = defineComponent({
      setup() {
        onUnmounted(() => cleanups(document.getElementById('tracked')?.isConnected));
        return () => h('p', 'Mounted');
      },
    });
    const bridge = createIslandRuntime({ tracked });
    bridge.start();
    bridge.start();
    document.dispatchEvent(new Event('DOMContentLoaded'));
    const element = root('tracked', '{}', 'tracked');
    element.dispatchEvent(new CustomEvent('htmx:load', { bubbles: true }));
    element.dispatchEvent(new CustomEvent('htmx:load', { bubbles: true }));
    expect(element.textContent).toBe('Mounted');
    element.parentElement?.dispatchEvent(new CustomEvent('htmx:beforeCleanupElement', { bubbles: true }));
    element.dispatchEvent(new CustomEvent('htmx:beforeCleanupElement', { bubbles: true }));
    expect(cleanups).toHaveBeenCalledExactlyOnceWith(true);
    element.parentElement?.remove();
    const replacement = root('tracked', '{}', 'tracked');
    replacement.dispatchEvent(new CustomEvent('htmx:load', { bubbles: true }));
    expect(replacement.textContent).toBe('Mounted');
    bridge.stop();
    expect(cleanups).toHaveBeenCalledTimes(2);
    replacement.textContent = 'Stopped';
    replacement.dispatchEvent(new CustomEvent('htmx:load', { bubbles: true }));
    expect(replacement.textContent).toBe('Stopped');
  });
});

it('demo uses typed server props and one update per button activation', async () => {
  const component = mount(CounterDemo, { props: { label: 'Example', initial: 7 } });
  expect(component.get('h2').text()).toBe('Example');
  await component.get('[title="Increase"]').trigger('click');
  expect(component.get('output').text()).toBe('8');
  await component.get('[title="Decrease"]').trigger('click');
  expect(component.get('output').text()).toBe('7');
  component.unmount();
});
