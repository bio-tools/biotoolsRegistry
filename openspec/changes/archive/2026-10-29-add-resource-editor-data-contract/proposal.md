## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

The bio.tools resource model contains nested repeatable structures and meaningful optional values. Rewriting the editor without an explicit data contract risks silently dropping untouched fields, conflating missing/null/empty values, or losing nested validation context.

## What Changes

- Define a typed editor-state model and explicit mapping to/from authoritative resource representations.
- Define stable client-only identifiers for repeated editor items without leaking them into public payloads.
- Define nested backend error paths that can target the correct repeated item/field.
- Add round-trip fixture tests for minimal and structurally rich resources.
- Establish one documented source-of-truth strategy for Python/TypeScript types.

## Capabilities

### New Capabilities

- `resource-editor-data-integrity`: Migrated editing can load, modify and resubmit resource data without unintended loss of untouched information or ambiguous nested error mapping.

### Modified Capabilities

None.

## Impact

Introduces mapping/types/fixtures used by later Vue editor changes. Public schema and API semantics remain unchanged.
