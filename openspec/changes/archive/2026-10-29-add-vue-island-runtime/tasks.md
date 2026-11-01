## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect the modern asset pipeline

- [x] 1.1 Reuse the existing Vite/modern asset package and Django manifest integration; if absent, add the minimum compatible Vite package rather than modifying Bower/Gulp.
- [x] 1.2 Add Vue 3, TypeScript, Vue Vite integration, `vue-tsc`, Vitest and Vue Test Utils with locked versions.
- [x] 1.3 Add documented development, production build, type-check and unit-test commands.

## 2. Implement generic island mounting

- [x] 2.1 Define an explicit DOM convention for Vue root name and initial-props reference.
- [x] 2.2 Implement a typed component/application registry and idempotent root scanner.
- [x] 2.3 Implement safe Django-to-Vue initial JSON data transfer using an escaping-safe mechanism.
- [x] 2.4 Track mounted application instances by root so they can be deterministically unmounted.

## 3. Integrate with htmx lifecycle

- [x] 3.1 Inspect the installed htmx version/events and mount new Vue roots after complete fragment insertion.
- [x] 3.2 Unmount applications before htmx removes/replaces their root elements.
- [x] 3.3 Document correct ownership examples and explicitly prohibit htmx targets inside mounted Vue roots.

## 4. Demonstrate and test

- [x] 4.1 Add a small typed demo island that accepts server props and can appear multiple times on one page.
- [x] 4.2 Unit-test initial mount, multiple roots, duplicate scan prevention, prop parsing and unmount.
- [x] 4.3 Add a browser test where htmx inserts/replaces a fragment containing a Vue root repeatedly without duplicate behavior or stale instances.
- [x] 4.4 Run modern frontend build, type-check, unit tests and relevant Django/browser tests.

## Completion evidence

Accepted 2026-09-14 on develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
The preceding baseline refresh is complete. The existing modern Vite package,
Django manifest and isolated HTML mount were reused; legacy/API routing is unchanged.

See [runtime conventions, commands and verification](../../../../docs/frontend-migration/vue-island-runtime.md).
Vue roots use Django-escaped JSON inside inert templates, preserving htmx's
`allowScriptTags=false` policy. Mounting follows `htmx:load`; teardown uses
`htmx:beforeCleanupElement`, including direct-root and containing-fragment swaps.

Clean install, production build, type-check and 11 unit tests passed. All 51
focused Django tests passed on both backend runtimes and all 23 browser tests
passed through each proxy. Final demo screenshots were inspected on desktop/mobile.
The final spacing-only template change also passed four browser and 28 Django
checks. No router, shared store, search/editor feature or visual redesign was added.
