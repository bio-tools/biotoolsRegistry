# Shared query services

Implemented against upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`
on 2026-09-13, after the [baseline refresh](develop-refresh.md). All commands and
source paths below refer to the separate `develop-migration/` checkout.

## Entry points

`backend/elixir/queries.py` provides two ordinary Python functions:

```python
from elixir.queries import get_tool, search_tools

tool = get_tool('biotools:signalp')
result = search_tools(
    {'q': 'alignment', 'toolType': '"Command-line tool"', 'sort': 'name', 'ord': 'asc'},
    page=1, per_page=25,
)
```

- `get_tool(identifier)` returns a `Resource` model using one case-insensitive
  ORM lookup with `visibility=1`. Bare identifiers and the literal `biotools:`
  prefix are supported. Missing and hidden tools raise `ToolNotFound`, including
  for their owners. Private **edit** permission does not make a visible tool private.
- `search_tools(query_params, *, page, per_page)` accepts a string-valued mapping
  or `QueryDict` containing current `q`, filters, `sort`, `ord` and `domain`
  parameters. Explicit pagination overrides mapping values without modifying the
  input. Repeated QueryDict parameters retain the existing last-value semantics.
  The existing `construct_es_query` remains authoritative, also for used-term queries.
- `ToolSearchResult` contains `items` (unmodified Elasticsearch source documents),
  `count`, `page`, `per_page`, `backend_requests` and `elapsed_ms`. It contains no
  HTTP response, serializer output newly constructed by the service, or page URLs.
- `SearchPageNotFound` means matches exist but the requested page is empty.
  `InvalidQuery` means the existing builder cannot parse an input. Elasticsearch
  transport/query errors propagate unchanged; do not hide them as empty success.

Search issues one Elasticsearch request, or two with a domain filter. It performs
no ORM hydration, database logging or per-result lookups. Count and timing metadata
are available to callers without exposing query text in a new log. Detail
serialization retains its existing related-object queries; no eager-loading or
serializer optimization is claimed by this extraction.

## API and permissions

`ResourceList.get` retains HTTP pagination parsing, search logging and the
`count`/`next`/`previous`/`list` response envelope. Indexed fields pass through
unchanged, including fields not present in the ORM serializer. Pagination links
remain `?page=N`; no new query-preserving URL contract is introduced here.

`ResourceDetail.get_object` maps `ToolNotFound` to the existing 404 and still calls
DRF object permissions before returning the model. GET uses `ResourceSerializer`;
PUT/DELETE retain their existing permissions and mutations. Other write helpers
and validators were not consolidated because they have distinct behavior.

Domain views/serializers are unchanged. Contracts verify that ordinary users see
their visible owned **or edited** domains, without duplicates, with `isOwner` and
`isEditor`. Anonymous and superusers receive the public `name`/`resourcesCount`
shape; unrelated ordinary users receive no managing domains. This is not a new
privacy policy: `is_private` is not an authorization filter in these existing reads.

New HTML callers must map domain exceptions themselves and apply write permissions
and CSRF for any mutation; `get_tool` is not write authorization. No server-side
HTTP call to the registry API was introduced. API renderers and serializers remain
in the presentation layer; search uses the existing indexed representation.

## Preserved limitations

The API still defaults to 50 results and caps size at 100. Invalid `per_page` text
falls back to the configured default. Zero size retains the old empty-page outcome;
negative pagination/backend-invalid inputs are not newly normalized. Malformed
`page` text still raises before execution rather than receiving a new 400 contract.
Future browser forms should validate positive integers before calling the service.
Sort aliases, boosts, filters and default lastUpdate-descending ordering are unchanged;
equal sort keys have no new tie-break guarantee.

A missing indexed domain currently leaves the query unfiltered; an existing empty
domain adds an empty terms filter. Tests retain both behaviors. Treat domain input
as a search filter, not an authorization boundary. Changes need separate approval.
The broad identifier route consumes `.json` as part of the identifier; format
selection through `?format=json` remains supported. No URL changes are included.

## Verification

Before extraction: 11 API/ORM/mocked-search contracts and one live Elasticsearch
test passed. They freeze detail fields/aliases/errors, visibility, domain management,
pagination, filter composition, ordering and exact representative response bodies.
After extraction: the same checks plus four direct-service checks pass, together
with the 24 foundation tests: **40 tests on Python 3.13 and Python 3.10.12**.
Both use Django 5.2.11. **57 existing API/permission/CRUD/parameter tests pass**.
The full browser suite passes through Apache and Caddy, **16 tests each**, no skips
or retries. No frontend build changes were required.

From the integration checkout, with the [refresh stack](develop-refresh.md#run-and-verify) running:

```sh
docker compose -f compose.refresh.json exec -T -e BIOTOOLS_TEST_QUERY_ES=1 backend python manage.py test elixirapp.test_query_contracts elixirapp.test_query_search_live elixirapp.test_html elixirapp.test_htmx --noinput --keepdb
# Repeat with service "apache" for the production Python runtime.
```

The new ORM contracts use Django's test database. The opt-in live test creates and
cleans up only a UUID-named index, using the production analyzers for its exercised
fields. Without `BIOTOOLS_TEST_QUERY_ES=1` that live test is explicitly skipped.
Search logging is mocked for read-only contract tests, not disabled in the app.

The upstream suite mutates hard-coded indexes, so use the test overlay to isolate it
from the preview. Run database suites serially:

```sh
docker compose -f compose.refresh.json -f compose.query-tests.yml up -d --wait query-test-elasticsearch
docker compose -f compose.refresh.json -f compose.query-tests.yml run --rm --no-deps -T backend python manage.py test elixirapp.tests.authorization_permission elixirapp.tests.cruds elixirapp.tests.parameters --noinput --keepdb
docker compose -f compose.refresh.json -f compose.query-tests.yml rm --stop --force --volumes query-test-elasticsearch
```

Existing MySQL conditional-constraint, naive timestamp and allauth deprecation
warnings remain visible. Upstream tests print disposable authentication data;
do not publish their raw logs. No production/provider checks are implied.

Rollback restores `ResourceList.get` and `ResourceDetail.get_object` to their
pre-extraction implementations and removes `elixir/queries.py`. Restart workers;
there are no schema, data, route, asset or dependency migrations.
