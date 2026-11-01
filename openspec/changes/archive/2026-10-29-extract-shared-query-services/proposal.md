## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

Django-rendered pages and frontend-oriented endpoints need the same search and retrieval semantics as the public REST API. Having server-side views call the application's own REST API over HTTP would add serialization/network overhead and duplicate error handling, while duplicating search logic risks behavioral drift.

## What Changes

- Extract reusable Python query/domain services for tool retrieval and representative search operations.
- Refactor existing API views to call the shared services without changing public response semantics.
- Add regression coverage for representative API responses, search semantics and errors.
- Do not introduce a localhost/internal HTTP client.

## Capabilities

### New Capabilities

- `shared-query-services`: Server-side callers can reuse authoritative Python tool retrieval and search services without calling the application's own REST API over HTTP.

### Modified Capabilities

None.

## Impact

Backend search/retrieval modules, API views/serializers and tests may change. Public API payloads, status codes and query semantics must remain compatible.
