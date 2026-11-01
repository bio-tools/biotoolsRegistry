## 1. Confirm authoritative behavior

- [x] 1.1 Review the schema coverage audit, generated contract and legacy editor for all 19 missing fields and their nested members.
- [x] 1.2 Record serializer/XSD differences, enumerations, identifier alternatives, ordering and publication enrichment behavior.
- [x] 1.3 Define tested preservation handling for enriched publications, protected identifiers and server-owned metadata; retain blockers until safe.

## 2. Complete metadata controls

- [x] 2.1 Add versions, other identifiers and topic selection.
- [x] 2.2 Add operating systems, languages, license, collection, maturity, cost and accessibility.
- [x] 2.3 Add ELIXIR platforms, communities and nodes.
- [x] 2.4 Add links, documentation and downloads with their distinct type cardinalities, notes and version fields.
- [x] 2.5 Add related tools and relationship types.
- [x] 2.6 Add publication identifiers, types, versions and notes with safe enrichment handling.
- [x] 2.7 Add credit identity/contact fields, persistent IDs, entity type, roles and notes.

## 3. Protect mutation and validation

- [x] 3.1 Extend the facade allowlist only for implemented fields; preserve authorization, CSRF, revisions and server-owned metadata.
- [x] 3.2 Reject unknown nested keys; strip client IDs; maintain validation identity through repeated-item edits/removal/reorder.
- [x] 3.3 Keep full-draft export, discard, session recovery and navigation protection working across all sections.

## 4. Verify parity

- [x] 4.1 Round-trip rich authoritative records, including publications and credits, through every editable section without unintended loss.
- [x] 4.2 Test valid/invalid shapes, exact nested errors, clear/remove behavior and preservation blockers in backend and frontend suites.
- [x] 4.3 Browser-test desktop/mobile creation and editing through Apache and Caddy, inspecting layouts and keyboard workflows.
- [x] 4.4 Update schema coverage for all 26 top-level fields and document registry-only workflow gaps before editor cutover.
- [x] 4.5 Run type-check/build, regression suites and strict OpenSpec validation; record evidence before marking complete.

## Verification evidence

Implemented in the pinned develop checkout. On 2026-09-29 the 118 migration
backend tests passed on Python 3.13 and Apache/Python 3.10 with the disposable
Elasticsearch tests enabled, without skips. On 2026-09-30 type-check and all
82 frontend unit tests pass. Production build: JS 243.33 kB / 67.92 kB gzip,
CSS 13.46 kB / 3.01 kB gzip; no added dependency or database migration.
All 18 OpenSpec changes pass strict validation. Existing backend/htmx warnings
remain unchanged.

The full Apache and HTTPS/Caddy browser runs each pass 55 tests without skips or
automatic retries. Artifacts: `tests/browser/test-results-metadata-apache-final/`
and `tests/browser/test-results-metadata-caddy-final/`. Screenshots of
the function flow, metadata labels and credits were inspected on desktop/mobile;
tests also assert unique IDs and no horizontal overflow. The earlier EDAM
test counted unrelated native options; it now scopes results to the dialog.
An intermediate asset rebuild invalidated a running test deployment; the final
run used one unchanged, collected production build.

See the [schema audit](../../../../docs/frontend-migration/resource-editor-schema-coverage.md)
for all controls and remaining gates. Valid publication persistence uses mocked
enrichment in backend tests; browsers verify invalid-identifier recovery.
At completion, enriched publications and protected identifiers remained blocked.
The 2026-10-06 `cut-over-migrated-routes` prerequisite fixes persistence and removes
those gates, with forged-value and unknown-field checks retained. See the schema
audit for current evidence. Ownership/permission editing and canonical editor
cutover are not part of this metadata milestone.
