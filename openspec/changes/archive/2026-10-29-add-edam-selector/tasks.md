## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect existing EDAM behavior

- [x] 1.0 Preserve develop EDAM modal cancel-versus-commit behavior, suggestion hints and distinct data versus operation/format payload shapes.

- [x] 1.1 Trace current EDAM lookup/search endpoints, ontology scope rules, selector UX and submitted payload formats.
- [x] 1.2 Reuse existing backend lookup logic where suitable and document any differences among topic, operation, data and format concepts.

## 2. Define and implement backend lookup contract

- [x] 2.1 Add or adapt a bounded frontend-oriented EDAM lookup endpoint/service with explicit concept scope and validated query inputs.
- [x] 2.2 Return stable identifiers and display labels plus only the metadata required by the selector.
- [x] 2.3 Validate submitted EDAM identifiers server-side for the declared concept scope.

## 3. Implement the Vue component

- [x] 3.1 Implement typed props for concept scope, multiplicity, initial values, disabled/read-only state and endpoint/configuration.
- [x] 3.2 Implement debounced search, loading/empty/error states, stale-request cancellation/ignoring and selected-term removal.
- [x] 3.3 Implement keyboard navigation, focus management and ARIA combobox/listbox semantics.
- [x] 3.4 Define reusable integration for ordinary Django form submission and Vue-owned state consumers.

## 4. Test and document

- [x] 4.1 Unit-test single/multiple selection, stale responses, removal, disabled/read-only behavior and serialization.
- [x] 4.2 Backend-test concept-scope validation and malformed/unknown identifiers.
- [x] 4.3 Browser-test keyboard-only search/select/remove and preservation after a server-side validation rerender where applicable.
- [x] 4.4 Document component props/events/value format for later search/editor changes.

## Completion evidence

Completed 2026-09-18 in the accepted develop checkout at
`9faec5b3b660498fdef9736e65e331728b55f99c`.

See [EDAM contract, develop review, preview and verification](../../../../docs/frontend-migration/edam-selector.md).
The selector is adopted by advanced topic filtering and a native Django
annotation-validation form. It uses the existing ontology records and validator,
with bounded remote choices, scoped ID validation, retained selected terms,
suggestion hints, cancel/apply drafts and keyboard-accessible single/multiple
selection. Public serializer rules and legacy editor routes remain unchanged.

Build and type-check pass, as do all 47 frontend tests, all 70 focused backend
tests on each runtime, and all 36 browser tests on both Apache and Caddy.
Desktop/mobile screenshots and the no-JavaScript form path were verified.
The preview does not save registry records; editor persistence is a later change.
