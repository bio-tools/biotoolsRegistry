## Baseline

Implement on `develop-migration/` after `add-workflow-designer`, using the existing browser-session and authorization infrastructure. The legacy image gallery and `/api/w` are separate and remain unchanged.

## Why

A workflow design should be useful beyond a single browser session and shareable deliberately without exposing private drafts.

## What Changes

- Save, list, reopen, rename and delete a user's private structured workflow designs; protect writes against stale revisions.
- Provide versioned portable import/export of non-executable designs and explicit, revocable sharing with clear visibility.
- Detect changed or missing tools, functions, annotations, schema and vocabulary when reopening or importing; preserve user work and support deliberate repair.
- Preserve unsaved state through authentication expiry, failed saves, invalid imports and sharing errors.

## Dependencies

Requires `add-workflow-designer`, `add-workflow-tool-matching` and migrated account/session infrastructure. Use the designer's graph/identity and validation contract; do not overload image-based Workflow records.

## Capabilities

### New Capabilities

- `workflow-drafts-sharing`: Private, recoverable, shareable structured workflow designs with versioned portable descriptions.

### Modified Capabilities

None.

## Impact

New persistence, browser/API routes, migrations and authorization tests. Existing resources and workflow images are unchanged. Portable descriptions are non-executable and do not include commands or actual datasets by default. No executable export or workflow execution.
