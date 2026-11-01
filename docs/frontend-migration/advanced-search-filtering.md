# Advanced search filtering

Implemented 2026-09-17 in `develop-migration/`, on upstream develop
`9faec5b3b660498fdef9736e65e331728b55f99c`. The accepted develop refresh,
shared query service, Vue runtime and search workspace are prerequisites and
are complete. This extends their actual contract, not the old fork's search.

Preview: `http://localhost:8003/_migration/html/search/?q=Workspace+sample&per_page=10&sort=name&ord=asc`

Expand **Advanced filters**. Setting **Added on or after** to `2026-01-08`
shows three of ten loaded candidates. **Apply to all matches** returns six
matching fictional records, recomputes facets/pages and saves the filter in the
URL. The existing blue shell, public API and canonical legacy routes are unchanged.

## Contract and semantics

The subsequent [EDAM-selector change](edam-selector.md) replaces manual topic-URI
entry in the preview with the reusable selector and additionally validates
promoted topic IDs against the provisioned ontology. That path adds two ontology
SQL reads; the measurements below remain the pre-selector baseline. Other
advanced conditions retain the original request behavior.

`GET /_migration/html/search/data/` accepts one additional `advanced` parameter:
a JSON array of conditions. Conditions are ANDed; values within a categorical
or ontology condition are ORed. There are no executable expressions, arbitrary
operators, user-selected Elasticsearch fields or query scripts.

```json
[{"type":"range","field":"added","scope":"server","min":"2026-01-08"}]
```

| Type | Field | Value and semantics |
| --- | --- | --- |
| `boolean` | `hasPublication` | Boolean `value`: at least one indexed DOI, PMID or PMCID, or its negation. Publication metadata without an identifier does not count. |
| `range` | `added` | Optional inclusive `min`/`max`, strict ISO dates interpreted as UTC calendar days. At least one bound is required. Missing dates do not match. |
| `categorical` | `toolType` | `values`: exact, case-sensitive membership, not legacy fuzzy search. |
| `ontology` | `topic` | `values`: exact `http://edamontology.org/topic_NNNN` URIs. No descendant expansion. |
| `score` | Declared key | Inclusive numeric `min`/`max` and required `version`. Missing scores do not match, including at threshold zero. |

Request validation rejects unknown types/fields/keys/operators, non-Boolean
Boolean values, invalid/reversed dates, nonfinite or out-of-scale numbers,
unknown scores/versions, candidate scope sent to the server, and malformed JSON.
Errors are HTTP 400 with `error.code=invalid_search`, `field=advanced` and a
recoverable message. Validation runs before any Elasticsearch request.
Limits: eight conditions, ten values per membership condition, 256 characters
per value, and 4096 UTF-8 bytes of decoded JSON. Duplicate categorical values
are removed and sorted; object keys are normalized for canonical serialization.
Large saved-filter objects/IDs are not needed for these bounded controls.

The shared service adds validated conditions as `bool.filter` in the query,
not as a post-filter after aggregation/pagination. Counts, facets and navigation
therefore describe the same authoritative set. Relevance scoring and existing
primary query semantics are preserved. This opt-in workspace path does not
change public API fields or envelopes.

The develop index was inspected directly: exact tool types use `toolType.raw`,
topic identifiers use `topic.uri.keyword`, publication identifiers use
`publication.doi/pmid/pmcid`, and added dates use `additionDate`. The historical
`backend/elixirapp/tests/Mapping.json` is not authoritative for these fields.

## Candidate scope and shared state

The candidate collection is the currently loaded server page: 10/25/50/100
records, never accumulated across pages. A separate prefetched pool or cache is
unnecessary for this UX. The response declares
`candidates={scope:"candidate",size,limit:100,complete}`. Completeness is true
only when page one contains every server match.

Compact `filterValues` preserve full tool-type and topic-URI membership, dates,
publication presence and declared scores. Filtering never uses truncated card
labels/descriptions. Only the needed source fields are fetched; full publication
metadata is not returned. Authoritative response items remain unchanged.

`useSearch` owns `localFilters`, `candidates`, `visibleItems`, `setLocalFilters`
and `promote`, alongside canonical `state.advanced`. Both Cards and Table consume
the same computed `visibleItems` and stable IDs. Future selection/comparison or
analysis consumers can use these refs/actions without DOM events or separate
result identity. No speculative selection or chart interface was added.

Local changes recompute immediately with zero fetches and do not change the URL,
authoritative totals or facets. A separate status displays the local numerator,
loaded denominator, server count, and partial/complete scope. Empty candidates
are distinct from an empty server query. Promotion appends the local conditions
as server-scoped conditions and resets page one. It cannot silently broaden an
existing server filter: remove that filter explicitly to widen the search.

Primary-query changes, pagination, promotion, clear, retry and Back/Forward
discard candidate-only state. Server filters survive refresh and history through
the existing canonical URL parser. Local drafts are deliberately not shareable.
Validation failures disable promotion until corrected/cleared. The existing
abort/sequence guard continues to prevent stale query responses replacing newer
state. htmx never targets the Vue-owned subtree.

## Optional derived scores

There is no production score model and no pretend score on preview records.
`SEARCH_WORKSPACE_SCORES` defaults to an empty list. A trusted deployment may
declare a stable key, label, version, numeric scale and a top-level scalar index
field containing that version's scores. For example, tests use:

```python
SEARCH_WORKSPACE_SCORES = [{
    'key': 'fixtureQuality', 'label': 'Fixture quality',
    'version': 'fixture-v1', 'min': 0, 'max': 1,
    'field': 'fixtureQualityV1',
}]
```

Only identity/label/version/bounds are exposed as `scores` in page configuration
and responses; the internal index field is never accepted from the client.
Vue renders numeric threshold controls from this metadata. URLs record the key
and version. Unknown/retired versions fail explicitly rather than being re-bound
to a different definition. Provision a new immutable numeric field and version
when semantics change; do not overwrite an old version's meaning. Multiple
versions under the same key are not currently served concurrently.

`backend/elixirapp/tests/data/AdvancedSearch.json` supplies shared source records
and expected IDs for live Elasticsearch tests and frontend local-execution tests.
It covers publication presence/absence, UTC day endpoints, membership beyond
card truncation, case sensitivity, missing values and score thresholds including
zero. Test settings alone enable fixture scores; no production settings change
or database migration is introduced.

## Measurements

Local disposable Elasticsearch 7.12.1, 125 synthetic documents, two shards;
three warm requests per case. Figures are fixture baselines, not production load
or registry-wide performance guarantees. Each request uses one Elasticsearch
search and zero SQL queries (the tests prohibit database access).

| Query | Response bytes | Python 3.13 median ms | Apache/Python 3.10 median ms |
| --- | ---: | ---: | ---: |
| Unfiltered, 50 candidates | 22,584 | 5.70 | 7.18 |
| Text `sequence`, 50 candidates | 22,592 | 13.16 | 10.69 |
| Primary command-line filter | 22,661 | 7.72 | 6.78 |
| Empty query result | 914 | 8.49 | 6.02 |
| Unfiltered, 100 candidates | 42,541 | 8.87 | 8.15 |
| Advanced exact type, 62 of at most 100 candidates | 27,536 | 6.85 | 7.12 |

The former 50-item baseline was 16,119 bytes. The extra 6,465 bytes carry exact
filter inputs and scope metadata; no additional request or registry transfer is
introduced. The payload scales with the bounded page and the selected records'
metadata, not the total number of registry matches.

Chromium desktop/mobile scenarios with ten of thirteen preview samples measured
7,823 response bytes and 5,531 bytes of serialized candidate items. Their JS heap
snapshots before/after local filtering were approximately 3.5-4.3 MB and
3.4-4.0 MB. These snapshots include page/runtime overhead and GC variability;
they are not retained-heap or leak measurements. Browser checks assert one
initial fetch, no local-edit fetches, and exactly one promotion fetch. State
retains one page only, with no growing candidate history.

Production assets: JS 169.42 kB / 52.29 kB gzip; CSS 5.55 kB / 1.44 kB gzip.
No dependencies, router or state store were added. The existing htmx direct-eval
build warning remains; its runtime eval setting remains disabled.

## Verification and operation

- `npm run build`, `npm run type-check`, and all 39 frontend unit tests passed.
- All 62 focused Django tests passed on both Python 3.13 and Apache/Python 3.10.
- The complete Apache browser suite passed all 31 tests, zero skips/retries.
- All eight search/advanced-filter browser scenarios passed through Caddy;
  its subsequent complete suite passed all 31 tests, zero skips/retries.
  The prior search change's intermittent legacy external-script/login timeout
  did not recur; no legacy analytics-loading fix is claimed.
- Desktop 1440px and mobile 390px screenshots were inspected; controls, scope,
  branding and result layouts render without page overflow or overlapping text.
- Initial browser checks caught uncollected assets; `collectstatic` deployed the
  new bundle before the passing runs. Existing MySQL constraint and naive-date
  test warnings remain unchanged.

From `develop-migration/frontend-modern`, build with `npm run build`. From
`develop-migration`, collect/reload the running disposable stack:

```sh
docker compose -f compose.refresh.json exec -T -u 0 backend python manage.py collectstatic --noinput
docker compose -f compose.refresh.json restart apache
```

Backend checks add `elixirapp.test_advanced_filters` to the
[search workspace regression command](search-workspace.md#run-and-verify).
Set `BIOTOOLS_TEST_QUERY_ES=1` for isolated, auto-cleaned live test indices.
`BIOTOOLS_TEST_SEARCH=1` now includes `advanced-filtering.spec.js`; it reuses the
existing fictional search samples and does not reseed or overwrite them.
See [browser setup](../../tests/browser/README.md) for all opt-in flags.

## Limits and rollback

This is scoped advanced filtering, not route cutover, a production scoring model,
ontology hierarchy selection, an export feature, or a visual redesign. The
future EDAM-selector change owns richer ontology selection. Existing primary
workspace exclusions (domain and nonprimary legacy dimensions) still apply.
Filters are a bounded conjunction, not an arbitrary Boolean expression tree.

To roll back this addition, remove the advanced-controls component/composable
paths, `advanced` parsing and workspace query clauses/source additions, then
rebuild and collect assets. There is no schema/data migration to undo. Alternatively,
disable the isolated HTML mount using the existing migration rollback; canonical
legacy `/t` and the public API were not replaced.
