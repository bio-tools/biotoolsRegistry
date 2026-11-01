# Vue island runtime

Implemented on upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`, after
`refresh-develop-migration-baseline`. The impact-matrix requirement is to reuse
the accepted Vite/manifest pipeline and test safe props and htmx lifecycle on
that shell. No legacy Gulp, API, authentication, proxy or canonical routes change.

Preview: <http://localhost:8003/_migration/html/islands/> (Apache), or
<https://localhost:8443/_migration/html/islands/> (Caddy, local certificate).
The two counters are disposable client state, not registry data. Reset counters
replaces their containing fragment; Reset first counter replaces one root.
Without JavaScript, Django renders the initial values and ordinary GET forms.

## Root and data convention

Register compiled components in `frontend-modern/src/main.js`. The typed runtime
accepts a component-name registry; each declared root gets a separate Vue App.
Unknown names, nested roots and repeated scans do not mount extra applications.
Pages with no declared roots retain server ownership of their DOM.

Use Django's `json_script` filter, never serialized JSON in attributes or `safe`:

```django
<section id="results">
  <template id="counter-props">{{ counter_props|json_script }}</template>
  <div id="counter" data-vue-island="counter-demo"
       data-vue-props="counter-props" hx-disable>
    <p>{{ counter_props.label }}: {{ counter_props.initial }}</p>
  </div>
</section>
```

`data-vue-props` references a unique document ID, not a selector or JSON value.
The referenced template must contain an `application/json` script with an object.
Omitting the attribute supplies `{}`. Missing/malformed containers and non-object
JSON are reported to the console; fallback HTML remains and other roots still
mount. Component-specific field validation belongs with the owning view/component;
TypeScript alone does not validate external data. Never pass secrets as props.

The inert template preserves Django's escaped JSON through htmx 2.0.10, whose
`makeFragment` strips script elements when `allowScriptTags=false` but does not
traverse template contents. Only `textContent` is parsed; the template is never
inserted as executable DOM. Keep `allowScriptTags=false` and `allowEval=false`.
These settings and fragment escaping are covered by actual-browser tests.

## Ownership and lifecycle

Django owns pages and routes. Vue owns only descendants of explicit roots.
Use `hx-disable` on every island root; do not put htmx controls inside Vue trees.
The runtime listens to `htmx:load` after fragment insertion/processing, and
`htmx:beforeCleanupElement` to call `app.unmount()` before roots are discarded.
Mounting on `afterSwap` alone is too early for a directly swapped `hx-disable`
root: htmx processes it during settling and would immediately clean it up.

Allowed ownership examples:

- An external htmx form replaces `#results` with `hx-swap="outerHTML"`, including
  its props templates and complete Vue roots. `innerHTML` on this server-owned
  wrapper is also valid.
- An external form replaces `#counter` itself with `hx-swap="outerHTML"`. Its
  referenced props must remain available, or be included in the replacement.
- Vue uses child components for its own internal controls and renders escaped text.

Prohibited: an htmx target **inside** a Vue root, or `innerHTML` replacement of
the root's Vue-owned children. Do not nest independent island roots, use morph or
`hx-preserve` for mounted roots, or remove them with uncoordinated DOM code. For
non-htmx removal, call `runtime.unmount(container)` first. `runtime.stop()` removes
runtime listeners and unmounts all tracked apps. Component authors must release
their own external listeners/timers in Vue teardown hooks.

This runtime does not implement routing, hydration, shared stores, search,
editing, asynchronous component discovery or visual redesign. No Vue Router or
Pinia is installed. Existing detail pages still omit JavaScript entirely.

## Build and verification

Use Node 22.12+; versions are pinned in `frontend-modern/package.json` and its
lockfile. From `frontend-modern/`:

```sh
npm ci
npm run type-check
npm test
npm run build
npm run dev
```

The last command is the optional persistent Vite build watcher. No Vite HTTP
server is needed. Build and collect static assets before serving the Django
preview; the existing manifest tag now also emits Vue component CSS.

From the develop checkout, use the isolated stack described in
[the develop runbook](develop-refresh.md#run-and-verify):

```sh
docker compose -f compose.refresh.json exec -T backend python manage.py test elixirapp.test_islands elixirapp.test_html elixirapp.test_htmx --noinput
docker compose -f compose.refresh.json exec -T -u 0 backend python manage.py collectstatic --noinput
docker compose -f compose.refresh.json restart apache
cd tests/browser
BIOTOOLS_BASE_URL=http://localhost:8003 BIOTOOLS_TEST_ISLANDS=1 npm test -- islands.spec.js
```

Set `PLAYWRIGHT_BROWSERS_PATH` if using a nondefault Chromium cache. For Caddy,
use `BIOTOOLS_BASE_URL=https://localhost:8443 BIOTOOLS_TEST_LOCAL_TLS=1`.
The focused island tests need no account, seed or Elasticsearch fixture.

Unit coverage checks multiple/idempotent mounts, unknown/nested roots, object
props validation and text escaping, teardown before removal, stopped listeners,
and independent demo interactions. Django tests cover full/fragment/history
responses, safe serialization, read-only methods, fallback and CSS manifests.
Browser coverage checks repeated wrapper/direct-root swaps, real Vue teardown
hooks, new insertion, markup-like props, keyboard interaction, reload, disabled
JavaScript, component CSS, branding and desktop/mobile overflow.

## Rollback and limitations

Remove the `islands/` route and demo templates, plus the registry bootstrap/imports
in `main.js`, then rebuild and collect assets. Keep the shared htmx package and
earlier migration pages. No database rollback or route cutover is involved.

This validates the generic runtime, not future editor/search workflows or their
authorization. Existing production-provider/Rendertron limitations in the develop
baseline remain unchanged. htmx's upstream build-time eval warning remains visible;
runtime eval stays disabled. The test DOM's transitive `whatwg-encoding` deprecation
does not affect the browser bundle.

## Validation record

Accepted 2026-09-14 on the pinned develop revision above:

- Node 22.23.2; Vue 3.5.42, Vite 8.2.2, Vue Vite plugin 6.0.9, TypeScript 5.9.3,
  vue-tsc 3.3.11, Vitest 5.0.0, Vue Test Utils 2.5.0 and jsdom 26.1.0.
- Clean `npm ci --ignore-scripts`, type-check, 11 unit tests and production build
  passed. npm reported zero vulnerabilities. An offline install first failed
  because the existing Vite archive was absent from the cache; network install
  succeeded, followed by the passing checks. Rebuilds produced identical hashes.
- JavaScript: 141.51 kB (44.83 kB gzip); component CSS: 0.37 kB. The manifest,
  JavaScript and CSS were collected and served through both preview proxies.
- All 51 focused migration backend tests passed on both Python 3.13 and Apache's
  Python 3.10 runtime, using Django 5.2.11. This includes the existing detail,
  query-contract and isolated live-Elasticsearch cases, plus four island tests.
  Existing MySQL conditional-constraint and naive timestamp warnings remain.
- All 23 browser scenarios passed on Apache HTTP and Caddy HTTPS, including
  authenticated legacy navigation; no skips or retries. Each enhanced island
  viewport checks five whole-fragment swaps and three direct-root replacements.
  Vue teardown hooks confirmed old instances unmounted while still connected.
- After the final template-only control-spacing adjustment, all four island
  browser tests and 28 shell/htmx/island Django tests passed again. Final 1440px
  and 390px screenshots were inspected for spacing, focus, logo, blue branding,
  loaded component CSS and overflow.
- Strict OpenSpec validation and whitespace checks passed. No legacy application
  files or existing records were changed by this runtime change.

References: [Vue applications](https://vuejs.org/api/application.html),
[Vue TypeScript tooling](https://vuejs.org/guide/typescript/overview.html),
[htmx lifecycle events](https://htmx.org/events/),
[Django json_script](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#json-script).
