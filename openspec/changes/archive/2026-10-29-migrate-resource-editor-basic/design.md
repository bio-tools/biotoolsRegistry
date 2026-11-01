## Context

The editor data-integrity contract and browser authentication should be reused when present. Vue owns the entire editor root; htmx does not update descendants. Django owns route, permissions and initial data/configuration.

## Goals / Non-Goals

**Goals:**
- Prove end-to-end load/edit/validate/save for a small safe field set.
- Preserve out-of-scope fields.
- Present authoritative backend validation precisely.

**Non-Goals:**
- No functions/operations/input/output editing.
- No generic schema-driven form generator.
- No route cutover of the legacy editor.

## Decisions

### Submit through authoritative existing semantics

Reuse current create/update endpoints or a thin frontend-specific facade that calls the same domain validation/persistence. Do not create a second validation regime.

### Client validation is usability-only

Use client checks for immediacy, but save success depends on backend validation. A backend rejection preserves entered editor state and maps errors to controls/global summary.

### Preserve out-of-scope data

Use the data contract so editing basic fields cannot drop nested metadata not yet editable in the new UI.

## Risks / Trade-offs

- **Risk: partial editor silently deletes data** -> Data-integrity round-trip tests are release-blocking.
- **Risk: server field errors lost during Vue state changes** -> Map errors to the submitted snapshot and stable editor paths.
- **Risk: duplicate editor implementations diverge** -> Keep this slice narrow and compare payload behavior with legacy/current API contracts.

## Migration Plan

Expose under migration routing or explicit preview access. Do not replace canonical editor routing until all required sections are migrated and parity tests pass.
