## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

Migrated pages should not replace legacy production routes until their behavioral tests and parity review are complete. Route ownership must change deliberately and reversibly so failures can be isolated to one feature rather than forcing a full frontend switch.

## What Changes

- Create/update a route ownership table for each user-facing path.
- Cut over only routes whose migrated implementation and acceptance tests are complete.
- Preserve unrelated legacy routes and all public API routes.
- Add redirects for obsolete URL variants where required.
- Document rollback per cut-over route and add enough logging/monitoring to identify 4xx/5xx regressions.
- Do not delete legacy implementation code in this change.

## Capabilities

### New Capabilities

- `migrated-route-cutover`: Verified route families can be moved incrementally to migrated owners with preserved API routing, direct-navigation semantics, observability and rollback.

### Modified Capabilities

None.

## Impact

Reverse proxy, Django URLs, legacy frontend fallback routing and deployment documentation may change. Runtime behavior should remain semantically equivalent for each cut-over route.
