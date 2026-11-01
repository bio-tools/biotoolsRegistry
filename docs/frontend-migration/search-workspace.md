# Vue search workspace

Baseline: upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
The develop refresh, shared query services and Vue island runtime are complete.
Implementation remains in the separate `develop-migration/` checkout.

Preview: <http://localhost:8003/_migration/html/search/> or
<https://localhost:8443/_migration/html/search/> (local certificate).
Pagination example:
<http://localhost:8003/_migration/html/search/?q=Workspace+sample&per_page=10&sort=name&ord=asc>.
The preview contains fictional local samples, not a copy of the public registry.

## Develop characterization

Reviewed `frontend/components/searchBar/searchBarController.js`,
`frontend/js/services.js`, `frontend/js/directives.js`, `frontend/js/app.js`,
`frontend/js/controllers.js`, `backend/elixir/search.py`, `search_settings.py`,
`view/edam.py`, and the actual `es_regenerate.py` mapping.

- The primary search bar exposes everything (`q`), topic, operation, input,
  output, tool type, language, accessibility, cost, license, credit, collection
  and name. Those 12 named dimensions are all present in the new workspace.
- Unquoted input uses the existing fuzzy/prefix query builder; quoted phrases
  retain its phrase semantics. Facet buttons submit quoted values. The browser
  never implements its own matching logic.
- API defaults are Updated descending and 50 results per page. The legacy UI
  initially chooses Score when adding search tags; the new UI retains its visible
  sort selection and exposes Relevance explicitly. Direct URL/query semantics
  remain the shared service's semantics.
- The legacy paginator offers 10/25/50/100 and keeps its selected size in a
  singleton. Its directive writes `per_page`, but the search state's declared URL
  parameters omit it and initialization only reads `page`. The new workspace
  deliberately fixes page-size deep-link/refresh/history persistence instead of
  copying that defect. The browser suite records legacy observations separately.
  Observed on the live develop build: a `per_page=10` deep link displayed all 13
  samples and an unmatched default-50 select option. Selecting 10 showed ten
  cards but removed `per_page` from the URL. Back/Forward retained the singleton's
  ten-result setting; refresh reset it to 50 and displayed all 13 again.
- Legacy Cards/Table is ephemeral, not URL state. Its table supports many optional
  configurable columns, including Added/Updated, stored as `gridState` in browser
  storage. The compact replacement provides Name, Description, Tool type, Added
  and Updated in its table, plus topic/operation summaries on cards. Full metadata
  remains on detail pages. Column personalization is not migrated by this change.
- The public API's historical malformed-page/size handling is intentionally left
  unchanged. New endpoint validation is tested separately from supported-query
  parity, including zero, negative, fractional, oversized and nonnumeric values.

## Routes and ownership

`GET /_migration/html/search/` renders the existing Django shell and one
`search-workspace` root. Escaped configuration is passed using `json_script`
inside an inert template, following the island-runtime convention. The Vue root
has `hx-disable` and no internal htmx targets. Django still owns page routing;
there is no Vue Router, Pinia, alternate build pipeline or site-wide SPA.

`GET /_migration/html/search/data/` serves the frontend DTO. Existing `/api/t/`
and `/api/tool/` contracts and `/t` route ownership are untouched. Detail links
point to the existing Django detail prototype. Without JavaScript, the page
retains a native search form and browse link to the legacy `/t` experience.

`search-state.ts` centrally parses/validates/canonicalizes URL state using
`URLSearchParams`. Default values and empty parameters are omitted. Result state
is pushed into history, while successive keystrokes inside one debounce window
replace the pending entry. Back/Forward parses the URL afresh. Query drafts retain
trailing spaces while typing; canonical requests trim them. Cards/Table mode,
expanded filters and the go-to-page draft stay out of the URL.

The component owns its results, facets and controls; stable `id` values and
`data-tool-id` attributes provide later selection/comparison integration points.
No speculative selection store or nonfunctional comparison buttons are added.

## Frontend contract

The subsequent [advanced-filtering change](advanced-search-filtering.md) extends
this contract with validated `advanced` conditions, exact candidate filter
values, scope metadata and optional versioned score declarations. The original
implementation and measurements below remain the pre-extension baseline.

Parameters are single-valued strings: `q`, the 12 named dimensions above, `sort`,
`ord`, `page`, `per_page`. Unknown or repeated keys are rejected, not silently
ignored. Text/filter values are limited to 256 characters; control characters and
backslashes are rejected before entering the legacy string-based query builder.
Filter text is a search expression, not a closed enum: an unknown ordinary term
is a valid empty-result search, while an unknown filter dimension is an error.

Sort keys: `lastUpdate`, `additionDate`, `name`, `score`, `citationCount`,
`citationDate`; directions: `asc`/`desc`. Page sizes: 10/25/50/100. Pages must be
positive integers and cannot extend beyond Elasticsearch's 10,000-result window.
The DTO reports whether this browse limit was reached. Narrow the query to
explore further; this is bounded offset pagination, not a cursor implementation.

Successful JSON contains:

```json
{
  "items": [{"id": "example", "name": "Example", "description": "...", "url": "/_migration/html/tool/example/", "toolTypes": [], "topics": [], "operations": [], "added": "2026-01-01", "updated": "2026-02-01"}],
  "count": 1,
  "facets": {"toolType": {"values": [{"value": "Command-line tool", "count": 1}], "truncated": false}},
  "state": {"q": "", "sort": "lastUpdate", "ord": "desc", "page": 1, "per_page": 50},
  "pagination": {"page": 1, "perPage": 50, "pages": 1, "previous": null, "next": null, "limited": false}
}
```

Descriptions are capped at 400 characters, tool types at four, and topics and
operations at five each. Only those source fields are fetched, never full tool
documents or all matching results. Vue renders text, not record-supplied HTML.

`search_tools(..., workspace=True)` reuses the existing query construction and
adds source projection, facets and a deterministic ID tie-breaker. With the
default `workspace=False`, the public API's Elasticsearch request is unchanged.
One Elasticsearch request obtains results, exact total and facets for the current
query, with no SQL/ORM queries. No separate public-API HTTP call is involved.

Facets are query-constrained, including active filters, rather than disjunctive
counts with each facet's own filter removed. At most 30 values per dimension are
returned, alphabetically, with a `truncated` flag. The UI shows five quick choices
and exposes returned suggestions in a native datalist; arbitrary filter text
remains available. Key ordering gives exact counts for the returned buckets
across shards. Input/output combine their data/format keyword fields in a fixed
server-side script with per-document deduplication, not sums that double-count
resources. This is tested on a two-shard temporary index.

Errors are JSON `{ "error": { "code": "...", "message": "...", "field": "..." } }`:
`invalid_search`/`invalid_page` use HTTP 400; `search_unavailable` uses 503. `field`
is optional. Backend timeouts/partial results are failures, never empty successes.
Elasticsearch has a five-second search timeout and eight-second transport limit;
the browser stops waiting after 12 seconds. Text input is debounced by 300ms.
Any new state immediately aborts the previous request and invalidates its sequence
number, so even a transport ignoring abort cannot overwrite newer results.

## Run and verify

Use the existing [develop stack](develop-refresh.md#run-and-verify). From the
develop checkout, build and collect assets, then reload Apache:

```sh
cd frontend-modern
npm ci
npm run type-check
npm test
npm run build
cd ..
docker compose -f compose.refresh.json exec -T -u 0 backend python manage.py collectstatic --noinput
docker compose -f compose.refresh.json restart apache
```

The fixture script requires the existing disposable `migration-test` owner and
refuses to overwrite any of its 13 IDs. It never purges a database or index:

```sh
docker compose -f compose.refresh.json exec -T -e BIOTOOLS_ALLOW_TEST_SEED=biotools-refresh backend python manage.py shell < tests/browser/seed_search.py
docker compose -f compose.refresh.json exec -T -e BIOTOOLS_TEST_QUERY_ES=1 backend python manage.py test elixirapp.test_search_workspace elixirapp.test_query_contracts elixirapp.test_query_search_live --noinput --keepdb
cd tests/browser
BIOTOOLS_BASE_URL=http://localhost:8003 BIOTOOLS_TEST_SEARCH=1 npm test -- search-workspace.spec.js
```

The live backend tests create and remove only a unique `workspace-contract-*`
index with 125 records. They do not change the preview's index. Set
`PLAYWRIGHT_BROWSERS_PATH` for a nondefault Chromium cache. Caddy uses origin
`https://localhost:8443` and `BIOTOOLS_TEST_LOCAL_TLS=1`. Full regression runs also
enable the HTML, detail and island flags and the existing disposable credentials.

## Measurement baseline

2026-09-16, Elasticsearch 7.12.1, two shards, 125 synthetic resources, 50-result
responses; median of three warm requests. These are local baselines, not a
production-capacity claim. The live test prints reproducible measurements.

| Search | JSON bytes | Python 3.13 search ms | Python 3.10 search ms |
| --- | ---: | ---: | ---: |
| Unfiltered | 16,119 | 6.48 | 5.23 |
| Text `sequence` | 16,127 | 15.24 | 12.92 |
| Command-line tool facet | 16,148 | 7.34 | 7.25 |
| Empty result | 803 | 8.15 | 6.87 |

Each case uses one Elasticsearch request and zero database requests, independently
of the result count. The search duration is exposed as `Server-Timing: search`.
The production modern bundle is 159.38 kB (49.73 kB gzip), with 4.41 kB CSS
(1.23 kB gzip). The existing htmx build-time eval warning remains; runtime eval
and response script execution remain disabled.

## Cutover limitations and rollback

This change covers the current primary discovery controls, not every advanced
legacy parameter. Domain searches, EDAM URI-specific filters, non-primary fields,
column customization, export, comparison and candidate-only filtering are not
implemented here. Unsupported parameters return an explicit error. Canonical
cutover must account for those routes/links and approved scope decisions; this
prototype must not silently replace `/t` yet. Visual redesign is still deferred.

For rollback, remove the two HTML route entries and the `search-workspace`
registration/import, rebuild and collect the modern assets. The ordinary legacy
search and public API remain available. No schema migration is introduced.
Do not delete existing records as a rollback action; disposable samples can remain
in the local preview until its whole isolated environment is retired.

## Verification record

Completed 2026-09-17; implementation and test runs performed 2026-09-16 against
the pinned develop checkout. Production build and TypeScript checks pass, along
with all 28 modern unit tests. All 57 focused Django migration tests pass on both
Python 3.13 and Apache's Python 3.10 runtime (Django 5.2.11), including public API
contracts, six sort modes, all primary facets and isolated live Elasticsearch.

The final Apache browser run passed all 28 scenarios without skips or automatic
retries. All five search-workspace scenarios also passed through Caddy HTTPS,
including real endpoint pagination/filter parity, mobile/desktop navigation,
malformed inputs, failure recovery, request races and legacy characterization.
Desktop/mobile screenshots were inspected: blue branding and logo load, controls
and record text fit, filters collapse on mobile, and no page-level overflow.
All 17 OpenSpec changes pass strict validation; whitespace checks pass.

The complete Caddy run is **not fully green**: the final run passed 27 tests and
timed out loading the legacy login page, before entering credentials. Its trace
shows a pending `plausible.galaxyproject.eu/js/script.js` request and slow external
badge/font assets. An earlier Caddy run instead timed out on anonymous registration
while its authenticated flow passed. No search test failed in either run.
Initial Apache discovery checks also waited on remote assets; legacy test
navigation now waits for DOMContentLoaded plus its existing UI assertions instead
of the complete load event. This reduces, but does not eliminate, dependence on
third-party deferred scripts. No remote requests were mocked to claim a passing
full suite, and no legacy application/authentication behavior was changed.

Production cutover still needs a clean provisioned-stack regression gate and the
scope decisions above. The isolated search implementation is complete; this
record is not approval to replace canonical routes or remove the old frontend.

References: [Elasticsearch 7.12 terms counts and ordering](https://www.elastic.co/guide/en/elasticsearch/reference/7.12/search-aggregations-bucket-terms-aggregation.html),
[Vue lifecycle/reactive cleanup](https://vuejs.org/guide/essentials/watchers.html).
