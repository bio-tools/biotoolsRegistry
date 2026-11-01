import { createApp, type App, type Component } from 'vue';

const selector = '[data-vue-island]';

function readProps(root: HTMLElement): Record<string, unknown> {
  const id = root.dataset.vueProps;
  if (!id) return {};
  const container = root.ownerDocument.getElementById(id);
  const script = container instanceof HTMLTemplateElement
    ? container.content.querySelector('script[type="application/json"]') : null;
  if (!script) throw new Error(`Missing JSON props template: ${id}`);
  const props: unknown = JSON.parse(script.textContent || '');
  if (props === null || typeof props !== 'object' || Array.isArray(props)) {
    throw new Error('Island props must be a JSON object');
  }
  return props as Record<string, unknown>;
}

export function createIslandRuntime(components: Readonly<Record<string, Component>>) {
  const applications = new Map<HTMLElement, App>();
  let nextId = 0;

  function mount(scope: ParentNode = document) {
    const roots = [...scope.querySelectorAll<HTMLElement>(selector)];
    if (scope instanceof HTMLElement && scope.matches(selector)) roots.unshift(scope);
    for (const root of roots) {
      const name = root.dataset.vueIsland || '';
      if (!root.isConnected || applications.has(root) || root.parentElement?.closest(selector) ||
          !Object.hasOwn(components, name)) continue;
      try {
        const app = createApp(components[name], readProps(root));
        app.config.idPrefix = `island-${nextId++}`;
        app.mount(root);
        applications.set(root, app);
      } catch (error) {
        console.error(`Could not mount Vue island "${name}"`, error);
      }
    }
  }

  function unmount(scope: ParentNode) {
    for (const [root, app] of applications) {
      if (scope === root || scope.contains(root)) {
        applications.delete(root);
        app.unmount();
      }
    }
  }

  function afterLoad(event: Event) {
    if (event.target instanceof Element) mount(event.target);
  }

  function beforeCleanup(event: Event) {
    if (event.target instanceof Element) unmount(event.target);
  }

  let started = false;
  function start() {
    if (started) return;
    started = true;
    // htmx:load follows processing, including cleanup of hx-disable roots.
    document.addEventListener('htmx:load', afterLoad);
    document.addEventListener('htmx:beforeCleanupElement', beforeCleanup);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialMount, { once: true });
    else mount();
  }

  function initialMount() { mount(); }

  function stop() {
    document.removeEventListener('DOMContentLoaded', initialMount);
    document.removeEventListener('htmx:load', afterLoad);
    document.removeEventListener('htmx:beforeCleanupElement', beforeCleanup);
    for (const root of applications.keys()) unmount(root);
    started = false;
  }

  return { mount, unmount, start, stop };
}
