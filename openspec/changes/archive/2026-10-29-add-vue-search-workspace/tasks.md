## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect current search behavior and services

- [x] 1.0 Characterize develop page-size controls (10/25/50/100), per_page URL refresh/history, Cards/Table and Added/Updated columns; test malformed page/size inputs independently of supported query parity.

- [x] 1.1 Trace legacy search query parameters, facets, result fields, sorting, pagination, display options and URL/history behavior.
- [x] 1.2 Reuse the shared Python search service and Vue runtime if present; if absent, add only minimum compatible infrastructure within the target architecture.
- [x] 1.3 Define representative search fixtures/queries for parity and performance checks.

## 2. Define the frontend search contract

- [x] 2.1 Define typed request parameters for text query, primary filters, sorting and pagination/cursor state.
- [x] 2.2 Define a compact response DTO containing result summaries, server-authoritative total/count metadata, facets and pagination/cursor information.
- [x] 2.3 Add a frontend-oriented Django endpoint backed by the shared search service without changing the existing public REST API response contract.
- [x] 2.4 Validate unknown/invalid filter and pagination values and return a typed recoverable error response.

## 3. Implement the Vue search application

- [x] 3.1 Add a Django-owned search page with a single Vue-owned search root and safe initial configuration.
- [x] 3.2 Implement text query, current primary facets/filters, sorting and pagination/cursor navigation.
- [x] 3.3 Implement a central URL parse/normalize/serialize module and synchronize result-defining state without Vue Router.
- [x] 3.4 Implement loading, empty, error and retry states plus debounced text requests and stale-request cancellation/ignoring.
- [x] 3.5 Render compact result cards/items with stable links to resource details and hooks for later selection/comparison features.
- [x] 3.6 Ensure no htmx target or swap operates inside the mounted search root.

## 4. Test search semantics and browser behavior

- [x] 4.1 Backend-test request validation, facets, result ordering, pagination/cursor and representative search parity with existing semantics.
- [x] 4.2 Unit-test URL state round trips and component behavior for loading/error/empty states.
- [x] 4.3 Browser-test deep links, refresh, Back/Forward, filter changes, sorting and pagination/cursor behavior.
- [x] 4.4 Test rapid query changes so stale responses cannot overwrite newer results.

## 5. Measure and document

- [x] 5.1 Measure representative response size, backend search duration and Elasticsearch/database request count; document a baseline for later comparison.
- [x] 5.2 Verify production build/type-check/unit/browser tests and document the route used for pre-cutover comparison.

## Completion evidence

Completed 2026-09-17 on upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
The develop refresh, shared query services and island runtime were reused.

See [search contract, characterization, measurements and verification](../../../../docs/frontend-migration/search-workspace.md).
The workspace implements all 12 primary dimensions, six sort modes, bounded
10/25/50/100 pagination, Cards/Table, URL history and request-race protection.
The public API and canonical legacy routes remain unchanged.

Production build, type-check, 28 unit tests and 57 focused Django tests on each
backend runtime passed. All 28 Apache browser scenarios passed. All five search
scenarios passed on Caddy too; its final complete run was 27 passed / 1 legacy
login-page timeout caused by pending external script loading. That residual
integration limitation is recorded, not treated as a fully green cutover gate.
Desktop/mobile screenshots were inspected and strict OpenSpec validation passed.
