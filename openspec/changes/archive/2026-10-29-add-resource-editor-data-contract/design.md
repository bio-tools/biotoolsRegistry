## Context

The editor representation does not have to be byte-identical to public API JSON. It may need client-only IDs, explicit blank states and normalized UI structures, but conversion must preserve authoritative semantics and untouched fields.

## Goals / Non-Goals

**Goals:**
- Make data loss detectable before UI migration.
- Provide stable repeated-item identity for Vue rendering/reordering.
- Map nested backend validation to precise editor locations.

**Non-Goals:**
- Building visual editor components.
- Changing biotoolsSchema.
- Silently normalizing values for convenience.

## Decisions

### Separate authoritative resource representation from editor state

Use explicit conversion functions in both directions. Keep client-only metadata in editor state only and strip it before persistence.

### Preserve meaningful optional-value distinctions

Determine from existing serializers/schema which distinctions among missing, null, empty string and empty list are semantically relevant. Preserve those; document any cases the current backend already normalizes.

### Make untouched-field preservation testable

Updating a subset of fields must not construct a partial payload that deletes unrelated fields unless the endpoint explicitly defines patch semantics. Use merge/version/update behavior consistent with current backend contracts.

### Error paths identify repeated items robustly

Translate backend array-index/path errors into editor item IDs/paths after considering reorder/add/remove operations.

## Risks / Trade-offs

- **Risk: TypeScript types drift from Python/schema** -> Choose and document one generation/maintenance source of truth and verify in CI.
- **Risk: round-trip tests bless current bugs** -> Compare schema/API semantics and mark intentional legacy quirks explicitly.
- **Risk: reordered items shift index-based errors** -> Map server errors immediately to stable editor IDs for the submitted snapshot.

## Migration Plan

This contract ships before the editing UI relies on it. No route cutover is involved.
