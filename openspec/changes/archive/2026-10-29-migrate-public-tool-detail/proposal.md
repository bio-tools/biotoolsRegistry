## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

The public tool detail page is primarily read-only and provides a low-risk route for proving the new Django presentation layer against real bio.tools data before migrating state-heavy search and editing.

## What Changes

- Implement a Django-rendered tool detail page using shared backend retrieval logic.
- Render important resource metadata, EDAM annotations, functions, publications, links, credits and relationships when present.
- Handle sparse records, non-public records and unknown identifiers explicitly.
- Add automated parity tests against representative legacy behavior.
- Keep the legacy production route owner unchanged until the later cutover change.

## Capabilities

### New Capabilities

- `public-tool-detail-page`: A directly addressable Django-rendered page presents a bio.tools resource without requiring client-side application rendering.

### Modified Capabilities

None.

## Impact

Adds templates/views/tests and possibly a migration-prefixed route. No public API behavior changes.
