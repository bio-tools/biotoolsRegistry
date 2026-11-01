## Baseline

Target: upstream develop pinned at `9faec5b3b660498fdef9736e65e331728b55f99c`, implemented only in `develop-migration/`. Review the current migration work on top of that baseline, not the older outer runtime.
See the [dependency audit](../../../../docs/frontend-migration/legacy-removal-audit.md) and [finishing sequence](../../../README.md#finishing-sequence).

## Why

The homepage, informational content, public domains, statistics and documentation redirects still require AngularJS. Literal routes and shared content assets must be preserved before the SPA fallback can be retired.

## What Changes

- Serve home, about, community aliases, public domains and statistics using Django-owned routes and the existing blue shell.
- Replace schema/meta-refresh and fixed documentation redirect states with explicit server redirects.
- Preserve source content, statistics data, domain/search links, referenced images and meaningful metadata.
- Provide native navigation, real error statuses and browser/crawler ownership through both proxies.

## Dependencies

Depends on completed shell/shared-query/cutover foundations and `complete-search-filter-parity` for native domain-search journeys. Management links may coexist temporarily; final acceptance requires their tested destinations.

## Capabilities

### New Capabilities

- `native-public-pages`: Public content, statistics, domain discovery and redirects have native route owners.

### Modified Capabilities

None. Existing completed migration contracts remain in force; this change closes the remaining scope rather than reopening their historical acceptance.

## Impact

Django public read views/templates/URLs, shared data reads, content/static images, navbar/footer, both proxies, public fixtures and browser/crawler tests. Audit B03/B07 and content assets in B10.
