## 1. Compatibility Matrix

- [x] 1.1 Review B02/B08 and map every declared query key and actual backend/UI producer, including result-mode/export workflows and repeated-value semantics.
- [x] 1.2 Add characterization fixtures for remaining functional filters, domain membership, EDAM IDs, nested metadata and invalid/historical parameters; resolve any proposed retirement explicitly.

## 2. Implementation

- [x] 2.1 Extend the shared query/parser/state contracts and active-filter controls using the completed schema-driven UI descriptor/capabilities, while preserving public API representations and advanced-filter scope.
- [x] 2.2 Implement native GET results and pagination with the same constraints and errors as the enhanced workspace.
- [x] 2.3 Update canonical URL/history/link producers; remove automatic supported-query and unavailable-asset dependence on AngularJS.

## 3. Verification

- [x] 3.1 Run backend/Elasticsearch parity tests for identifiers/counts, combined filters, domains, duplicates, encoding, invalid input, limits and failures.
- [x] 3.2 Run modern unit/type/build checks and desktop/mobile browser journeys with JavaScript enabled, disabled and failed assets through both proxies.
- [x] 3.3 Update the compatibility matrix, route ownership and audit with evidence; retain only the explicitly temporary rollback escape hatch.

Local acceptance 2026-10-22: [compatibility matrix and test evidence](../../../../docs/frontend-migration/search-filter-parity.md).
No functional query key or export workflow is retired. Legacy saved grid layouts
remain available through explicit rollback and are tracked in the polish change
for migration or explicit retirement approval before legacy deletion.

2026-10-23 presentation follow-up: replaced the flat filter list with shared,
schema-derived nested groups in enhanced and native search. All supported keys
remain available; focused unit/backend and both-proxy browser checks pass. See
the nested-filter section of the linked evidence.
