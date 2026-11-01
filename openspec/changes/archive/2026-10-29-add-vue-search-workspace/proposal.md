## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

The search results page is expected to grow beyond conventional facets into post-search filtering, selection, comparison, visual summaries and future analytical features. Splitting those interdependent states between htmx and Vue would create brittle synchronization. The search experience therefore needs one Vue-owned workspace while Django remains the route/server authority.

## What Changes

- Add a Django-owned search page whose search application subtree is owned entirely by Vue.
- Add a frontend-oriented search response contract backed by shared Python search services; keep the existing public REST API compatible.
- Implement text query, primary filters/facets, sorting and bounded pagination/cursor behavior.
- Synchronize result-defining state with a canonical URL so deep links, refresh and Back/Forward are reproducible.
- Add loading, empty, error, stale-request and request-cancellation/debouncing behavior.
- Keep htmx from replacing/mutating nodes inside the search root.

## Capabilities

### New Capabilities

- `search-workspace`: Users can discover and navigate bio.tools resources through a URL-reproducible Vue search workspace backed by server-authoritative search services.

### Modified Capabilities

None.

## Impact

Adds a substantial Vue application, a frontend-oriented backend endpoint/DTO, search tests and migration routing. Existing public API clients must not be forced onto the new frontend contract.
