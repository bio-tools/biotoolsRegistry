## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
The original completion record applies to the old tree; revalidate this foundation as part of `refresh-develop-migration-baseline`.

## Why

Many registry interactions are simpler as server-rendered forms/fragments than as client-side applications. A common htmx convention allows partial updates without introducing a second SPA, while preserving ordinary browser requests as the fallback.

## What Changes

- Add a reproducible modern asset entry point for migrated pages and include stable htmx 2.x.
- Define full-page versus fragment response conventions.
- Add request-history, loading, error and CSRF conventions for htmx interactions.
- Demonstrate one interaction that works as a normal request and is enhanced by htmx.
- Keep htmx out of Vue-owned DOM subtrees.

## Capabilities

### New Capabilities

- `progressive-html-interactions`: Django-rendered interactions can update targeted HTML fragments with htmx while retaining direct-request fallback behavior.

### Modified Capabilities

None.

## Impact

Adds modern frontend asset dependencies/build output and shared Django/htmx conventions. Legacy AngularJS build/runtime remains operational.
