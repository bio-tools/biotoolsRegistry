## 1. Contracts

- [x] 1.1 Review B04-B06/B08 and characterize delete/disown, raw JSON/Validate, domain aliases and supported workflow interactions.
- [x] 1.2 Document server-side permission/protected-domain rules, current-record races, index consistency and any unproven historical behavior.

## 2. Implementation

- [x] 2.1 Implement confirmed session/CSRF-protected delete/disown commands and connect profile/detail actions, reusing existing requests and permissions.
- [x] 2.2 Add raw JSON draft editing and validation-only behavior through the completed schema-driven editor contract, including descriptor-version checks, without losing invalid/unsaved drafts or hidden metadata.
- [x] 2.3 Implement native domain create/edit/delete, resource membership and editor management with compatible route aliases.
- [x] 2.3a Reuse the reviewed user-picker behavior: keyboard selection, duplicate exclusion, cancellation/stale-response protection and explicit empty/error states; verify current domain permissions again when saving.
- [x] 2.4 Migrate workflow list/filter/annotated media interaction with keyboard/touch support; preserve staff/API boundaries.
- [x] 2.5 Replace editor legacy fallback links with an honest accessible unavailable-runtime state, record/export links and retry where applicable; update both proxies and callers.

## 3. Verification

- [x] 3.1 Add backend/current-record/index tests for authorization, CSRF, confirmation, duplicate requests, stale ownership, hidden records, validation-only writes and failure consistency.
- [x] 3.2 Run modern contract/type/build tests plus browser mutation, native-form, failed-asset and workflow-image checks on desktop/mobile through both proxies.
- [x] 3.3 Update route ownership and audit dispositions; record parity/rollback evidence and any explicitly approved behavior retirement.

Local acceptance: 2026-10-28. See [contracts, evidence and recovery limits](../../../../docs/frontend-migration/record-domain-management.md).
Production activation, concurrency hardening and legacy deletion remain separate gates.
