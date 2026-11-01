## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect and extend the search state contract

- [x] 1.1 Identify the current Vue search state, URL serializer, backend filter inputs and candidate/result bounds.
- [x] 1.2 Define a typed discriminated filter model for Boolean, range, categorical, ontology and backend-declared numeric score filters.
- [x] 1.3 Define explicit execution scope metadata: server-authoritative versus candidate-local.
- [x] 1.4 Add server allow-list validation so arbitrary fields/operators cannot be injected through the filter representation.

## 2. Implement candidate-local exploration

- [x] 2.1 Add a bounded candidate collection abstraction separate from the current visible result segment when needed by the chosen UX.
- [x] 2.2 Implement at least one representative local range/Boolean filter with immediate Vue-side recomputation.
- [x] 2.3 Display candidate-set scope and ensure local counts are not presented as full-query counts when completeness is unknown.
- [x] 2.4 Ensure local filter changes integrate with selection/comparison/visual-analysis state through the shared search model rather than DOM events.

## 3. Implement authoritative full-set refinement

- [x] 3.1 Extend the frontend search endpoint to accept the supported server-side filter representation and apply it through shared search services.
- [x] 3.2 Add an explicit action or automatic promotion policy for applying supported candidate-local filters to the complete result set.
- [x] 3.3 Update canonical URL/saved-search serialization for server-applied advanced filters.
- [x] 3.4 Verify authoritative totals/facets/pagination are recomputed after full-set refinement.

## 4. Add derived-score extensibility

- [x] 4.1 Define backend/frontend metadata for optional numeric derived scores, including stable key, label and definition/model version when applicable.
- [x] 4.2 Implement a score-threshold filter using fixture/mock score metadata without requiring a production scoring model.
- [x] 4.3 Ensure saved/canonical state can identify the score definition/version when that identity affects reproducibility.

## 5. Test and measure

- [x] 5.1 Unit-test filter serialization, local execution, scope labeling and URL round trips.
- [x] 5.2 Backend-test allow-list validation and equivalence between supported local filter semantics and server full-set semantics on the same fixture set.
- [x] 5.3 Browser-test candidate-only filtering, promotion to full-set filtering, Back/Forward and clear scope/count presentation.
- [x] 5.4 Measure browser payload/memory and backend request behavior to confirm no unbounded registry transfer was introduced.

## Completion evidence

Completed 2026-09-17 against upstream develop
`9faec5b3b660498fdef9736e65e331728b55f99c`, reusing the accepted refresh,
shared queries and Vue search workspace.

See [contract, scope, score fixtures, measurements and verification](../../../../docs/frontend-migration/advanced-search-filtering.md).
The current page is the bounded candidate collection (at most 100 records);
no separate prefetched pool is needed for this UX. Both result views and future
analysis consumers share the composable's candidate/visible-item/filter refs.
Boolean, date range, exact category, exact topic URI and declared versioned score
conditions have equivalent local/server tests over the same fixture records.

Build/type-check and all 39 unit tests pass. All 62 focused backend tests pass
on both runtime images. All 31 browser scenarios pass on both Apache and Caddy,
including desktop/mobile candidate scope, zero local fetches, promotion and
history. Production scoring, richer EDAM selection and route cutover remain out
of scope. Canonical legacy routes and the public API are unchanged.
