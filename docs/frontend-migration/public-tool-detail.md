# Public tool detail prototype

Implemented 2026-09-14 in `develop-migration/` against upstream develop
`9faec5b3b660498fdef9736e65e331728b55f99c`, after the baseline refresh and
shared-query extraction. The original parent worktree remains unchanged.

## Preview

- Rich, explicitly fictional record: `http://localhost:8003/_migration/html/tool/detail-demo/`
- Sparse record: `http://localhost:8003/_migration/html/tool/migration-fixture/`
- Legacy comparison: `http://localhost:8003/detail-demo`
- Caddy equivalent: `https://localhost:8443/_migration/html/tool/detail-demo/`

The populated demo is not a claim about real software, contributors or publications.
Its example.org and citation links are illustrative. Other records already in the
local database can be viewed at `/_migration/html/tool/<biotoolsID>/`.

The migration route is noindex/nofollow and points its canonical link to the
still-legacy record URL. No public route, API URL or reverse-proxy mount changed.
`Manage record` and `Edit & ownership requests` open the legacy page, which retains
its account-aware edit/request controls. The prototype itself accepts GET/HEAD
only; browser authentication and mutation workflows are not migrated here.

## Data and safety

`elixirapp.tool_detail.detail` calls `elixir.queries.get_tool_detail`, which reuses
`get_tool` and batch-prefetches only the relations rendered by this page. Templates
consume the ORM record, not an HTTP response or DRF representation. API callers
and serializers are unchanged. The case-insensitive identifier lookup and literal
`biotools:` prefix remain supported, with a trailing-slash page URL.

Visibility remains `visibility=1`. Missing/hidden records receive the shell 404,
even for their owner; private edit permission does not hide public reads. Invalid
identifier syntax receives 404. Empty optional sections are omitted; incomplete
functions and publication metadata do not crash the page.

Stored text is escaped. A shared link tag validates HTTP/HTTPS/FTP/FTPS URLs before
creating anchors; invalid stored URLs become plain text. Identifier links encode
values against fixed resolver hosts. Malformed related identifiers remain text
instead of breaking template reversal. No metadata-enrichment calls run on GET.

## Parity decisions

Reviewed `frontend/components/toolPage/toolPageController.js`, its active partials,
the develop resource/EDAM/credit/publication models and the migration inventory.
Browser checks compare the rendered legacy and Django versions of the same fixture.

| Area | Prototype behavior |
| --- | --- |
| Identity and summary | Name, CURIE, homepage, description, versions, tool types, language, operating systems, license, cost, maturity and accessibility. SPDX links preserve the legacy exceptions. |
| Scientific annotations | Topic, operation, input/output data and format labels plus EDAM URIs. Search links preserve the quoted identifier query parameters used by develop. Function notes and commands are visible, not tooltip-only. |
| Publications | Available identifiers, types, title, authors, journal, publication date, version, notes and abstract. Abstracts use native keyboard-operable details/summary. |
| Downloads and links | Typed documentation, downloads and links, including notes, versions and commands. |
| Attribution | Credits, roles, entity types, URL, obfuscated email and provided external identifiers. |
| Registry metadata | Owner, added/updated timestamps, other identifiers, collections, related tools, ELIXIR platforms/nodes/communities and stored badge flags. |
| Discovery links | TeSS materials/events, OpenEBench, collection and credit search, EDAM search, related migrated records. |
| Machine-readable metadata | Title, description, Open Graph fields, canonical URL and JSON/XML/JSON-LD alternates. Inline JSON-LD generation is not added; the existing API owns that representation. |
| BIP/Dimensions and other metrics | No BIP, Dimensions, Altmetric or Elsevier scripts/objects are embedded. These optional remote widgets are deliberately not reproduced in this read-only prototype; stored bibliographic metadata and DOI/PubMed/PMC links remain. No legacy client-side API key was copied. This is a documented presentation difference, not a claim of metric parity. |
| Legacy-only fields | Removed BioLib/community model data is not resurrected from stale template branches. Current ELIXIR communities and collection IDs remain. |

The page uses the existing white bio.tools logo and blue `#005472` header, ordinary
document sections, a metadata sidebar and stacked mobile layout. It has no scripts,
Vue runtime, htmx requests or third-party asset dependency. Native anchors and
details/summary provide all interactions. No new package dependencies were added.

## Verification

- 47 Django tests pass on both Python 3.13 and Python 3.10.12 / Django 5.2.11:
  seven new detail tests plus all 40 foundation/query tests, including live search.
- 19 browser tests pass on both Apache and Caddy, without skips or retries when
  all fixture flags are enabled. Coverage includes direct links, refresh, Back,
  related sparse records, outbound hrefs, keyboard abstracts, JavaScript disabled,
  browser/bot routing, unchanged API/legacy ownership and rendered legacy parity.
- Desktop 1440px and mobile 390px screenshots were inspected. Logo loading, blue
  header, zero horizontal overflow and absence of third-party requests are asserted.
- Rich-page rendering uses at most 35 SQL queries, including one resource lookup.
  Adding eight functions with inputs/formats, eight publications with authors/types
  and eight credits/roles does not increase that count. Prefetched relation traversal
  requires no further queries. Detail performs no Elasticsearch request.
- Existing MySQL conditional-constraint and naive-timestamp warnings remain visible.
  Initial fixture failures rolled back transactionally; existing records were not changed.

## Run and rollback

Use the [develop stack](develop-refresh.md#run-and-verify). For a fresh stack that
already has the basic browser fixture, seed the rich record once from the
`develop-migration/` directory:

```sh
docker compose -f compose.refresh.json exec -T -e BIOTOOLS_ALLOW_TEST_SEED=biotools-refresh backend python manage.py shell < tests/browser/seed_detail.py
docker compose -f compose.refresh.json exec -T backend python manage.py collectstatic --noinput
docker compose -f compose.refresh.json restart apache
```

The seed refuses existing record/index identifiers and requires the disposable-stack
opt-in and fixture owner. In this local checkout the collected static directory is
root-owned, so collection was run with `exec -u 0`; source files stay in the workspace.
Normal deployments should provision matching static-directory permissions.

```sh
docker compose -f compose.refresh.json exec -T -e BIOTOOLS_TEST_QUERY_ES=1 backend python manage.py test elixirapp.test_tool_detail elixirapp.test_html elixirapp.test_htmx elixirapp.test_query_contracts elixirapp.test_query_search_live --noinput --keepdb
```

Repeat with service `apache` for production Python. Run database suites serially.
For browser verification, use the existing fixture/account environment from the
develop runbook plus `BIOTOOLS_TEST_DETAIL=1`; run `npm test` from `tests/browser/`.
Without that flag the three new detail tests are explicitly skipped. Screenshots
and traces remain in ignored test-output directories; do not publish authentication traces.

Rollback removes the named `tool-detail` pattern from `elixirapp/html_urls.py` and
restarts workers. Canonical routes and the API remain legacy-owned throughout;
there is no schema migration or production data change to reverse.

## Publication presentation: 2026-10-25

The later canonical migration now renders each publication as a separate citation
entry with a title, type, authors, journal/year and identifier links. Abstracts
remain keyboard-operable native disclosures; notes and schema-derived additional
metadata remain visible. Missing enrichment preserves a numbered heading and
working identifier links. Shared citation styling also fixes the About page.
See the [publication correction evidence](public-information-pages.md#publication-presentation-correction-2026-10-25)
for the passing backend/browser checks. This is a presentation correction, not
a rewrite of publication enrichment or stored bibliographic metadata.
