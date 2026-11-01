# Complete search filter parity

Local acceptance: 2026-10-22, pinned develop
`9faec5b3b660498fdef9736e65e331728b55f99c`. Runtime changes live only in
`develop-migration/`. This is not production activation or permission to remove
AngularJS. It resolves B02 and the search fallback portion of B08 in the
[removal audit](legacy-removal-audit.md).

## Compatibility matrix

The declared `/t` parameters in `frontend/js/app.js` were compared with
`backend/elixir/search_settings.py:search_struct`, `construct_es_query`, shared
queries and actual producers. All 61 filter keys below are functional under the
deployed Elasticsearch mapping. None is retired or silently ignored. The
`SearchParity.json` fixture has one positive example per key; live tests compare
identifiers and counts with the unchanged public query engine, not just HTTP 200.

| Family | Supported keys | Contract / producer |
| --- | --- | --- |
| Identity and text | `biotoolsID`, `name`, `homepage`, `description`, `version`, `owner` | Existing text/phrase query builder; homepage fixture uses the full quoted URL because of its deployed analyzer. Router, search tags and record links. |
| Scientific annotations | `topic`, `topicID`, `function`, `operation`, `operationID`, `dataType`, `dataTypeID`, `dataFormat`, `dataFormatID`, `input`, `inputID`, `inputDataType`, `inputDataTypeID`, `inputDataFormat`, `inputDataFormatID`, `output`, `outputID`, `outputDataType`, `outputDataTypeID`, `outputDataFormat`, `outputDataFormatID` | Existing mapped field groups, including shared input/output aliases. Quoted compact EDAM IDs from detail/result links remain supported. |
| Classification | `toolType`, `collectionID`, `maturity`, `operatingSystem`, `language`, `cost`, `license`, `accessibility`, `elixirNode`, `elixirPlatform`, `elixirCommunity` | Existing backend fields; activated descriptor supplies labels and choices. Search tags, curated home links and URL bookmarks. |
| Credits | `credit`, `creditName`, `creditTypeRole`, `creditTypeEntity`, `creditOrcidID`, `creditGridID`, `creditRORID`, `creditFundRefID` | Existing nested metadata mappings; record credit links and router bookmarks. |
| Publications | `publication`, `publicationID`, `publicationType`, `publicationVersion` | Existing DOI/PMID/PMCID and metadata mappings. `publicationID` is an existing grouped search alias, not a new stored field. |
| Links and files | `link`, `linkType`, `documentation`, `documentationType`, `download`, `downloadType`, `downloadVersion` | Existing nested metadata mappings, router bookmarks and schema-backed filter controls. |
| Other identifiers | `otherID`, `otherIDType`, `otherIDVersion`, `otherIDValue` | Existing nested identifier mappings and router bookmarks. |
| Domain | `domain` | Intersects the query with lowercased, deduplicated indexed membership IDs. Home/community/domain-directory links. Empty or missing domains produce zero workspace results; failed/partial membership lookup produces 503. |
| Navigation | `q`, `sort`, `ord`, `page`, `per_page` | Six existing sorts; ascending/descending; sizes 10/25/50/100; maximum 10,000-result window. Default workspace size remains 50. Legacy services, unlike the router declaration, supply `per_page`. |
| Advanced filters | `advanced` | Existing validated JSON server-filter contract. Candidate-local filters remain local until explicit promotion; view changes preserve those filters and the current page. |
| Presentation | `view=cards`, `view=table` | New reproducible workspace view state; legacy cards/grid mode was in-memory. Table uses the same bounded filtered result set. |
| Invalid/historical input | Unknown keys, invalid sort/page/view, malformed advanced JSON, controls/backslashes, overlong or punctuation-only text | Actionable 400, never automatic legacy fallback or silent broadening. There were no additional functional declared legacy filter keys to retire. |

Repeated query keys use the public API's **last value wins** semantics, including
control keys. The enhanced client canonicalizes repeats; native pagination
preserves the query and uses the same last-value parser. Blank text filters are
omitted. Encoded spaces, ampersands, literal plus signs and quoted terms survive.
The existing builder preserves phrase/fuzzy matching and AND across constraints;
keys mapped to several fields retain their existing alternatives. This change
does not rewrite nested-query semantics or ranking.

The missing-domain safeguard intentionally differs from the legacy public API,
which can return global results for a missing domain. That external API behavior
and its response representation remain unchanged; the workspace fails closed.
No new model field, index migration or automatic schema activation is introduced.

## Producers and result workflows

| Producer | Disposition |
| --- | --- |
| `frontend/js/app.js`, `frontend/js/services.js`, searchBar/home controllers | Existing supported keys and canonical `/t` targets remain valid. Existing cross-page document navigation enters the native owner. |
| `frontend/components/toolPage/toolPageController.js`, `frontend/js/controllers.js` | Existing quoted compact EDAM-ID links are accepted unchanged. |
| `backend/elixir/templatetags/detail_tags.py`, `templates/html/tool_detail.html`, `templates/html/detail/io.html` | Existing `search_url`/`edam_term` links already use canonical `/t` and the correct ID keys; no URL rewrite needed. |
| `frontend/components/{home,community}/*.html`, `frontend/partials/subdomains/domains.html` | Domain links now resolve directly to native results. The source pages themselves remain owned by the later public-information change. |
| Workspace and native GET form | State, history, pagination, view and active constraints use one validated search payload. Errors render at their real 400/503 status. Unknown native parameters remain visible to validation on submission instead of disappearing. |
| Cards and detailed comparison | Cards retain compact summaries and record links. Table exposes every descriptor-approved public top-level field, recursively including approved nested function/credit/etc. fields; enhanced users select columns, native users scroll all columns. No private permission fields or unknown nested values enter the projection. |
| Record exports | Existing record JSON/XML API links remain unchanged. No bulk search export command was found in the legacy search UI. Editor draft JSON export is a separate existing workflow. |

Comparison replaces the ui-grid rendering dependency, not access to the underlying
public data. Legacy grid drag/resize and its saved `gridState` layout are not
ported or deleted; the explicit rollback still exposes them. Enhanced column
selection currently lasts for the mounted workspace only. Cross-page polish and
retirement review must resolve layout preference migration before claiming exact
legacy presentation parity. No legacy code/dependency is removed here.

Filter labels, enum choices and comparison fields come from the activated schema
descriptor. Existing search aliases were added to the backend UI policy; its new
approved revision is
`6ab2490fa587b187de771a4c4cdc89da6407c83b5c31413de6de967b58b1a535`.
Capability declarations describe existing backend support, not arbitrary automatic
index construction. The prior same-build schema activation evidence remains
historical and is not being claimed as a new rehearsal for this revision.

## Fixtures and reproduction

`backend/elixirapp/tests/data/SearchParity.json` covers every backend key and
nested/encoded metadata. `test_search_parity.py` copies the deployed resource
mapping into uniquely named disposable indices and deletes those indices on exit.
Set `BIOTOOLS_TEST_QUERY_ES=1` only with disposable services.

The browser fixture adds a dedicated `search-parity-fixture` domain around the
13 existing search samples. Seed existing browser/search samples first, then run
once from the implementation root:

```sh
docker compose -f compose.refresh.json exec -T -e BIOTOOLS_ALLOW_TEST_SEED=biotools-refresh backend python manage.py shell < tests/browser/seed_search_parity.py
```

The script requires the disposable-stack sentinel, refuses an existing domain,
checks the sample records/index entries and never overwrites existing records.
It is not a production seeder. The preview is
`http://localhost:8003/t?domain=search-parity-fixture`.

From `tests/browser`, run:

```sh
BIOTOOLS_BASE_URL=http://localhost:8003 BIOTOOLS_TEST_SEARCH_PARITY=1 BIOTOOLS_TEST_SEARCH=1 BIOTOOLS_TEST_CUTOVER=1 BIOTOOLS_TEST_DETAIL=1 BIOTOOLS_TEST_TOOL_ID=migration-fixture BIOTOOLS_TEST_QUERY=Migration PLAYWRIGHT_BROWSERS_PATH=/tmp/biotools-playwright npm test -- search-parity.spec.js search-workspace.spec.js advanced-filtering.spec.js cutover.spec.js --output=test-results-search-parity-apache
```

For Caddy use `BIOTOOLS_BASE_URL=https://localhost:8443`,
`BIOTOOLS_TEST_LOCAL_TLS=1` and output `test-results-search-parity-caddy`.
Do not rebuild assets, alter the active descriptor or restart services during
these runs. The fixture journeys are read-only after seeding.

## Acceptance evidence

Verified on 2026-10-22 with deployed JS `main-czHrXrdr.js`, CSS
`main-ncpGur7D.css` and the descriptor revision above:

- 99 modern unit tests, type check and production build passed.
- All 194 backend regression tests passed separately on Python 3.13 (backend)
  and Python 3.10 (Apache), with live Elasticsearch enabled. The eight focused
  parity tests passed again on both runtimes after adding the explicit native
  timeout/503/retry assertion.
- All 20 browser journeys passed through Apache, and all 20 through Caddy HTTPS,
  with one worker and no retries. This includes six new 1440px/390px enhanced,
  no-JavaScript and failed-asset journeys, plus existing history/race, candidate
  promotion, error/retry, proxy isolation and legacy navigation checks.
- Screenshots were inspected for enhanced desktop/mobile, native mobile and
  failed-asset desktop. Blue branding is retained; tables scroll within their
  region, with no document overflow or overlapping controls in those views.
- Descriptor drift check and strict OpenSpec validation passed. Artifacts are
  `tests/browser/test-results-search-parity-{apache,caddy}/`.

The candidate-view regression found during verification is fixed: toggling
cards/table retains candidate filters and the current page. It fetches the
requested representation, but does not promote candidate constraints to the
full query. Unit and desktop/mobile browser assertions cover that distinction.

Existing htmx build-eval, MySQL conditional-constraint and fixture-date warnings
remain; they are not new test failures. The public REST compatibility tests pass,
but this is not a complete security audit or a production-scale benchmark.
Production-scale performance, configured external providers and live email are
not part of this local search acceptance. Production switches remain unchanged.

## Nested filter presentation: 2026-10-23

The flat list is replaced with ten collapsible top-level groups in both Vue and
the native GET form. Functions contain Operations, Inputs and Outputs; input and
output groups contain their Data and Format controls. Topics, Credits,
Publications, Links, Documentation, Downloads and Other identifiers follow the
activated schema labels. Scalar fields live under Tool details, and the
registry-only domain filter has its own Registry group.

The backend derives hierarchy from the shared query mappings and the activated
descriptor, without a frontend field catalogue. Cross-input/output aliases stay
under their common Functions ancestor. Every supported key appears exactly once.
Active ancestors open on load and show active counts; collapsing a group does
not remove its constraints. Query semantics, URLs and public APIs are unchanged.

Verification: 100 modern unit tests, type check and build passed; 42 focused
schema/search/cutover backend tests passed on each Python runtime with live ES.
All 20 browser journeys passed on each proxy, including nested-field submission,
reload, keyboard collapse/expand and no-JavaScript/failed-asset paths at 1440px
and 390px. Screenshots were inspected without document overflow or overlapping
controls. Artifacts: `tests/browser/test-results-nested-filters-{apache,caddy}/`.
Deployed assets: `main-DidFc-OB.js` and `main-BxxHbfie.css`; descriptor unchanged.
This focused follow-up does not repeat production readiness or the full editor
regression suite.
