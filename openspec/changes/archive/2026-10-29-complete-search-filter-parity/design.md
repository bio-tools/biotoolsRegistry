## Scope and Contract

Compare every search-state key in frontend/js/app.js with construct_es_query,
shared queries and existing UI producers. Classify each as supported, alias,
invalid or historical/nonfunctional, with fixtures. The declared router alone is
not evidence that a parameter works. Record duplicate-key semantics, encoded
values, empty values, combined constraints, domain membership, sorting, paging
and malformed input. No silent broadening of a query is acceptable.

## Decisions

- Extend the existing shared query service and modern search state; do not build
  a second search engine or change public API response representations.
- Reuse existing facets/EDAM controls. Handle supported legacy text/ID and nested
  metadata filters explicitly, with inspectable active constraints.
- Keep candidate-local filtering and full-set promotion distinct; parity must
  not turn a page-local result into a claimed registry-wide result.
- Native GET search renders actual results and pagination with the same validated
  constraints. It is not a link to an Angular search shell.
- Preserve repeated-key semantics where characterized as supported. If an input
  is genuinely invalid, return an actionable error rather than ignoring it.
- Characterize legacy result modes/export links as part of parity. Preserve
  meaningful comparison/export workflows with existing components; document any
  proposed retirement for explicit approval instead of recreating a grid library
  solely for visual similarity.

## Verification and Rollback

Use seeded domain/EDAM/nested-metadata fixtures and real Elasticsearch contract
tests. Compare counts and identifiers, not just a successful HTTP response.
Cover reload, shared bookmarks, Back/Forward, escaped/repeated values, empty and
failed searches, query limits, native GET and enhanced paths on both proxies.
Keep _legacy only as temporary rollback until retirement; normal supported search
must not use it. Update every link producer discovered in the matrix.

## Non-Goals

No new ranking model, unbounded queries, new schema fields or general search
engine rewrite. Existing error/data-exposure protections remain mandatory.
