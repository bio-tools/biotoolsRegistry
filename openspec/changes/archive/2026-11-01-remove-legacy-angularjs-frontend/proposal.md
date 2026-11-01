## Baseline

Target: upstream develop pinned in the [migration baseline](../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

Audit status (2026-10-14): **blocked**. The [dependency audit](../../../docs/frontend-migration/legacy-removal-audit.md) identifies B01-B12; only audit tasks are complete, not permission to delete.

Once every production route is owned by the migrated Django/htmx/Vue implementation, retaining the AngularJS/Bower/Gulp frontend adds security, build, deployment and maintenance cost. Removal must occur only after an explicit dependency audit proves nothing still relies on it.

## What Changes

- Audit all runtime, proxy, Docker, CI, documentation and backend mounts/references to the legacy frontend.
- Abort cleanup and document blockers if any active route/build still depends on legacy assets.
- Otherwise remove AngularJS source/runtime dependencies, Bower/Gulp build configuration, obsolete frontend container/volumes/mounts and stale CI/docs.
- Preserve the modern Vite/Django static asset pipeline and public API behavior.

## Dependencies

Require `add-schema-driven-resource-ui`, `migrate-account-pages`, `complete-search-filter-parity`,
`migrate-public-information-pages`, `migrate-record-and-domain-management`,
`polish-and-validate-migrated-experience` and a refreshed dependency audit before
cleanup. On 2026-11-01 the user authorized removal before the remaining tasks in
`verify-production-migration-readiness`, which remain required before release.
See the [finishing sequence](../../README.md#finishing-sequence).

## Capabilities

### New Capabilities

- `legacy-frontend-retirement`: The legacy AngularJS/Bower/Gulp runtime and deployment stack can be removed safely once dependency and route-ownership gates prove it is unused.

### Modified Capabilities

None.

## Impact

Potentially large deletion across frontend source, Docker Compose, reverse proxy, CI and documentation. Must be gated by route ownership and full acceptance tests.
