## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
The original completion record applies to the old tree; revalidate this foundation as part of `refresh-develop-migration-baseline`.

## Why

The legacy frontend contains route, search, authentication, validation and editor behavior that can be lost during a framework rewrite if it is inferred only from visible screens. The migration also needs an explicit ownership model so Django, htmx and Vue do not evolve into overlapping frontend architectures.

## What Changes

- Inventory all user-facing legacy routes, their controllers/templates/services and API usage.
- Inventory authentication, URL/query-state, search/filter, editor validation and client-side payload transformation behavior.
- Classify each interaction as a candidate for plain Django rendering, htmx enhancement or Vue ownership.
- Add an architecture decision record defining route ownership, DOM ownership, public API compatibility and migration/cutover rules.
- Add a risk register for behavior that is untested, ambiguous or likely to cause data loss.
- Do not change runtime application behavior.

## Capabilities

### New Capabilities

- `migration-inventory`: Maintainers have an evidence-based inventory of legacy frontend behavior and explicit Django/htmx/Vue ownership rules for migration.

### Modified Capabilities

None.

## Impact

Documentation only. The output becomes the evidence base for later OpenSpec changes and regression tests.
