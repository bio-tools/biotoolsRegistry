## 0. Develop baseline

- [x] 0.1 Revalidate this change on pinned upstream develop as part of `refresh-develop-migration-baseline`; preserve the completed items below as old-baseline evidence.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

Develop evidence (2026-09-13): upstream `9faec5b3b660498fdef9736e65e331728b55f99c`,
preserved in `develop-migration/`. The [refresh record](../../../../docs/frontend-migration/develop-refresh.md)
covers the 41-state inventory, current authentication/editor/search deltas, both
asset builds, 24 Django tests on each runtime, 16 browser tests on each proxy,
57 API/permission tests, screenshots and exercised rollback. No browser skips or
retries. Real ORCID/email and legacy Rendertron remain later deployment gates.

## 1. Inspect existing test infrastructure

- [x] 1.1 Identify existing JavaScript/browser test tooling, CI jobs, development fixtures and documented local startup commands.
- [x] 1.2 Reuse compatible Playwright infrastructure if already present; otherwise add the minimum Playwright setup and lock dependencies reproducibly.

## 2. Build the browser harness

- [x] 2.1 Add a configurable base URL and documented environment variables for local/deployed execution.
- [x] 2.2 Configure useful failure artifacts such as trace, screenshot and console/network diagnostics.
- [x] 2.3 Add fixture/setup helpers without coupling tests to AngularJS implementation objects.

## 3. Add critical regression flows

- [x] 3.1 Test loading the public search/home experience and executing a text search.
- [x] 3.2 Test at least one filter plus sorting or pagination and assert the resulting URL/state.
- [x] 3.3 Test opening a tool detail page from search and directly via a deep link.
- [x] 3.4 Test refresh and browser Back/Forward for a stateful search URL.
- [x] 3.5 Add login/logout/protected-route coverage if deterministic test credentials or fixtures are available; otherwise document the blocker explicitly.

## 4. CI and documentation

- [x] 4.1 Add documented commands for installing browser dependencies and running focused/full browser tests.
- [x] 4.2 Integrate the smoke suite into CI where the required services/fixtures are available, or document the exact missing prerequisite.
- [x] 4.3 Run the suite against the current implementation and record any pre-existing failures without changing behavior to hide them.

## Completion evidence

- Harness, pinned lockfile, fixtures, six scenarios and environment/CI instructions: `tests/browser/`.
- Baseline: checkout `a1fc8b94067f33bc9047efc9c75ebe1579365a07` frontend served unchanged through a temporary GET-only public API proxy; final repeated suite: 10 passed, 2 authentication skips, zero retries.
- No running local stack or maintained seed; no dedicated authentication credentials. Exact prerequisites and the directly deployed autocomplete HTTP 500 observed during validation are recorded in `tests/browser/README.md`.
- Failure screenshots, traces and browser console/network attachments verified. No production application files changed.
- Reproducible install, test discovery, invalid configuration checks and strict OpenSpec validation passed.
