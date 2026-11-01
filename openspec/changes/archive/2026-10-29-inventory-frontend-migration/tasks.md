## 0. Develop baseline

- [x] 0.1 Revalidate this change on pinned upstream develop as part of `refresh-develop-migration-baseline`; preserve the completed items below as old-baseline evidence.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

Develop evidence (2026-09-13): upstream `9faec5b3b660498fdef9736e65e331728b55f99c`,
preserved in `develop-migration/`. The [refresh record](../../../../docs/frontend-migration/develop-refresh.md)
covers the 41-state inventory, current authentication/editor/search deltas, both
asset builds, 24 Django tests on each runtime, 16 browser tests on each proxy,
57 API/permission tests, screenshots and exercised rollback. No browser skips or
retries. Real ORCID/email and legacy Rendertron remain later deployment gates.

## 1. Repository reconnaissance

- [x] 1.1 Record the inspected commit SHA, active frontend/backend entry points, build files, route configuration, reverse-proxy configuration and test infrastructure.
- [x] 1.2 Enumerate all user-facing frontend routes and identify the controller/component/directive/template chain for each.
- [x] 1.3 Enumerate frontend API calls and map them to routes/features, including authentication and mutation calls.

## 2. Behavior inventory

- [x] 2.1 Create `docs/frontend-migration/routes.md` covering URL parameters, deep links, authentication, mutations and important states for every route.
- [x] 2.2 Create `docs/frontend-migration/api-usage.md` mapping observed API endpoints to frontend callers and payload transformations.
- [x] 2.3 Create `docs/frontend-migration/editor-behavior.md` covering nested fields, EDAM handling, validation, reordering, defaults and pre-submit transformations.
- [x] 2.4 Create `docs/frontend-migration/search-behavior.md` covering filtering, sorting, pagination, result display options and browser-history behavior.

## 3. Architecture and risks

- [x] 3.1 Add an ADR defining Django/htmx/Vue ownership, the Vue-owned search workspace, the Vue-owned editor subtree and public API compatibility.
- [x] 3.2 Create `docs/frontend-migration/risk-register.md` with evidence, uncertainty and proposed regression coverage for high-risk behaviors.
- [x] 3.3 Classify existing interactions as plain Django, htmx, Vue or legacy-until-later and record the rationale.

## 4. Verification

- [x] 4.1 Cross-check the route inventory against router configuration and navigation links so no known route is omitted.
- [x] 4.2 Cross-check API usage against frontend service/request code and document orphaned or uncertain calls separately.
- [x] 4.3 Confirm the change contains no runtime behavior modifications and summarize unresolved questions.

## Completion evidence

- Source baseline: `a1fc8b94067f33bc9047efc9c75ebe1579365a07`, inspected 2026-09-09.
- Six documents in `docs/frontend-migration/`; ADR: `adr-001-frontend-ownership.md`.
- Static checks cover all 40 router states, all 66 declared search parameters, source links and commit/date stamps; navigation and request callers cross-checked against their definitions.
- `openspec validate inventory-frontend-migration --strict --no-interactive` passed.
- Only documentation and this task checklist were edited. Existing unrelated workspace changes were preserved.
- No live browser/API tests performed. Deployment routing, runtime auth/recovery, data round trips and uncovered route-family migration decisions remain explicit questions in `risk-register.md`.
