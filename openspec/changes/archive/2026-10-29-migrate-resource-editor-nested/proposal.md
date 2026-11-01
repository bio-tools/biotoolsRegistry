## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

bio.tools resources can describe multiple functions with repeatable operations, inputs and outputs. This is the most structurally complex part of the editor and must preserve ordering, EDAM identity, nested validation and unrelated metadata without relying on htmx DOM replacement inside the Vue editor.

## What Changes

- Add repeatable function editing with operations, inputs and outputs.
- Reuse the EDAM selector for operations, data and format concepts.
- Support add/remove and any ordering behavior required by the authoritative model/current editor.
- Use stable client-only IDs for rendering while stripping them from persisted payloads.
- Map nested backend errors to the correct repeated item after edits.

## Capabilities

### New Capabilities

- `resource-editor-nested-science`: Authorized users can edit nested function, operation, input and output structures through the migrated Vue editor with authoritative validation and data preservation.

### Modified Capabilities

None.

## Impact

Substantially extends editor Vue components and tests. No public schema change is intended.
