## Context

The target architecture requires multiple presentation layers to share search/retrieval behavior. Serialization is an API concern; querying, permissions and domain errors should be reusable from ordinary Django views or frontend-oriented endpoints.

## Goals / Non-Goals

**Goals:**
- Create a stable internal boundary for tool lookup and search.
- Preserve API behavior with regression tests.
- Make query cost observable and suitable for HTML/search-workspace callers.

**Non-Goals:**
- Redesigning the public API.
- Replacing Elasticsearch.
- Generalizing every backend module at once.

## Decisions

### Extract only behavior needed by imminent migrated routes

Start with tool-by-identifier and the search operations required by detail/search pages. Do not create a speculative service framework.

### Keep representation layers separate

Shared services return domain/query results or clearly defined internal DTOs. DRF serializers continue to own public API representation. Frontend-oriented response shaping belongs to its own endpoint layer later.

### Preserve error semantics deliberately

Use domain-specific exceptions/result states so callers can map not-found, invalid query and permission states to their own HTTP representations without parsing API JSON.

## Risks / Trade-offs

- **Risk: refactor subtly changes search ordering/filtering** -> Golden/contract tests around representative queries.
- **Risk: service abstraction merely wraps view code** -> Move actual query composition and retrieval logic, not only function names.
- **Risk: expensive queries proliferate** -> Expose timing/count instrumentation points and keep pagination explicit.

## Migration Plan

Refactor API callers first and verify contract tests before using the services from new presentation layers. Rollback is a code-level revert with no data migration.
