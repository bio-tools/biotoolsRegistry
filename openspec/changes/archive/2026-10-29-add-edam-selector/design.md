## Context

The component must work both inside the search workspace and inside the Vue-owned resource editor. It should depend only on typed props/contracts, not on a global search/editor store.

## Goals / Non-Goals

**Goals:**
- Reusable single/multiple EDAM selection.
- Accessible combobox/listbox keyboard behavior.
- Stable ID submission and server validation.
- Safe handling of rapid lookup requests.

**Non-Goals:**
- Replacing EDAM itself.
- Loading the full ontology into every browser page.
- Trusting labels supplied by the browser as authoritative identifiers.

## Decisions

### Configure concept scope explicitly

Props declare the allowed EDAM concept type/branch and multiplicity. The backend validates submitted identifiers against the permitted scope.

### Lookup is remote and bounded

Debounce textual lookup and cap result size. Cancel or ignore stale responses. Selected concepts remain available even if they fall outside the current lookup result list.

### Submit identifiers through an explicit contract

Ordinary Django forms may use hidden fields/structured serialized values; Vue editor/search consumers may use typed object state. In both cases the server validates identifiers and resolves authoritative labels.

## Risks / Trade-offs

- **Risk: autocomplete request flood** -> Debounce plus stale request cancellation.
- **Risk: inaccessible custom combobox** -> Follow ARIA combobox/listbox semantics and keyboard tests.
- **Risk: label/ID mismatch** -> Server trusts validated IDs, not browser labels.

## Migration Plan

Adopt first in one migrated interface, then reuse the same component in search/editor sections as they migrate.
