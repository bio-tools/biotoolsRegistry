## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect authoritative resource semantics

- [x] 1.0 Refresh fixtures from develop serializers: old community/BioLib is removed, while elixirCommunity, collection IDs and domain membership remain distinct; do not resurrect removed fields to satisfy historical fixtures.

- [x] 1.1 Inspect biotoolsSchema usage, backend models/serializers/validators and current AngularJS editor transformations.
- [x] 1.2 Document semantics for missing, null, empty string, empty list, server-generated fields and fields ignored on create/update.
- [x] 1.3 Build representative minimal and structurally rich fixtures including functions, operations, inputs/outputs, publications, links, credits and relationships.

## 2. Define the editor contract

- [x] 2.1 Define a typed editor-state model with stable client-only IDs for repeated structures.
- [x] 2.2 Implement authoritative-resource-to-editor conversion.
- [x] 2.3 Implement editor-to-submission conversion that strips client-only metadata and preserves untouched data according to endpoint semantics.
- [x] 2.4 Define backend-validation-error-to-editor-path mapping for top-level and nested repeated fields.
- [x] 2.5 Document the source of truth/generation strategy for corresponding Python and TypeScript types.

## 3. Add data-integrity tests

- [x] 3.1 Test minimal and rich resource round trips without user edits.
- [x] 3.2 Test editing one scoped field while unrelated top-level and nested fields remain unchanged.
- [x] 3.3 Test add/remove/reorder of repeated editor items and confirm client-only IDs never appear in submitted public payloads.
- [x] 3.4 Test nested backend error mapping after reorder/add/remove using the exact submitted snapshot.
- [x] 3.5 Test documented missing/null/empty semantics and record any backend normalization that prevents exact round trip.

## 4. Verification

- [x] 4.1 Run backend schema/serializer tests plus frontend type-check/unit tests.
- [x] 4.2 Document non-round-trippable legacy cases explicitly instead of hiding them in conversion code.

## Completion evidence

Completed 2026-09-21 on pinned develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
See [resource editor data contract](../../../../docs/frontend-migration/resource-editor-data-contract.md)
for serializer/schema and legacy-editor review, types/generation, conversion and error
identity, explicit backend limitations, fixture coverage and verification commands.

- 56 frontend unit tests and type-check/build passed.
- 79 migration backend tests passed on Python 3.13 and Apache/Python 3.10.
- No editor UI, persistence behavior change, route cutover, or preview-record writes.
- Known unsafe legacy cases are explicit submission blockers; they are not silently normalized away.
