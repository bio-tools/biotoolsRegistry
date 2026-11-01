## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect prerequisites and current editor behavior

- [x] 1.1 Verify/reuse the Vue runtime, browser authentication and resource-editor data contract; if absent, add only compatible minimum pieces or report the prerequisite blocker.
- [x] 1.2 Trace current create/edit permissions, submission endpoints and validation behavior for the in-scope basic fields.
- [x] 1.3 Define representative existing-resource fixture containing substantial out-of-scope nested metadata.

## 2. Add the editor page and state

- [x] 2.1 Add a Django-owned migration editor route with server-side authentication/permission checks and safe initial resource/configuration data.
- [x] 2.2 Mount one Vue editor root and implement name, description, homepage and in-scope resource/tool type fields according to authoritative schema semantics.
- [x] 2.3 Load/save through the established editor conversion contract and current authoritative persistence path.
- [x] 2.4 Implement dirty state, save progress and a safe navigation warning when unsaved user changes would otherwise be lost.

## 3. Validation and error handling

- [x] 3.1 Add client usability validation only where it does not conflict with backend rules.
- [x] 3.2 Map backend field and global errors into the editor while preserving user-entered values.
- [x] 3.3 Handle authentication/CSRF/session-expiry failures without discarding editor state unnecessarily.

## 4. Test data integrity and permissions

- [x] 4.1 Test authorized create/edit and unauthorized access/submission.
- [x] 4.2 Test invalid basic values and precise backend error presentation.
- [x] 4.3 Test editing one basic field on a rich resource and assert all out-of-scope metadata remains unchanged.
- [x] 4.4 Browser-test load, edit, validation failure, correction, successful save and unsaved-navigation warning.
- [x] 4.5 Run backend tests, frontend type-check/unit tests, production build and focused browser tests.

## Completion evidence

Completed 2026-09-23 on develop `9faec5b3b660498fdef9736e65e331728b55f99c`
in the isolated `develop-migration/` checkout. See the
[basic editor contract, preview and limitations](../../../../docs/frontend-migration/resource-editor-basic.md).
Type-check/build and 70 frontend tests pass; 104 migration backend tests pass on
both runtimes, and all 49 browser tests pass on both Apache and Caddy. Rich-resource
round trips, permissions, validation, recovery, stale edits, navigation warnings
and preservation rollback are covered. Desktop/mobile screenshots were inspected.
Known unsafe replacement cases remain blocked; export retains their drafts.
Nested editing, legacy concurrency guarantees, cross-store atomicity and canonical
route cutover are not included. Live ORCID verification remains separately pending.
