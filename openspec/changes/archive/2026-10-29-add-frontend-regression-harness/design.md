## Context

Later changes will replace the implementation behind individual routes. Browser tests must therefore target semantics rather than AngularJS internals and must be runnable against both legacy and migrated deployments.

## Goals / Non-Goals

**Goals:**
- Establish a small, reliable behavioral baseline.
- Make tests runnable against a configurable local or deployed base URL.
- Prefer deterministic fixtures and accessible selectors.

**Non-Goals:**
- Exhaustive editor-field coverage.
- Visual pixel-equivalence testing.
- Rewriting application code.

## Decisions

### Use behavioral selectors

Prefer roles, labels, links and visible names. Introduce `data-testid` only for elements without a stable accessible selector.

### Avoid arbitrary sleeps

Wait on URL changes, network completion, visible states or explicit application signals. Trace intermittent failures rather than masking them with long timeouts.

### Keep environment assumptions explicit

Document any fixture accounts, seeded resources, Elasticsearch indexing requirements and Docker services. Tests must fail with a useful message when prerequisites are absent.

## Risks / Trade-offs

- **Risk: legacy timing makes tests flaky** -> Use deterministic waits and retry only at CI policy level.
- **Risk: tests encode obsolete markup** -> Target behavior and accessible semantics.
- **Risk: mutable public data changes assertions** -> Prefer local fixtures or stable seeded records.

## Migration Plan

The test harness can be added without route changes. CI integration should initially be non-destructive and scoped to existing development/test environments.
