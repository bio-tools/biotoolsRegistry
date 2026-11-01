## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect nested legacy behavior and prerequisites

- [x] 1.1 Trace current function/operation/input/output editing semantics, ordering, defaults, EDAM validation and payload transformations.
- [x] 1.2 Reuse the editor data contract and EDAM selector; if either is absent, add only compatible minimum behavior or report the prerequisite blocker.
- [x] 1.3 Add rich fixtures covering multiple functions, multiple operations, inputs/outputs and multiple data/format EDAM values.

## 2. Implement repeatable function structure

- [x] 2.1 Add typed Vue components for repeatable functions keyed by stable client-only IDs.
- [x] 2.2 Add repeatable operations using the operation-scoped EDAM selector.
- [x] 2.3 Add repeatable inputs and outputs with data-type and format EDAM selectors as defined by the authoritative model.
- [x] 2.4 Implement add/remove and semantically required ordering with an accessible keyboard-operable mechanism.
- [x] 2.5 Add appropriate confirmation for destructive removal of populated nested sections.

## 3. Preserve validation and data integrity

- [x] 3.1 Submit nested structures through the established editor conversion contract and verify client-only IDs are absent from payloads.
- [x] 3.2 Map backend nested validation errors back to the correct function/input/output from the submitted snapshot.
- [x] 3.3 Verify unrelated existing resource fields remain unchanged during nested edits.

## 4. Test complex workflows

- [x] 4.1 Unit-test add/remove/reorder and EDAM selection across multiple nested sections.
- [x] 4.2 Backend/integration-test valid and invalid nested payloads plus precise error paths.
- [x] 4.3 Browser-test multiple functions, multiple inputs/outputs, removal, reorder and invalid nested field recovery.
- [x] 4.4 Round-trip a rich existing resource through load/save and compare authoritative data for unintended loss/reordering.
- [x] 4.5 Run frontend type-check/unit/build and focused backend/browser suites.

## Completion evidence

Follow-up: the editable input/operation/output diagram and compact EDAM controls
restore the legacy scientific flow. Desktop/mobile geometry and keyboard
selection are covered by the nested browser scenarios. The remaining 19 metadata
fields were included at the user's request in `migrate-resource-editor-metadata`;
see its completion evidence and the schema coverage audit.

Implemented 2026-09-23 in `develop-migration/` on pinned develop
`9faec5b3b660498fdef9736e65e331728b55f99c`. See the
[schema review, preview, tests and limits](../../../../docs/frontend-migration/resource-editor-nested.md).
The local bio.tools schema 3.3.0 and current serializers retain exactly one data
object per input/output and repeatable operation/format objects. No public schema
or canonical route cutover was introduced. Frontend type-check/build and 76 unit
tests pass; 112 migration backend tests pass on each runtime. Rich round trips
retain publications/credits and other unrelated fields. Browser evidence covers
1440px/390px layouts, scoped selections, reorder/removal and real nested error
recovery. Known unsafe replacement cases remain blocked.
The full Apache and HTTPS/Caddy browser runs each pass 53 tests without skips or
automatic retries. All 17 OpenSpec changes pass strict validation.
