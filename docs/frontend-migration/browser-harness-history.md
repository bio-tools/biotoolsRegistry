# Frontend browser regressions

Current baseline: upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
See the [develop runbook](../../docs/frontend-migration/develop-refresh.md#run-and-verify)
for isolated services, guarded fixture seeding, proxy URLs and complete test results.
All 16 scenarios passed on both Caddy and Apache, including authentication.
The baseline run at the end of this document is historical `a1fc8b9` evidence.

Discovery, navigation and session-authentication checks for the legacy frontend and its replacements.
Authentication checks use a dedicated account and change disposable sessions, not registry records.
The separately opted-in basic and nested editor tests **do write registry records**; never
enable `BIOTOOLS_TEST_EDITOR_WRITES` outside a disposable deployment.
This is a separate Node package: do not install it in the legacy Node 11 frontend image.
Use Node 22 or newer. No frontend build or AngularJS test hooks are required.

## Install and run

The legacy-free packaged Apache candidate has an additional opt-in smoke suite.
Start it as described in the [removal audit](../../docs/frontend-migration/legacy-removal-audit.md#legacy-free-packaged-rehearsal-2026-10-31),
then run from `tests/browser/`:

```sh
BIOTOOLS_BASE_URL=http://localhost:8005 BIOTOOLS_TEST_NATIVE_PACKAGE=1 npm test -- native-package.spec.js
# Or test through the local Caddy TLS proxy:
BIOTOOLS_BASE_URL=https://localhost:8444 BIOTOOLS_TEST_LOCAL_TLS=1 BIOTOOLS_TEST_NATIVE_PACKAGE=1 npm test -- native-package.spec.js
# Or the Caddy-to-runserver candidate:
BIOTOOLS_BASE_URL=https://localhost:8446 BIOTOOLS_TEST_LOCAL_TLS=1 BIOTOOLS_TEST_NATIVE_PACKAGE=1 npm test -- native-package.spec.js
# For the secure production-image rehearsal, also set the disposable credentials:
BIOTOOLS_BASE_URL=https://localhost:8447 BIOTOOLS_TEST_LOCAL_TLS=1 BIOTOOLS_TEST_NATIVE_PACKAGE=1 BIOTOOLS_TEST_SECURE_COOKIES=1 npm test -- native-package.spec.js
```

The suite expects the disposable refresh database, search index and the
management workflow image fixture. It reads existing data and does not seed it.

From the repository root:

```sh
cd tests/browser
npm ci
npx playwright install --with-deps chromium
npm test
```

The browser installation may require administrator access for operating-system packages.
On an already provisioned machine, `npx playwright install chromium` is enough.

```sh
# A development deployment with a known indexed tool (never seeds or edits data).
BIOTOOLS_BASE_URL=https://your-test-deployment.example BIOTOOLS_TEST_TOOL_ID=signalp npm test

# Focused scenarios, discovery-only execution and test discovery without a server.
npm test -- --grep 'Back/Forward'
npm test -- discovery.spec.js
npm test -- --list

# Isolated Django shell: desktop/mobile with JavaScript disabled.
BIOTOOLS_TEST_HTML_SHELL=1 npm test -- shell.spec.js

# With frontend-modern built: enhanced GET, history, failures and native fallback.
BIOTOOLS_TEST_HTML_SHELL=1 npm test -- shell.spec.js htmx.spec.js

# Vue island lifecycle demo; no registry seed or account needed.
BIOTOOLS_TEST_ISLANDS=1 npm test -- islands.spec.js

# Search workspace, after guarded seed_search.py provisioning.
BIOTOOLS_TEST_SEARCH=1 npm test -- search-workspace.spec.js

# Canonical detail/search ownership, after enabling both cutover switches.
BIOTOOLS_TEST_CUTOVER=1 npm test -- cutover.spec.js
# With this flag, existing search/advanced scenarios exercise /t and /_search/data/.
BIOTOOLS_TEST_CUTOVER=1 BIOTOOLS_TEST_SEARCH=1 npm test -- search-workspace.spec.js advanced-filtering.spec.js

# Migrated sessions, with the dedicated test-account credentials set.
BIOTOOLS_TEST_BROWSER_AUTH=1 npm test -- browser-auth.spec.js

# Disposable registry writes only, after guarded seed_editor.py provisioning.
BIOTOOLS_TEST_EDITOR_WRITES=1 npm test -- resource-editor.spec.js
BIOTOOLS_TEST_EDITOR_WRITES=1 npm test -- resource-editor-nested.spec.js
BIOTOOLS_TEST_EDITOR_WRITES=1 npm test -- resource-editor-metadata.spec.js

# Interactive debugging and the last HTML report.
npm test -- --headed --grep 'text search'
npm run report
```

## Complete search parity

After the existing browser/search fixtures, seed `seed_search_parity.py` once in
the disposable refresh stack with `BIOTOOLS_ALLOW_TEST_SEED=biotools-refresh`.
It creates the separate `search-parity-fixture` domain and refuses overwrite.
`BIOTOOLS_TEST_SEARCH_PARITY=1` enables six desktop/mobile journeys covering
enhanced, JavaScript-disabled and failed-modern-asset search, bookmarks, repeated
EDAM constraints, domain membership, paging, history, comparison and errors.
Set `BIOTOOLS_TEST_SEARCH=1` and `BIOTOOLS_TEST_CUTOVER=1` for the companion suites.
See [search parity evidence](../../docs/frontend-migration/search-filter-parity.md)
for fixture prerequisites and exact Apache/Caddy commands. Never seed production.

## Native public pages

`BIOTOOLS_TEST_PUBLIC=1` enables `public-pages.spec.js` against the disposable
refresh stack with public/account/search/detail switches enabled and the existing
search-parity domain fixture seeded. It covers home/about/community content and
images, domain search/history/links, statistics, metadata, fixed redirects,
missing routes and navigation from retained workflows. Six journeys exercise
1440px/390px with normal, disabled-JavaScript and failed-modern-asset modes.
Use both Apache and Caddy URLs; Caddy needs `BIOTOOLS_TEST_LOCAL_TLS=1`.
See [public-page evidence](../../docs/frontend-migration/public-information-pages.md).

For a public-only rollback, set `BIOTOOLS_EXPECT_PUBLIC=0` and select
`--grep 'route ownership'`; other families must remain native. After restoring
public ownership, `--grep 'public navigation, domains'` can run with the frontend
service stopped to check the retained asset pipeline. Restore that service after
the check; management/workflows and explicit legacy rollback still require it.

## Same-build schema activation rehearsal

Run only against the disposable `compose.refresh.json` stack, with its normal
preview running, modern assets already built/collected and Chromium installed:

```sh
BIOTOOLS_SCHEMA_REHEARSAL=biotools-refresh PLAYWRIGHT_BROWSERS_PATH=/tmp/biotools-playwright npm test -- schema-update.spec.js --output=test-results-schema-transition
```

This scenario temporarily switches the local Apache and Caddy-backed applications
to an isolated `test_schema_ui_<random>` database and search index. Do not run
other browser suites, builds or backend restarts concurrently. It generates and
activates baseline/added/removed schema fixtures, then performs a compatible
rollback, using one unchanged bundle on desktop and mobile through both proxies.
It covers a real persisted optional nested field, labels/help, enum correction,
EDAM label/cache refresh, stale draft conflict/export and public/search metadata.
The optional field uses the existing `Download.cmd` column via test-only
serializer settings; this is not an automatic database migration.

The harness restores normal application settings in `finally`. If forcibly
interrupted, restore from the checkout root with:

```sh
docker compose -f compose.refresh.json up -d --no-deps backend apache
```

Generated fixtures, compose override and evidence remain in the logged
`/tmp/biotools-schema-*` directory; the named test database/index also remain for
inspection. Remove only those exact disposable names when no longer needed.
Normal preview records and its `elixir` search index are not overwritten.
The Playwright output includes desktop/mobile screenshots and JSON evidence
with the unchanged bundle SHA-256 and activated descriptor revisions.

## Target and fixtures

| Variable | Default | Requirement |
| --- | --- | --- |
| `BIOTOOLS_BASE_URL` | `http://localhost:8000` | HTTP(S) origin serving both frontend and `/api`; no path, query or embedded credentials. |
| `BIOTOOLS_TEST_TOOL_ID` | `signalp` | Explicit, stable record in the target database and Elasticsearch index. |
| `BIOTOOLS_TEST_QUERY` | Tool ID | Text query that returns the fixture on page 1, also after tool-type filtering and descending name sorting. |
| `BIOTOOLS_TEST_USERNAME` | Unset | Optional dedicated test account; set together with the password. |
| `BIOTOOLS_TEST_PASSWORD` | Unset | Optional test-account password; use environment/CI secrets, not committed files. |
| `BIOTOOLS_TEST_HTML_SHELL` | Unset | Set to `1` only on a target deploying `add-django-html-shell`; enables checks at `/_migration/html/`. |
| `BIOTOOLS_TEST_LOCAL_TLS` | Unset | Set to `1` only for a local self-signed test certificate. |
| `BIOTOOLS_TEST_NATIVE_PACKAGE` | Unset | Set to `1` for the isolated legacy-free production or development rehearsals. |
| `BIOTOOLS_TEST_SECURE_COOKIES` | Unset | Set to `1` with disposable account credentials on an HTTPS target configured for secure cookies. |
| `BIOTOOLS_TEST_DETAIL` | Unset | Set to `1` after the guarded `seed_detail.py` has created `detail-demo`; enables three migrated detail checks. |
| `BIOTOOLS_TEST_ISLANDS` | Unset | Set to `1` with the Vue runtime built; enables four lifecycle/demo checks at `/_migration/html/islands/`. |
| `BIOTOOLS_TEST_SEARCH` | Unset | Set to `1` after guarded `seed_search.py` provisioning; enables search/history/race, advanced candidate/promotion and legacy characterization checks. |
| `BIOTOOLS_TEST_CUTOVER` | Unset | Set to `1` to enable six canonical-route checks, use canonical URLs in search/advanced tests, and replace four legacy-only discovery checks. |
| `BIOTOOLS_EXPECT_DETAIL`, `BIOTOOLS_EXPECT_SEARCH` | `1` | With cutover checks enabled, set each to `0` when verifying that family's rollback. Must match the deployment switches; these variables do not change routing. |
| `BIOTOOLS_TEST_EDAM` | Unset | Set to `1` with the selector deployed and EDAM ontology records provisioned; enables five selector/form scenarios. |
| `BIOTOOLS_TEST_BROWSER_AUTH` | Unset | Set to `1` with migrated browser authentication deployed and both test-account credentials set; enables six session/CSRF/recovery scenarios. |
| `BIOTOOLS_TEST_EDITOR_WRITES` | Unset | Explicitly opt into fifteen real basic/nested/metadata/permission editor-write scenarios on a disposable target with `seed_editor.py` provisioned and both credentials set. Never enable on production. |
| `BIOTOOLS_TEST_ENRICHED_EDITOR` | Unset | Set to `1` when running `seed_editor.py` to create the separate `editor-enriched` fixture without overwriting `editor-demo`. Set alongside editor-write opt-in during tests to check enriched saves at desktop/mobile sizes. |
| `BIOTOOLS_TEST_SESSION_BRIDGE` | Unset | Set to `1` with the server's `BIOTOOLS_BROWSER_SESSION_BRIDGE=1`, canonical search enabled, both credentials and editor-write opt-in. Adds five ownership/session checks; creates disposable users, records and requests. Never run on production. |
| `BIOTOOLS_EXPECT_SESSION_BRIDGE` | Unset | Set to `0` or `1` during `auth.spec.js` to verify the deployed transport switch, token storage, session-mount availability and public API isolation. |
| `BIOTOOLS_TEST_CANONICAL_EDITOR` | Unset | Set to `1` with editor and bridge switches enabled to run editor/ownership suites at canonical URLs and add four route/navigation checks. Retained auth tests explicitly use `_legacy=1`. |
| `BIOTOOLS_TEST_ACCOUNTS` | Unset | Set to `1` for native account routing, signup, profile, recovery and desktop/mobile no-JavaScript checks. Set alongside editor-write opt-in for disposable account/email/password mutations. |
| `BIOTOOLS_EXPECT_ACCOUNTS` | `1` | Set to `0` only during account rollback; run `account-pages.spec.js --grep 'route ownership'` plus retained `auth.spec.js`. |
| `BIOTOOLS_EXPECT_EDITOR` | `1` | Set to `0` with the editor switch disabled for `canonical-editor.spec.js --grep 'route ownership'`; verifies rollback without changing detail/search ownership. |
| `PLAYWRIGHT_BROWSERS_PATH` | Playwright default | Optional browser cache override; use the same value when installing and running. |

Choose a controlled fixture with a nonempty name, homepage and at least one tool type.
The fixture helper reads its metadata via `GET /api/t/<id>?format=json` and fails with
setup guidance if the record/API is missing. It does not choose a random search result,
create data, bypass login or inspect framework state. Its ID/query must identify a
unique visible tool name on the first page. `signalp` is an example, not a bundled seed.
Public mutable deployments are useful for manual smoke checks, not a reproducible CI baseline.

For current local setup, follow [INSTALL.md](../../INSTALL.md) and [compose.yml](../../compose.yml).
MySQL, Elasticsearch, built modern assets and the backend/proxy are required.
The isolated refresh rehearsal retains the legacy assets for rollback checks;
legacy-only assertions should run there rather than against standard Compose.
Apply migrations and seed/index the guarded disposable fixture before running.

The repository includes `initial_db.sql` and `load_initial_db.sh`, but the old seed
and the documented example account are not prerequisites for the guarded migration
fixtures. Do not load the seed or run database-purging setup scripts on shared targets.

## Coverage

The [public tool detail prototype](../../docs/frontend-migration/public-tool-detail.md)
adds rich/sparse deep links, keyboard abstracts, outbound links, mobile layout,
legacy parity and bot/API isolation checks. With both HTML/detail flags and account
credentials, those changes provide 19 tests. Enabling `BIOTOOLS_TEST_ISLANDS=1`
adds four [Vue runtime checks](../../docs/frontend-migration/vue-island-runtime.md),
bringing the complete suite to 23 tests. These focused tests observe Vue teardown
hooks to verify cleanup, without exposing production diagnostic state.
The [search workspace](../../docs/frontend-migration/search-workspace.md) adds five
tests, bringing the complete opted-in suite to 28. Legacy navigation waits for
DOMContentLoaded plus the existing UI assertions, not unrelated badge/font loads.
The [advanced filtering change](../../docs/frontend-migration/advanced-search-filtering.md)
adds three scenarios using the same search flag and samples, bringing the total
to 31. They cover local scope/counts, zero local fetches, full-set promotion,
URL refresh/history, Boolean/date/category/ontology conditions and desktop/mobile
screenshots with payload/heap measurements.
The [EDAM selector](../../docs/frontend-migration/edam-selector.md) adds five
scenarios, bringing the complete suite to 36. They cover keyboard selection and
removal, cancel/apply, validation rerenders, all concept scopes and payload
shapes, lookup errors/races, unique ARIA IDs, and native no-JavaScript submission.
Search's advanced topic test now uses the selector instead of manual URI entry.
The [browser authentication change](../../docs/frontend-migration/browser-authentication.md)
adds six scenarios, bringing the complete suite to 42. They cover desktop/mobile
login and logout, Vue/htmx session expiry, retained unsaved input, second-tab login,
explicit reconnection, missing/stale CSRF, browser storage, native no-JavaScript
forms and recovery/API route ownership. Live ORCID exchanges require configured
provider credentials and are not part of these deterministic checks.
The [basic editor](../../docs/frontend-migration/resource-editor-basic.md) adds
seven scenarios, bringing the complete opted-in suite to 49. Tests create unique
`editor-browser-*` records and edit/restore `editor-demo`, retaining version history.
They cover authoritative validation, successful create/edit, hidden metadata,
navigation warnings, expiry/reconnection, stale tabs, draft export, failed saves
and the no-JavaScript legacy fallback. They do not delete arbitrary target data.
The [nested editor](../../docs/frontend-migration/resource-editor-nested.md) adds
four scenarios, bringing the complete suite to 53. Tests create unique
`nested-browser-*` records, choose real scoped EDAM concepts, move functions and
inputs/outputs by keyboard, confirm populated removals, recover from real nested
validation errors, and edit/restore the rich fixture without unrelated loss.
The metadata editor adds two scenarios (55 total). The
[route cutover](../../docs/frontend-migration/route-ownership.md) adds six more
(61 total): browser/crawler ownership and API/schema/account/static isolation,
aliases/404s, legacy query preservation, and desktop/mobile cross-owner navigation.
With cutover enabled, four legacy-only discovery cases are replaced by the new
canonical workflows; run them again with both deployment switches disabled and
`BIOTOOLS_TEST_CUTOVER` unset. To check independent rollback, run `cutover.spec.js
--grep 'route ownership'` with the matching `BIOTOOLS_EXPECT_*` values on each proxy.

For the editor/request cutover, set `BIOTOOLS_TEST_CANONICAL_EDITOR=1` alongside
the existing authentication, session-bridge, editor-write and enriched-editor
flags. Run `canonical-editor.spec.js`, `ownership-session.spec.js` and all three
`resource-editor*.spec.js` files. They reuse the same mutations, preservation and
expiry checks at `/register`, `/<id>/edit` and `/requests`. Roll back only
`BIOTOOLS_CUTOVER_EDITOR`, recreate backend/proxy services, and run the two
`canonical-editor.spec.js --grep 'route ownership'` cases with
`BIOTOOLS_EXPECT_EDITOR=0`. Restore the switch and repeat with `1`. The public
account/provider routes remain legacy-owned; live ORCID exchange is not simulated
by these checks.

- Home renders, Explore > Tools opens search, typed text updates the URL/results, and a result opens its detail.
- Tool-type filtering updates URL and visible results.
- A separate filtered-URL scenario verifies name sorting, selected sort control, Back, Forward and refresh, even if autocomplete is broken.
- A tool detail deep link works in a fresh browser context.
- Anonymous registration access redirects to login.
- With explicit credentials: login, authenticated registration access, logout and renewed access denial. Nothing is saved.
- With the isolated Django mount enabled: desktop/mobile complete-page rendering, static assets, CSRF form submission and refresh with JavaScript disabled. See [shell setup](../../docs/frontend-migration/django-html-shell.md).
- With modern assets built: fragment swaps, Back/Forward, loading/errors/retry, and complete-page GET fallback when JavaScript is disabled or unavailable. See [htmx setup](../../docs/frontend-migration/htmx-progressive-enhancement.md).

Every test has a fresh browser context; there are no arbitrary sleeps or automatic retries.
The page fixture blocks only optional third-party Google Fonts, legacy badge and
analytics hosts. These can stall Angular startup; application assets, APIs and
mutations are not mocked. Provider exchanges remain separate manual checks.
Run authenticated proxy suites sequentially when they share an account/database:
legacy logout invalidates the account's shared API token, and editor tests share
the rich fixture. Read-only route-ownership checks do not have this constraint.
Crawler cutover requests allow 20 seconds because Rendertron's own rendering
deadline is 10 seconds; the grouped crawler test allows 90 seconds for up to four
such renders. HTTP status, rendered content and ownership assertions still apply.
Authentication is explicitly skipped when credentials are absent. Provision a dedicated
account with permission to register a tool to enable it. Supplying only one credential is a configuration error.

## Failures and CI

Failures retain screenshots, traces and a `browser-diagnostics` JSON attachment containing
console warnings/errors, uncaught errors, failed requests and HTTP error responses.
See `test-results/` and `playwright-report/`; open a trace with
`npx playwright show-trace test-results/<scenario>/trace.zip`.
These directories are ignored. Traces can include login request bodies and private data:
restrict artifact access/retention and never commit or publish them without review.
Console/network errors are recorded, not blanket-asserted away, so unrelated legacy
third-party failures do not obscure the failing user-visible assertion.
See the [Playwright artifact options](https://playwright.dev/docs/test-use-options)
and [trace viewer](https://playwright.dev/docs/trace-viewer).

Develop has [API CI](../../.github/workflows/test-api.yml), but no browser CI job.
The guarded `seed.py` supplies the disposable browser fixture; CI still needs a reachable test deployment
(or provisioned MySQL/Elasticsearch/backend), seeded and indexed fixture, Node 22+,
Chromium system dependencies, and optional account secrets. Once supplied, run the
installation commands above followed by `CI=1 npm test`, and retain both artifact
directories on failure with access restricted. Do not point an authenticated CI job at production.

## Baseline run

Validated on 2026-09-09 with Node 22.23.2, Playwright 1.63.0 and Chromium 153.0.8010.12.
The frontend baseline was checkout `a1fc8b94067f33bc9047efc9c75ebe1579365a07`, including
its checked-in bundles, with no application changes or rebuilds.

- `npm ci --offline --cache /tmp/biotools-npm-cache`: passed after the initial dependency download; lockfile is reproducible.
- `npm test -- --list`: six scenarios discovered. Invalid target URLs and partial credential configuration were also checked and rejected.
- Default localhost execution: four setup/connection failures and one authentication skip in the initial five-scenario suite; no stack was running on port 8000. Fixture errors named the missing target/record. Screenshots, traces and console/network attachments were verified.
- Direct `https://bio.tools` smoke check: observed HTTP 500 from `/api/used-terms/all`, preventing the Tool type menu from appearing. The failure remains an ordinary failing assertion, not a skip or an expected failure. Anonymous profile HTTP 401 responses are expected.
- Checked-in frontend execution: a temporary loopback server served `frontend/` unchanged, supplied the normal SPA fallback, and forwarded only public API GET requests to `https://bio.tools`. Five unauthenticated scenarios passed; authentication was skipped. The final suite with explicit sort-selection assertions was repeated twice (`--repeat-each=2`): **10 passed, 2 skipped, zero retries** in 28.1 seconds. The deployed autocomplete failure did not recur in these runs. The temporary server was stopped afterward and is not part of the harness.
- `openspec validate add-frontend-regression-harness --strict`: passed.

This verifies the checked-in frontend against real public API data, not a provisioned
local backend or an immutable dataset. A fully local/CI baseline still needs the services,
maintained seed and optional test account described above. `https://dev.bio.tools` timed
out during target discovery; no dedicated account was available or used. No resources
were created, edited or deleted, and no product behavior was changed to make tests pass.

## Native management acceptance (2026-10-28)

`management.spec.js` requires `BIOTOOLS_TEST_MANAGEMENT=1`,
`BIOTOOLS_TEST_EDITOR_WRITES=1`, native account/editor switches, the existing
`editor-demo` fixture, and the guarded `seed_management.py` fixture. Run only in
the disposable refresh stack. It creates unique records/domains, disowns its own
records and removes only a record created by its isolated test administrator.
The workflow seed does not overwrite existing records. Ports 8003 (Apache) and
8443 (Caddy, with `BIOTOOLS_TEST_LOCAL_TLS=1`) exercise the same checks.

Set `BIOTOOLS_EXPECT_MANAGEMENT=0` only for rollback navigation checks. Ordinary
workflow navigation is native with management enabled; explicit `_legacy=1`
requests deliberately retain legacy behavior. See
[management evidence](../../docs/frontend-migration/record-domain-management.md).
