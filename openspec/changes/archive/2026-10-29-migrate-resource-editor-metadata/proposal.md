## Baseline

Target: pinned develop `9faec5b3b660498fdef9736e65e331728b55f99c` in
`develop-migration/`. Reuse completed basic/nested editing, EDAM selection,
browser authentication and the editor data contract.

## Why

The two editor slices leave 19 top-level schema fields without controls.
Preserving their existing values does not provide legacy editor parity. See the
[schema coverage audit](../../../../docs/frontend-migration/resource-editor-schema-coverage.md).
This missing migration step must precede authenticated editor route cutover.

## What Changes

- Add version/other identifiers, topic, operating system, language, license,
  collection, maturity, cost, accessibility and ELIXIR classification controls.
- Add links, downloads, documentation, related tools, publications and credits,
  including their authoritative nested fields and cardinalities.
- Reuse domain components, stable item IDs, backend error mapping and existing
  serializers/options; keep the public schema unchanged.
- Extend the write facade only for implemented fields, preserving session/CSRF,
  permission, stale-version and unrelated-data checks.
- Resolve preservation blockers through tested persistence changes where needed;
  never bypass them to make a field appear editable.
- Keep canonical routes legacy-owned until schema and registry workflow parity
  are independently verified. Metadata controls are implemented in the develop
  preview; known unsafe replacement cases remain blocked.

## Capabilities

### New Capabilities

- `resource-editor-metadata`: Schema-shaped editing of the remaining resource metadata.

### Modified Capabilities

None.

## Impact

Vue editor components, the session write facade, focused persistence fixes where
required, authoritative fixtures, regression tests and cutover prerequisites.
No public schema redesign, generic form generator or legacy removal.
