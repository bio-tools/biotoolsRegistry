## 1. Contract

- [x] 1.1 Define graph persistence, revision/identity, ownership, sharing/revocation and portable format contracts; inventory security and privacy boundaries.
- [x] 1.2 Define schema/vocabulary/resource change handling, unresolved references, import validation and migration/rollback behavior.

## 2. Implementation

- [x] 2.1 Add private design create/list/open/rename/delete with authenticated authorization, CSRF, current revision and recoverable errors.
- [x] 2.2 Add explicit revocable read-only sharing and owner-controlled duplication, ensuring private drafts remain private.
- [x] 2.3 Add versioned non-executable import/export, safe validation and lossless unresolved-reference handling; reconnect changed tools only after user review.
- [x] 2.4 Integrate session expiry, conflict, failed save and import errors without losing the current draft; document migration and rollback.

## 3. Verification

- [x] 3.1 Test authorization, shared-link access and revocation, invalid imports, stale/concurrent edits, session expiry and unchanged drafts on failure.
- [x] 3.2 Test round trips, schema/vocabulary/resource changes, hidden/deleted tools, duplicate step instances, migration/rollback and both proxy/browser journeys.
