## Baseline

Implement on the preserved `develop-migration/` checkout after the current frontend experience acceptance. Reuse the accepted schema-driven resource contract, EDAM lookup and shared search services. The existing annotated-image workflow gallery remains a separate capability.

## Why

People need to discover tool functions that can receive their data and produce useful outputs. Existing search filters identify resources but do not establish that the chosen data type, format and operation belong to the same function and input/output annotation.

## What Changes

- Provide a paginated, explainable service for matching annotated functions by input or output EDAM data type and format, with an optional EDAM operation filter.
- Support exact and explicitly identified ontology-related matches, distinguish missing metadata and conflicts, and preserve function and input/output relationships when verifying candidates.
- Reuse the active schema and EDAM vocabulary, with bounded queries, vocabulary revision and recoverable errors; do not hard-code a catalogue of schema terms or values.
- Characterize index behavior, annotation coverage, provenance and stable references required by the designer.

## Dependencies

Depends on completed `add-schema-driven-resource-ui`, `add-edam-selector`, `extract-shared-query-services` and `complete-search-filter-parity`. It supplies the contract for `add-workflow-designer`; review the existing `polish-and-validate-migrated-experience` before implementation.

## Capabilities

### New Capabilities

- `workflow-tool-matching`: Explainable, function-specific data/format matching and EDAM operation filtering.

### Modified Capabilities

None.

## Impact

Shared query services, an isolated matching endpoint, ontology access and tests. Existing search and public API behavior remain compatible. No workflow execution or executable export is included.
