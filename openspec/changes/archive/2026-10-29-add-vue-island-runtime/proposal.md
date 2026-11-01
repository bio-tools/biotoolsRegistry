## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

Complex controls such as EDAM selection, search exploration and the nested resource editor need coherent client-side state, but the registry should not become a site-wide SPA. A typed Vue island runtime provides state-heavy components while Django retains page routing and htmx remains available for simpler regions.

## What Changes

- Add Vue 3, TypeScript, `vue-tsc`, Vitest and Vue Test Utils to the existing modern asset package.
- Add a generic explicit-root island mounting registry with safe server-to-client JSON props.
- Integrate mount/unmount behavior with htmx swaps that insert or remove complete Vue roots.
- Support multiple component instances without duplicate mounting or leaked applications.
- Do not add Vue Router; do not add Pinia without a demonstrated need.

## Capabilities

### New Capabilities

- `vue-island-runtime`: Django pages can embed isolated typed Vue applications/components whose lifecycle remains correct across ordinary navigation and htmx fragment replacement.

### Modified Capabilities

None.

## Impact

Modern frontend dependencies/build/tests grow, but legacy AngularJS remains operational. Django templates gain a safe convention for Vue roots and initial props.
