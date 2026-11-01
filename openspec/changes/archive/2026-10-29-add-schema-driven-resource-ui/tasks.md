## 1. Authority and Compatibility

- [x] 1.1 Audit schema/serializer/validator/UI metadata sources and duplicated field/enum lists across editor, detail, search and EDAM on the pinned implementation.
- [x] 1.2 Record the selected schema artifact/version/digest and vocabulary revisions; reconcile bundled-XSD versus JSON/backend discrepancies and classify registry-only policy/fields.
- [x] 1.3 Specify supported constructs, stable IDs, runtime descriptor/version protocol, public/read/write/search capabilities and the compatibility/update/rollback policy.

## 2. Backend Contract

- [x] 2.1 Implement structured schema ingestion and repeatable generation/check commands using existing tooling; fail on unsupported or inconsistent schema/backend mappings.
- [x] 2.2 Derive schema-owned options and presentation metadata from the selected source, reuse them in authoritative validators, and replace manually maintained duplicates with generated data or explicit tested registry extensions.
- [x] 2.3 Deliver the effective descriptor and vocabulary revisions through existing backend configuration/lookup paths; handle unavailable metadata, cache invalidation and per-user permissions safely.
- [x] 2.4 Add server checks for schema-version changes during editing, deprecated/removed values and unsupported persistence without weakening existing record-revision or preservation checks.

## 3. Frontend Adoption

- [x] 3.1 Extend existing generic field/repeatable components and draft mapping to consume runtime metadata, including new supported nested fields without frontend source edits or rebuilds.
- [x] 3.2 Replace hard-coded schema field/label/option/section allowlists; retain bounded function/EDAM/publication overrides with generic fallback for unhandled fields.
- [x] 3.3 Adopt metadata for public detail and applicable search controls; expose only server-authorized public/search capabilities and preserve current URL/filter semantics.
- [x] 3.4 Handle descriptor reload/conflict, missing metadata and deprecated values without losing drafts, rewriting stable IDs or silently dropping record data.

## 4. Verification and Handover

- [x] 4.1 Add fixture-update tests proving label/help, enum addition/removal, optional nested field and EDAM term changes propagate with the same frontend build; cover generic fallback inside a specialized function section.
- [x] 4.2 Test incompatible field/value renames, required/type/cardinality changes, unsupported constructs, stale caches/drafts and missing persistence; verify activation blocking or explicit safe migration.
- [x] 4.3 Run backend/API/round-trip tests, modern type/unit/build and desktop/mobile browser checks through both proxies, including permissions, function diagrams and native/read-only fallback.
- [x] 4.4 Add CI drift checks and schema-driven-ui.md with generation/refresh/activation commands, source provenance, discrepancy resolutions and compatible rollback evidence.
- [x] 4.5 Update schema coverage, dependency audit and finishing evidence; keep unverified schema/vocabulary transitions explicitly incomplete.

## Evidence: 2026-10-21

See `docs/frontend-migration/schema-driven-ui.md` for the source manifest,
activation/rollback runbook and verification counts. The isolated same-build
rehearsal passed through both live proxies at desktop/mobile widths, including
new nested-field persistence, EDAM label updates, removed values, stale drafts
and compatible rollback. Backend/Vue fixtures additionally cover compatibility
blocking and unknown nested additions within function diagrams. CI drift checking
and the runbook are complete. Regressions passed: 186 backend tests in each
runtime, 96 modern unit tests, type-check/build and 30 browser tests per proxy.
Local acceptance is complete; production deployment, live provider/email and
legacy deletion remain separate gates.
