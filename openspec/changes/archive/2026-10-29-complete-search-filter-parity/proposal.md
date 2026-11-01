## Baseline

Target: upstream develop pinned at `9faec5b3b660498fdef9736e65e331728b55f99c`, implemented only in `develop-migration/`. Review the current migration work on top of that baseline, not the older outer runtime.
See the [dependency audit](../../../../docs/frontend-migration/legacy-removal-audit.md) and [finishing sequence](../../../README.md#finishing-sequence).

## Why

Canonical search redirects unsupported legacy query keys to AngularJS, and the modern parser rejects repeated values. Search cannot become the sole implementation until supported URLs and unenhanced search have native behavior.

## What Changes

- Create a parameter-by-parameter compatibility matrix from the develop router, query services and backend search implementation.
- Support remaining functional filters, including domains, EDAM IDs and supported nested metadata identifiers, without silently dropping constraints.
- Preserve query URLs, ordering, pagination, history and existing candidate/full-set advanced filter semantics.
- Provide server-rendered GET search/results when JavaScript or modern assets are unavailable, eliminating the legacy fallback.

## Dependencies

Depends on completed shared-query, search-workspace, advanced-filter, EDAM and route-cutover changes. Complete before public domain links and domain management receive final end-to-end acceptance.

Also requires `add-schema-driven-resource-ui`: consume shared field labels/choices
and server-advertised filter capabilities rather than introducing a new copied
schema field list. Schema membership alone does not establish search support.

## Capabilities

### New Capabilities

- `complete-native-search`: Supported search URLs and native GET results work without an AngularJS fallback.

### Modified Capabilities

None. Existing completed migration contracts remain in force; this change closes the remaining scope rather than reopening their historical acceptance.

## Impact

Shared search/query contract, Django parsing/GET/data views, Vue search state/controls, search templates, URL compatibility fixtures and both-proxy browser tests. Audit B02 and the search portion of B08.
