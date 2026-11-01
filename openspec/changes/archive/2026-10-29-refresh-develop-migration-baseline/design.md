## Context

The target is upstream `bio-tools/biotoolsRegistry` develop, not this fork's stale
local develop branch. The original working tree contains uncommitted migration
work and unrelated user files. The [baseline matrix](../../../../docs/frontend-migration/baseline.md)
records the pinned revision and observed differences.

## Decisions

### Preserve work and integrate explicitly

First record tracked, untracked and ignored migration artifacts. Create an isolated
checkout from the pinned upstream commit, and transfer only reviewed migration
changes. Do not blindly copy old settings, URLs, requirements or proxy configuration.
Keep the original worktree intact; no automatic stash, reset, checkout or unrelated
commit is necessary. Report the integration location and actual application base.

### Revalidate, do not relabel evidence

Retain old SHA/test records. Refresh the inventory from develop and record deltas
with source references. Reuse existing upstream tests and add missing migration
checks. Reopen foundation acceptance only until it actually passes on develop.
If an upstream build or test fails before migration changes, record it separately
and make only fixes necessary for this baseline, with explicit tests.

### Cover both runtime paths

Caddy forwards HTTP to runserver in development; Apache uses WSGI in production.
The old HTML entry-point marker does not automatically work through Caddy. Choose
an explicit route arrangement that preserves API and legacy ownership in both.
Test bot handling before SPA/Rendertron fallbacks, cache variation, static assets,
session/CSRF behavior, reverse URLs, errors and direct navigation. Account-backed
and external-provider tests need isolated fixtures and provider configuration;
document missing prerequisites instead of claiming complete verification.

### Keep the target architecture

Django remains route/server authority, htmx handles server fragments, and Vue owns
coherent stateful subtrees. Keep one modern Vite package. This change refreshes
compatibility assumptions, not the agreed ownership model or feature scope.

## Risks

- Lost dirty-worktree changes: use an isolated checkout and explicit artifact inventory.
- False confidence from old tests: record base SHA and runtime for every run.
- Dropped newer functionality: review ORCID/recovery, API schema, search/editor contracts and every route family.
- Deployment mismatch: validate both Caddy and Apache; a temporary WSGI dispatcher is not sufficient evidence.
- Destructive fixtures: run upstream database/index tests only in disposable services.
