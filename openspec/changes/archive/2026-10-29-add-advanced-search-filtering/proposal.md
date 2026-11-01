## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

The search results page is expected to support extensive future features beyond fixed facets, including post-search filtering, score thresholds, comparison and analytical views. These features need a structured filter model and a clear distinction between instantaneous filtering of a bounded candidate set and authoritative filtering of the complete server result set.

## What Changes

- Add an extensible typed filter representation for Boolean, range, categorical and ontology-based conditions.
- Add post-search filtering over a bounded client candidate set for responsive exploration.
- Clearly label when a local operation applies only to the candidate set rather than all matches.
- Add a server path for applying equivalent supported filters to the complete result set for authoritative counts, pagination and export.
- Add support for backend-declared derived-score fields so future quality/relevance/posterior scores can be thresholded and versioned without a frontend redesign.
- Add extension hooks for result selection, comparison and visual-analysis panels that share the same search state rather than separate DOM/state systems.

## Capabilities

### New Capabilities

- `advanced-search-filtering`: The search workspace can apply extensible post-search filters and analysis operations while preserving the boundary between bounded client exploration and complete server-authoritative results.

### Modified Capabilities

None.

## Impact

Extends the Vue search state model and frontend-oriented search contract. May add backend filter validation and score metadata, but does not define or require a particular statistical scoring model.
