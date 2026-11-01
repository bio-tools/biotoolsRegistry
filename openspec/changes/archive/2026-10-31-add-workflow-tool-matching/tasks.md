## 1. Contract and data review

- [x] 1.1 Characterize input/output/function relationships, active schema, EDAM hierarchy and index mapping; measure representative annotation coverage and candidate-query limitations. A 34,519-record anonymized public crawl and the preview's EDAM 1.25 vocabulary are documented with their limitations in the [matching evidence](../../../docs/frontend-migration/workflow-tool-matching.md#full-public-corpus-results).
- [x] 1.2 Define match states, direction, operation filtering, incomplete metadata, revisions, pagination and privacy; document compatibility boundaries and corpus expectations.

## 2. Implementation

- [x] 2.1 Implement bounded matching and operation filtering on the active schema/vocabulary; preserve function and IO identity and verify structured candidates.
- [x] 2.2 Implement exact and directional related evidence, unknown/obsolete/conflict states, safe candidate retrieval, consistent pagination and recoverable errors. The user accepted the explicitly disclosed live-scan behavior on 2026-10-31; a test covers additions and visibility changes between pages.

## 3. Verification

- [x] 3.1 Compare results to an independent structured-data oracle for multi-function/multi-IO, missing, obsolete, incompatible, same-function operation and changed/hidden-record cases.
- [x] 3.2 Test pagination, completeness, schema/vocabulary changes, privacy, failures and representative performance; document endpoint and limitations. The real 34,519-record corpus passed the structured-data oracle and user-accepted local budgets on both runtimes; production deployment performance remains a separate gate.
