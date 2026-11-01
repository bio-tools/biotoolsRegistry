## Context

The migration has deliberately kept legacy and new implementations in parallel. Cutover should be route-by-route, not a single switch. The exact routing layer may involve Django, reverse proxy and SPA fallback rules; inspect the deployed configuration before editing.

## Goals / Non-Goals

**Goals:**
- Explicit route ownership and reversible cutover.
- Preserve API and unrelated legacy routing.
- Detect production routing regressions quickly.

**Non-Goals:**
- Removing legacy source/build dependencies.
- Rewriting migrated pages.
- Combining multiple unverified routes into one cutover.

## Decisions

### Maintain a route ownership matrix

For each canonical route/pattern record current owner, target owner, readiness evidence, cutover status and rollback instruction.

### Cut over one coherent route family at a time

A detail-route pattern can be one family; search can be another; editor routes another. Keep changes reviewable and rollback small.

### Keep legacy code until cleanup change

Routing can move away from AngularJS while source remains available for immediate rollback. Legacy removal is a separate final change.

## Risks / Trade-offs

- **Risk: proxy fallback captures migrated deep links** -> Route-resolution and direct-refresh tests at deployment configuration level.
- **Risk: redirects create loops** -> Test canonical and legacy URL variants through the full proxy stack.
- **Risk: rollback instructions stale** -> Include exact configuration keys/files and verify in staging.

## Migration Plan

For each route family: verify acceptance suite -> stage cutover -> smoke test direct/deep links -> monitor errors -> keep documented rollback until stable. Reverse only that route family on regression.
