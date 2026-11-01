## Context

The basic editor, EDAM selector and data-integrity mapping should be reused if present. The entire editor remains one Vue-owned subtree. Repeated-item identity is local editor state; public payload identity/order follows the authoritative schema/API.

## Goals / Non-Goals

**Goals:**
- Safe nested function/input/output editing.
- Reusable components for repeatable sections.
- Precise nested error presentation.
- Accessible add/remove/reorder interaction.

**Non-Goals:**
- No arbitrary schema-generated UI.
- No drag-and-drop dependency unless existing ordering semantics require it and an accessible alternative is provided.
- No public schema redesign.

## Decisions

### Model nested sections as typed editor components

Use components keyed by stable client IDs and map their values through the established editor data contract. Do not key repeated items solely by array index in Vue.

### Reuse the EDAM selector

Operations, data types and formats use the same validated EDAM selection infrastructure with explicit concept scope.

### Reordering must be deterministic and accessible

If order is semantically relevant, support accessible move controls or equivalent keyboard operation. Drag-and-drop may be supplemental, not the only mechanism.

### Destructive removal is contextual

Removing a non-empty nested section should require clear user intent; confirmation policy can depend on the amount of nested data that would be discarded.

## Risks / Trade-offs

- **Risk: array-index keys cause state/error drift** -> Stable client IDs and snapshot-based error mapping.
- **Risk: nested save drops fields not represented in the UI** -> Round-trip fixture assertions for each slice.
- **Risk: drag-only reordering excludes keyboard users** -> Provide accessible deterministic controls.
- **Risk: huge components become unmaintainable** -> Extract function/input/output sections along domain boundaries, not generic UI abstraction prematurely.

## Migration Plan

Enable nested sections progressively behind the migrated editor route. Do not cut over the canonical editor until all required sections and parity tests are complete.
