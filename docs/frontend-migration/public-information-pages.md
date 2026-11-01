# Native public information pages

Implementation baseline: upstream develop
`9faec5b3b660498fdef9736e65e331728b55f99c`, with the existing migration changes
in `develop-migration/`. Review date: 2026-10-23. Runtime changes are confined
to that checkout; this evidence is mirrored to the outer planning tree.

## Content and route inventory

| Route | Develop source | Native disposition |
| --- | --- | --- |
| `/` | `frontend/components/home/home.html`, `homeSearch.html`, `homeController.js` | Registry introduction, search, community/domain links, ELIXIR support and 16 partner logos. Native GET search opens `/t`; its full filter workspace replaces the home tag/autocomplete widget. |
| `/about` | `frontend/components/about/about.html` | Twelve explanatory sections, publications/citations, funding and 23 node flags. Existing copy, links and attribution retained. |
| `/community`, `/communities` | `frontend/components/community/community.html` | Both aliases show 3D-BioInfo, Biodiversity, hCNV, IDP/condensates, Proteomics, Rare Diseases and Systems Biology communities with existing domain links. Canonical URL is `/communities`. |
| `/domains` | `frontend/partials/subdomains/domains.html`, `frontend/js/subdomainController.js`, `/api/d/all` source | Public directory, tool counts, title/subtitle, collection links, tags and field-selectable search. Domain management remains a separate retained route. |
| `/stats` | `frontend/components/stats/{stats_page.html,stats_controller.js}`, `backend/elixir/stats.py` | Four existing datasets, accessible values and native bar summaries. No Chart.js/Angular dependency. |
| `/schema` and nine documentation shortcuts | `frontend/js/app.js`, `frontend/partials/schema.html` | Fixed server-side 302 redirects; see destination review below. |
| `/404`, unknown public paths and missing tool IDs | Angular 404 state / native detail handler | Genuine native 404 responses; no successful SPA bootstrap for missing pages. |

Home/about/community copy was ported from the pinned develop templates, including
existing terminology and citations, rather than rewritten. Angular attributes,
Bootstrap layout dependencies and inline layout rules were removed. Internal
registry links now use canonical paths; external links retain their destinations.
Blue `#005472` branding and the shared header/footer remain.

Literal public routes precede generic tool IDs. API, static, media, preview,
account/editor and retained management/workflow namespaces stay separate.
Canonical home/about/community/statistics pages return `index, follow`; the
searchable directory, errors and isolated previews return `noindex, follow`.
Query strings do not alter the canonical URL. This defines application metadata,
not production indexing approval; the preview Apache robots file still denies
crawling. Page failures return 503 and noindex rather than indexable zero counts.

## Data semantics

The domain directory uses the existing Elasticsearch domain index through
`queries.public_domains()`, projecting only domain, title, subtitle, description,
tags, collections and resource names/IDs. Owner/editor fields are not fetched.
As in the existing public directory API, domain edit privacy is not read privacy.
An incomplete/timed-out/shard-failed directory returns 503. The existing 10,000
entry bound is explicit: exceeding it returns unavailable, never a truncated
list labelled complete. Pagination is a future scaling need, not added here.

Domain name always participates in search. Visitors can select title, subtitle,
collection, tags, description and tools; the initial selection matches develop.
Native search is case-insensitive, requiring all query words in the selected
values. The old Fuse fuzzy ranking is not reproduced. Query and selected fields
survive GET submission, refresh and browser history. Domain/collection links use
encoded query values and the migrated search service.

Statistics reuse `StatsInfo.statsData(10, now)`, `totalEntriesForLast(24)`,
`userGrowthByMonth()` and `totalAnnotationsCountForLast(24)` independently.
They retain total entries/users, EDAM counts, all 17 annotation measures and
their total, top topics/functions/data/formats/contributor domains, tool types,
monthly content/EDAM growth, user growth and annotation history. Native meters,
readable counts and a table replace the old chart widgets; details controls work
without JavaScript. Empty history is labelled empty; a failed dataset is marked
unavailable while successful sections remain visible, with overall status 503.
No fake historical points or zero substitutions are generated.

Live verification uncovered a missing upstream migration for the already-declared
nullable `StatsData.toolTypeCounts` JSON field. Migration
`elixir.0005_statsdata_tooltypecounts` adds that column without rewriting history;
it was applied only to the disposable rehearsal database. Deployment must apply
normal Django migrations before activation. Rollback of route ownership does not
require dropping this backward-compatible column. Existing StatsInfo monthly
sampling/count policies are reused; this is not a historical analytics redesign.

## Redirect destination review

All shortcut targets are fixed in `elixirapp/public_pages.py`. Visitor query data
is never forwarded, and existing destination fragments are preserved. These are
302 responses so an external site's later change does not create a permanent
browser redirect cache.

Direct HTTP checks on 2026-10-23 (following redirects, 15-second limit) found:

| Shortcut | Existing destination | Observed result |
| --- | --- | --- |
| `/schema` | `https://github.com/bio-tools/biotoolsSchema` | 200 |
| `/governance` | `https://biotools.readthedocs.io/en/latest/governance.html` | 200; changed only HTTP to HTTPS |
| `/changelog` | Google document `1C5KFu2t4OIAuUpx6dS7Djsa9y3zgicd8naOsAs9QPAY` | 200 |
| `/roadmap` | Google document `17iH72hmwVo205QVEkptv7GTMlqFojatIwMmxVOyuPy8` | 200 |
| `/events` | Google document `1K-6IG_7a-4amstSSOxYjjJ3uDUEg4-WGSSt9jvvO7Ik` | 410 |
| `/faq` | Google document `1WdcY0WQJVdRHz0BAhII7s8gygxKRJaHZC4gOnAC1eqs` | 410 |
| `/apidoc` | Google document `1c1zridWLBNSrWcYyR2fnBfgjWfrUSrT7HJ6Ql6ZCkS4` | 410 |
| `/projects` | Google document `1QBIZHBzHxxmvSnOG3xK6t3SCeft5g4AH2rVICLRLmDw` | 410 |
| `/helpdesk` | `https://elixir-registry.atlassian.net/servicedesk/customer/portal/2/user/login?destination=portal%2F2` | 404 |
| `/mail` | `http://elixirmail.cbs.dtu.dk/mailman/listinfo` | DNS resolution failed, including retry outside the sandbox |

These observations do not establish permanent availability or unavailability.
The existing failing destinations are retained, not silently replaced with
unrelated pages or deleted. Content owners must choose replacements before
production readiness closes its external-link review. No page handler fetches
external sites or turns their failure into invented local content.

## Asset disposition (B10)

Forty images were copied byte-for-byte from `frontend/img/` to
`backend/elixir/static/public/img/`, keeping relative names:

- Home: `ELIXIR_logo_white_background.png`; `logos/` contains `dtu.png`, `ku.png`,
  `aarhus-uni.jpg`, `aalborg-uni.png`, `sdu2.png`, `institut-pasteur.png`,
  `bergen.jpg`, `bsc.jpg`, `ceitec.jpg`, `tartu.png`, `embl.png`, `sib.png`,
  `irb.jpeg`, `inesc.png`, `cnrs.png`
  and `OIP.jpeg`.
- About: `countries/` contains SVG flags for be, cz, dk, ee, fi, fr, de, gr, hu,
  ie, il, it, lu, nl, no, si, pt, es, se, ch, gb and cy, plus `embl.png`.

Templates use Django static URLs under `/static/public/img/`; collectstatic and
the retained static pipeline serve them on both proxies. Existing source links,
alt text and adjacent attribution are retained; no new licensing assertion is
made about partner marks. The already-retained header logo remains unchanged.
Original images and old URLs remain available for rollback. Schema/reference
resources, EDAM sources, API/admin assets, workflow media, Angular/vendor assets
and legacy builds are not deleted. This resolves only the public-content part of
B10; its remaining classification/removal gates remain open.

## Rehearsal and verification

`BIOTOOLS_CUTOVER_PUBLIC` controls public ownership independently of the other
families. It defaults to `1` only in `compose.refresh.json`, and `0` in normal
development/production Compose. Canonical URLs are `http://localhost:8003/`
and `https://localhost:8443/`. Isolated preview:
`/_migration/html/public/about` (noindex). `_legacy=1` retains explicit rollback.

After applying migrations, building existing assets and collecting static files:

```sh
BIOTOOLS_CUTOVER_PUBLIC=0 docker compose -f compose.refresh.json up -d --no-deps backend apache caddy
# Restore native public ownership:
BIOTOOLS_CUTOVER_PUBLIC=1 docker compose -f compose.refresh.json up -d --no-deps backend apache caddy
```

Production Apache requires a rebuilt image for the proxy configuration. The
rehearsal mounts it. Do not rebuild or recreate services during browser checks.
No production activation, legacy deletion or production-scale benchmark is part
of this change.

## Acceptance evidence: 2026-10-24

- 59 focused backend checks passed on each runtime (Python 3.13 backend and
  Python 3.10 Apache): public pages, cutover, accounts, HTML shell and htmx.
  These include real StatsInfo database reads, fixed redirects, reserved paths,
  encoded domain/collection links, invalid/empty/unavailable states and all 40
  image comparisons. MySQL conditional-constraint and legacy naive-date warnings
  remain; neither is a new failure.
- 100 modern unit tests, type checking and production asset build passed.
  Deployed JS remains `main-DidFc-OB.js`, CSS `main-BxxHbfie.css`; public styling
  is in the retained `html/shell.css`. The existing htmx eval warning remains.
- 28 distinct public/search/cutover browser journeys passed on each proxy
  (27 in the Apache combined run plus the added retained-navigation check;
  28 in the Caddy combined run). Five affected account/navigation checks also
  passed per proxy, including signed-in desktop/mobile with and without JS.
  Corrected test selectors were rerun successfully; no runtime workaround was
  introduced for those test failures.
- Public-only switch rollback passed on both proxies for ordinary browsers and
  Googlebot, with search/detail/accounts still native. Native ownership was
  restored afterwards.
- With the frontend build service stopped, seven public route/content/image
  journeys passed on each proxy, including 1440px/390px normal, no-JavaScript and
  failed-modern-asset modes. A Caddy run first hit connection timeouts and
  `ERR_NETWORK_CHANGED`; after checking endpoint health, the unchanged suite
  passed. The frontend service was restored afterwards. This verifies service
  independence, not deletion of the legacy tree: collected static output still
  lives under `frontend/static`, whose relocation remains B10 retirement work.
- Inspected home/about/community/domain/statistics desktop/mobile screenshots;
  blue branding, content and images remain, with no document overflow in those
  views. This is focused visual inspection, not the later full accessibility and
  design acceptance change.
- Descriptor drift check passed at revision
  `6ab2490fa587b187de771a4c4cdc89da6407c83b5c31413de6de967b58b1a535`.
  `makemigrations elixir --check --dry-run` reports no model drift after migration
  0005. Strict OpenSpec validation and whitespace checks passed.

Browser artifacts are under `tests/browser/test-results-public-pages-*`,
`test-results-public-navigation-*`, `test-results-public-legacy-navigation-*`,
`test-results-public-rollback-*` and `test-results-public-retained-assets-*`.
Earlier failed runs remain identified above; final focused reruns establish
acceptance. Backend public checks are `elixirapp.test_public_pages`.

Reproduce the combined browser run from `tests/browser`:

```sh
BIOTOOLS_BASE_URL=http://localhost:8003 BIOTOOLS_TEST_PUBLIC=1 BIOTOOLS_TEST_SEARCH_PARITY=1 BIOTOOLS_TEST_SEARCH=1 BIOTOOLS_TEST_CUTOVER=1 BIOTOOLS_TEST_DETAIL=1 BIOTOOLS_TEST_TOOL_ID=migration-fixture BIOTOOLS_TEST_QUERY=Migration PLAYWRIGHT_BROWSERS_PATH=/tmp/biotools-playwright npm test -- public-pages.spec.js search-parity.spec.js search-workspace.spec.js advanced-filtering.spec.js cutover.spec.js --output=test-results-public-pages-apache
```

Use `https://localhost:8443`, `BIOTOOLS_TEST_LOCAL_TLS=1` and a separate Caddy
output directory for the other proxy. Fixture setup is documented in the browser
README. The next finishing change is `migrate-record-and-domain-management`.
Production traffic, live providers/email, load testing and a cleaned legacy-free
artifact were not revalidated here; their existing readiness gates stay open.

## Publication presentation correction: 2026-10-25

About citations now use separate semantic list entries with a clear title,
authors/year, journal and DOI, replacing manual indentation and line breaks.
The same retained citation styling is used for tool publications. Tool records
keep identifiers, full authors, types, notes, abstract disclosure and descriptor
extensions; unenriched publications have a readable heading and retain their
identifier link. No record or enrichment metadata was changed by this correction.

Added the Mendes et al. (2026) bio.tools citation exactly as identified in the
reviewed upstream dev source; all four earlier references remain. The
[upstream review](upstream-dev-review.md) records the SHA and the separate open
integration proposal, which now precedes management in the finishing sequence.

Verification: 17 focused publication/public-page backend tests passed on each
Python runtime. Eight browser journeys passed on each proxy, covering tool detail
and About on desktop/mobile, no-JavaScript and failed-modern-asset public pages.
Publication screenshots were inspected at both widths. Artifacts:
`tests/browser/test-results-publications-{apache,caddy}/`.
Only templates/retained CSS changed; the modern bundle and schema descriptor did
not change. No full production/provider or load test was repeated for this fix.
