# Legacy search behavior

Develop review (2026-09-12): see [search and detail](develop-refresh.md#search-and-detail)
for the pinned upstream changes and acceptance limits. That review supersedes
conflicting old-baseline observations below; historical evidence is retained.

Baseline note: this document describes the old `a1fc8b9` worktree.
The [selected upstream develop baseline](baseline.md) has separate completed revalidation;
the source observations and test results below are not develop acceptance evidence.

Inspected commit: `a1fc8b94067f33bc9047efc9c75ebe1579365a07`.
Inspection date: 2026-09-09. Source-derived behavior; browser history and live Elasticsearch results have not been exercised.

## State and entry points

The [search state](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/app.js) owns `/t`. `SearchResultController` in [controllers.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/controllers.js) starts `ToolList.refresh()`, which sends `$stateParams` through `ToolListConnection` to GET `/api/t/`. Results are `{count,next,previous,list}`; the client consumes count/list. [searchBar](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/components/searchBar/searchBarController.js) lives in the navbar on non-home routes, while [homeSearch](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/components/home/homeController.js) supplies the home control. The search toolbar is a separate shell region today; the migration ADR places these interdependent search controls and results in one Vue workspace.

The complete declared search parameter set, preserving spelling, is:

| Category | Parameters |
| --- | --- |
| Query/navigation | `page`, `q`, `sort`, `ord`, `domain` |
| Identity/basic | `biotoolsID`, `name`, `homepage`, `description`, `version`, `owner` |
| Scientific terms | `topic`, `topicID`, `function`, `operation`, `operationID`, `input`, `inputID`, `inputDataType`, `inputDataTypeID`, `inputDataFormat`, `inputDataFormatID`, `output`, `outputID`, `outputDataType`, `outputDataTypeID`, `outputDataFormat`, `outputDataFormatID`, `dataType`, `dataTypeID`, `dataFormat`, `dataFormatID` |
| Classification | `accessibility`, `toolType`, `collectionID`, `maturity`, `operatingSystem`, `language`, `cost`, `license`, `elixirPlatform`, `elixirNode`, `elixirCommunity` |
| Links/downloads/docs | `documentation`, `documentationType`, `link`, `linkType`, `download`, `downloadType`, `downloadVersion` |
| Publications | `publication`, `publicationID`, `publicationType`, `publicationVersion` |
| Credits | `credit`, `creditName`, `creditTypeRole`, `creditTypeEntity`, `creditOrcidID`, `creditGridID`, `creditRORID`, `creditFundRefID` |
| Other identifiers | `otherID`, `otherIDType`, `otherIDVersion`, `otherIDValue` |

Router acceptance is not a guarantee that every parameter is implemented identically by Elasticsearch. [search_settings.py](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/search_settings.py) maps backend search fields/operators; [search.py](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/search.py) applies only keys in `search_struct`. Preserve and test the mapping before changing URLs.

## Tag editing and URL serialization

| Interaction | Source behavior | Regression target |
| --- | --- | --- |
| Restore a URL | `updateQuery()` skips page/sort/ord/domain, turns `q` into `everything` tags by splitting on `+`, and represents other defined parameters as filter tags. Highlights are rebuilt, stripping quote characters from displayed highlight terms. | Reload a URL with multiple terms, quoted strings and named filters; check restored tags and request parameters. |
| Choose filter | Dropdown offers everything, topic, operation, input, output, toolType, language, accessibility, cost, license, credit, collectionID and name. Other declared parameters remain accessible via URLs and links. | Preserve deep-link-only filters rather than restricting to dropdown entries. |
| Add tag | Removes literal `+` from tag text, attaches current filter, resets selected filter to everything. | Literal-plus input, spaces, apostrophes and quoted multiword terms. |
| Serialize tags | All everything tags joined with `+` into `q`; each named filter assigned one string. Multiple tags for the same named filter overwrite earlier values in the outgoing object. | Capture duplicate-filter behavior; decide explicitly whether to preserve or correct it. |
| Change tags | Emits `search-bar-tags-changed`; starts with page 1, existing sort or score, and existing ord/domain. Empty tags clear page/sort. Transitions to search with notifications; a timeout then fetches suggestions/results. | Domain retention, clearing last tag, page reset, removal of old filters and effective UI Router inheritance behavior. |
| Home submit | Tag changes stage `scope.params` and last tag. Submit/Enter calls `doHomeSearch`; only then transitions using staged parameters. Curated topic/operation links supply a quoted term, page 1 and score sort with `inherit:false`. | Empty submission, Enter timing and transition after adding a final tag; home tags differ from navbar's immediate search. |
| Result/detail term link | Search result topic/operation clicks use quoted short EDAM IDs and `inherit:false`; detail also links input/output types/formats, collection, name, credit. Credit opens a new window. | Exact ID/term distinctions and whether previous query/domain survives each entry point. |

Sources: [searchBarController.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/components/searchBar/searchBarController.js), [homeController.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/components/home/homeController.js), [SearchResultController](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/controllers.js), [ToolPageController](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/components/toolPage/toolPageController.js), [services.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/services.js).

## Filtering, suggestions and domain scope

[construct_es_query](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/search.py) separates single/double-quoted terms from unquoted input, strips punctuation in the unquoted portion, builds weighted text/phrase queries, and combines constraints through bool `must` clauses with alternatives within each field group. Free text considers IDs, names, description, collections, EDAM, credits and other metadata; quoted free text has a different field/boost mix. Score, wildcard and phrase semantics depend on the deployed index mapping. There is no separate frontend result filter for the main `/t` list.

The search control makes 13 used-term requests for all/topic/operation/input/output/toolType/language/accessibility/cost/license/credit/collectionID/name. It forwards existing query parameters while clearing page/sort/ord, then matches suggestions locally. [UsedTermsList](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/view/edam.py) aggregates up to 50,000 terms per field and returns a deduplicated set as `data`; order should not be assumed stable. No request cancellation, debounce of these request batches, or stale-response check is visible in the source.

[ResourceList.get](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/view/resource.py) adds domain membership after building the common query: it looks up the domain in ES, lowercases its resource IDs and adds a terms restriction. If a domain is not found, the active code adds no restriction, so an unknown domain can return global results. `UsedTermsList` calls only the common query builder and does not add this membership restriction. Suggestions therefore need not be scoped to the domain even though the client forwards it. [Domain.load](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/components/domain/domainServices.js) separately fetches title/subtitle/description; `DomainBarController` delays loading by 500 ms.

The `/domains` directory is a separate local-search feature: [DomainListController](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/subdomainController.js) fetches `/api/d/all`, sorts names alphabetically and uses Fuse with threshold 0.2, minimum match length 2, tokenization and weighted fields. Domain always participates; title, subtitle, tags and collection default on; description/tool name/tool ID default off. An empty query restores the original list. These controls and results have no URL/history serialization.

## Sorting, pagination and presentation

| State | Representation and observed behavior |
| --- | --- |
| Sort field | `ToolSorter`: Updated (`lastUpdate`, default), Added (`additionDate`), Name (`name`), Citation Count (`citationCount`), Publication Date (`citationDate`); Score (`score`) is inserted when a query is present or score arrives in URL. Backend maps score to `_score` and citation sorts to publication metadata fields. |
| Sort direction | Boolean client `order`, true -> `desc`, false -> `asc`; default Updated/descending removes both URL keys. Dropdown/direction changes transition with `notify:false` and explicitly refresh. Invalid sort lookup has no reliable client fallback (`findIndex` can return -1). No deliberate page reset in the sort handler. |
| Pagination | Client page size 10, maximum five visible page buttons; server uses configured `PAGE_SIZE` (default 10). Page 1 is omitted from URL by paginator; other pages set `page`. Transitions use `notify:false` then refresh. Deep `Query.current` watch resets local page to 1; initialization includes a special watcher to undo premature resets. |
| Server paging | ES `size=PAGE_SIZE`, `from=PAGE_SIZE*(page-1)`, `track_total_hits:true`. No result with positive total -> 404 invalid page; count zero -> normal empty list. Page parsing uses `int`; malformed/negative values are not explicitly validated here. Server next/previous strings contain only page. |
| Result display | `DisplayModeSelector` is an in-memory service: `cards` = Compact (default), `grid` = Detailed. Mode changes issue another list refresh. Mode is not encoded in URL or explicitly saved to localStorage. |
| Grid preferences | `gridState` JSON in localStorage stores/restores ui-grid state on visibility, resize and column-position events. Default visible fields: Name, Description, Homepage, Credits, Operation, Topic, Input, Output. Grid sorting is disabled; uses global sort. Version visibility is erroneously based on Homepage in `columnsDescription`; record rather than copy unquestioningly. |
| Display transforms | Cards flatten operations across functions keyed by term text; search highlighting removes quotes. Publication/credit/EDAM/collection links expose richer detail or initiate a new search. |
| Loading/errors | Shared loading flag and spinner; zero results message. `ToolList.refresh` defines no failure callback, so a failed request can leave loading active. Older responses can overwrite newer list/count data. |

Sources: [services.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/services.js), [directives.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/directives.js), [controllers.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/controllers.js), [search_results.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/search_results.html), [resource.py](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/view/resource.py).

## History and regression baseline

HTML5 URLs represent server search state; UI Router transitions do not explicitly request history replacement. Tag changes notify state listeners, while sorting/pagination suppress notifications and manually fetch results. State-success listeners rebuild tags and sort options; grid settings and display mode follow separate persistence rules. Back/Forward, reload and direct-link equivalence are intended by these mechanisms but not verified. Do not report them as passing tests.

Minimum later browser/API scenarios: plain and quoted text; EDAM IDs; multiple/deduplicated filter tags; domain + text and missing domain; every supported sort/direction; page 2 and empty/out-of-range pages; Back/Forward after tag/sort/page changes; reload with grid preferences; leave detail and return; slow/out-of-order requests, API failure and retry. Capture both URL and result identities/count, not only screenshots. Main search results, suggestions, selection and later analytical filters must share one Vue-owned workspace as specified in the [ADR](adr-001-frontend-ownership.md).
