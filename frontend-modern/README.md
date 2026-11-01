# Modern browser assets

Validated on upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
Use the [develop runbook](../docs/frontend-migration/develop-refresh.md#run-and-verify)
for the current Docker services, preview and verification results.

This isolated Vite package supplies Django migration pages. It does not use or
modify the Node 11/Bower/Gulp package in `frontend/`. Vue 3 islands and htmx share
this package; do not introduce another asset pipeline.

Use Node 22.12+ (validated with 22.23.2). From this directory:

```sh
npm ci
npm run build
npm run type-check
npm test
# Rebuild on changes; reload the Django page after each build.
npm run dev
```

The watch command writes production-format files directly into Django's static
source tree. There is no separate Vite HTTP server or cross-origin development
script. Run the [Django shell stack](../docs/frontend-migration/django-html-shell.md)
alongside it. `vue-tsc` checks TypeScript and Vue single-file components; Vitest
and Vue Test Utils run the unit tests in jsdom. The existing JS entry point and
manifest key remain unchanged. There is no lint command.

## Deployment

Run `npm ci` and `npm run build` **before building the backend image**, then run
the existing `collectstatic --noinput` step. The backend Dockerfile copies
`backend/elixir/`, including the generated `static/modern/` directory. Ship that
source directory and its manifest along with the collected files. Neither Node
nor a runtime CDN is needed by Django.

The Vite build produces `backend/elixir/static/modern/manifest.json` and
content-hashed `assets/main-*.js` and component CSS. The `modern_script` template
tag reads the manifest on each full-page render, emits its CSS links and module
script, and uses Django's configured `STATIC_URL`.
The manifest has a non-hidden name so `collectstatic` includes it. Generated
files and `node_modules` are ignored; commit the package lockfile instead.

Publish assets before switching application code/manifests, and retain the
previous deployment's hashed assets while old pages can still reference them.
Do not use `collectstatic --clear` against a shared live static directory during
a rolling deployment. Build into an isolated checkout: Vite clears its output
directory on rebuild. Hashing makes the JS safe for immutable caching; ordinary
shell CSS retains the existing deployment cache policy.

Without a manifest, Django deliberately omits the script and serves the native
HTML fallback. A malformed manifest is a build/deployment error, not silently
ignored. The 500 template omits scripts so asset failures cannot break its render.

Vite currently warns about upstream htmx's direct `eval`. The application sets
`allowEval = false` and `allowScriptTags = false`; do not add inline evaluated
htmx expressions. The warning is left visible rather than suppressed.

See [Vite backend integration](https://vite.dev/guide/backend-integration) and
the project's [interaction conventions](../docs/frontend-migration/htmx-progressive-enhancement.md).
For explicit roots, safe props and lifecycle ownership, see the
[Vue island runtime convention](../docs/frontend-migration/vue-island-runtime.md).
