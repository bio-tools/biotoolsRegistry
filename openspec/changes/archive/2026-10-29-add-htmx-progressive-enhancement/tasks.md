## 0. Develop baseline

- [x] 0.1 Revalidate this change on pinned upstream develop as part of `refresh-develop-migration-baseline`; preserve the completed items below as old-baseline evidence.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

Develop evidence (2026-09-13): upstream `9faec5b3b660498fdef9736e65e331728b55f99c`,
preserved in `develop-migration/`. The [refresh record](../../../../docs/frontend-migration/develop-refresh.md)
covers the 41-state inventory, current authentication/editor/search deltas, both
asset builds, 24 Django tests on each runtime, 16 browser tests on each proxy,
57 API/permission tests, screenshots and exercised rollback. No browser skips or
retries. Real ORCID/email and legacy Rendertron remain later deployment gates.

## 1. Inspect and establish the modern asset package

- [x] 1.1 Inspect existing npm/Vite/static-file tooling and reuse it if compatible; otherwise create one isolated modern asset package without changing the legacy Bower/Gulp build.
- [x] 1.2 Add pinned stable htmx 2.x and configure production build output with cache-safe asset naming/manifest integration for Django.
- [x] 1.3 Add documented install, development and production-build commands.

## 2. Establish htmx conventions

- [x] 2.1 Add a project helper/convention for detecting htmx requests without duplicating domain logic.
- [x] 2.2 Define naming/layout conventions for complete templates and fragment templates.
- [x] 2.3 Define shared behavior for loading indicators, request errors, history updates and session/CSRF-safe mutations.
- [x] 2.4 Document that htmx targets must never point inside a mounted Vue-owned root.

## 3. Add a demonstration interaction

- [x] 3.1 Implement a small non-domain GET interaction that works through ordinary navigation/form submission and performs a fragment swap when htmx is active.
- [x] 3.2 If a mutation example is added, protect it with Django CSRF and test the failure case. No mutation added; HX-header CSRF rejection/success additionally checked on the existing native session form.

## 4. Test and verify

- [x] 4.1 Add Django tests proving normal requests return complete pages and htmx requests return the expected fragment where applicable.
- [x] 4.2 Add a small browser test for the enhanced interaction and direct-request fallback.
- [x] 4.3 Run backend tests plus modern frontend build/type/lint commands that exist at this stage. Final verification passed after restoring the temporary environment: 21 focused Django tests, 14 browser runs and the Vite build. No modern type/lint scripts exist. Database/proxy environment limits are recorded in docs/frontend-migration/htmx-progressive-enhancement.md.
