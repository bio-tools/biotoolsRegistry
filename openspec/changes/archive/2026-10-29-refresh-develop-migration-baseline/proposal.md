## Why

The migration inventory and four implemented foundation changes were based on an
older fork. Upstream develop has different runtime, authentication, deployment,
tests and user-facing behavior. Continuing without a new baseline could preserve
obsolete behavior or discard upstream functionality.

## What Changes

- Target upstream develop at `9faec5b3b660498fdef9736e65e331728b55f99c`.
- Preserve the existing dirty worktree and prepare an isolated upstream-based integration checkout.
- Port the completed harness/shell/htmx work without replacing upstream runtime configuration wholesale.
- Refresh the behavior inventory and affected acceptance criteria from develop.
- Revalidate foundations through the actual Caddy/development and Apache/production paths.
- Gate all remaining migration changes on recorded develop evidence; keep old results historical.

## Capabilities

### New Capabilities

- `develop-migration-baseline`: Migration work is based on a pinned upstream develop revision with explicit compatibility evidence.

### Modified Capabilities

None. Existing behavior contracts are revalidated before further implementation.

## Impact

This is the immediate prerequisite to the remaining frontend migration changes.
Implementation touches the integration checkout, inventory, foundation compatibility
and tests only as needed. No canonical route cutover, framework redesign, production
data migration or legacy retirement is authorized by this change.
