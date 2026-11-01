## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect current backend search/retrieval flow

- [x] 1.0 Preserve develop domain owner/editor membership and public versus managing-user serialization when characterizing shared retrieval contracts.

- [x] 1.1 Trace public tool-detail and search requests from URL/view through serializers, Elasticsearch/ORM helpers and permission/filter logic.
- [x] 1.2 Identify representative API requests/responses and error cases to freeze in regression tests before extraction.

## 2. Add contract/regression coverage

- [x] 2.1 Add tests for successful tool retrieval, not-found behavior and relevant visibility/permission behavior.
- [x] 2.2 Add representative search tests covering query text, pagination, one or more filters and stable ordering semantics where guaranteed.
- [x] 2.3 Record response fields/status codes that are treated as public compatibility constraints.

## 3. Extract shared services

- [x] 3.1 Extract the minimum reusable tool-retrieval service and clear domain error states.
- [x] 3.2 Extract the minimum reusable search/query service with explicit pagination and filter inputs.
- [x] 3.3 Refactor existing DRF views to call the shared services while leaving serialization in the API layer.
- [x] 3.4 Ensure no Django server code calls the local/deployed public API over HTTP for these operations.

## 4. Verify behavior and performance

- [x] 4.1 Run existing and new API tests and compare representative responses before/after the refactor.
- [x] 4.2 Check database query counts and/or Elasticsearch request counts for representative detail/search cases and prevent obvious duplication/N+1 behavior.
- [x] 4.3 Document the shared service entry points for later Django page and search-workspace changes.

## Completion evidence

Completed 2026-09-13 in `develop-migration/`, based on upstream develop
`9faec5b3b660498fdef9736e65e331728b55f99c`; the original worktree is unchanged.

- `elixir.queries.get_tool` returns the visible ORM resource or `ToolNotFound`.
- `elixir.queries.search_tools` reuses the current query builder, executes domain/tool
  queries and returns source documents, counts, pagination and cost metadata.
- DRF views retain serialization, logging, object permissions, response envelopes and errors.
  Domain owner/editor selection and public/managing representations are unchanged.
- Before extraction: 11 API contracts and one live Elasticsearch test passed.
  After extraction: 16 query tests plus 24 foundation tests pass on both Python
  3.13 and 3.10.12, with Django 5.2.11.
- Existing authorization/permission/CRUD/parameter suite: 57 passed in a separate
  disposable Elasticsearch service, removed afterward without changing preview indexes.
- Browser suite: 16 passed through Apache and 16 through Caddy, no skips or retries.
- One ORM tool lookup; one Elasticsearch request for ordinary search, two with a
  domain filter; shared search performs no database hydration or logging.
- Strict OpenSpec validation and whitespace checks passed. No dependencies, schema
  migrations, frontend changes or internal API HTTP clients were added.

See [shared service contracts and runbook](../../../../docs/frontend-migration/shared-query-services.md)
for exact commands, error mapping, baseline quirks and deferred hardening.
