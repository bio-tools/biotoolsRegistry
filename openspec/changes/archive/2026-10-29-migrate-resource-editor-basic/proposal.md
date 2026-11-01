## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

The resource editor is the highest data-integrity risk in the migration and should be introduced in narrow vertical slices. The first slice proves the Vue-owned editor subtree, permission/CSRF behavior, data contract and backend error mapping before nested scientific structures are migrated.

## What Changes

- Add a Django-owned editor page that mounts one Vue-owned editor subtree.
- Implement basic identity/description/homepage/tool-type fields already supported by the authoritative model.
- Load and submit through the resource-editor data contract and current backend mutation semantics.
- Keep backend validation authoritative and map errors to fields while preserving user input.
- Preserve all out-of-scope existing fields during edits.

## Capabilities

### New Capabilities

- `resource-editor-basic`: Authorized users can create or edit the basic resource fields through the migrated Vue editor without unintended changes to out-of-scope metadata.

### Modified Capabilities

None.

## Impact

Adds editor route/components/submission tests. The legacy editor remains available until later cutover.
