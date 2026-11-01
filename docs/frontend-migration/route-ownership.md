# Route ownership and cutover

The production image was changed to native routing on 2026-10-31; it no longer
supports selective Angular route rollback. Standard development Compose also
uses native routing; the switch and fallback descriptions below describe the
still-retained refresh rehearsal and previous-release configuration.
See [production readiness](production-readiness.md#production-image-migration-2026-10-31)
for the current production image and outstanding deployment checks.

Baseline: pinned develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
Runtime work is confined to `develop-migration/`. This is a local cutover rehearsal,
not a deployment to the public registry. Detail, search, editor and request
cutover/rollback verification pass. Native account ownership is additionally
controlled by its own switch; see [account pages](account-pages.md) for policy,
helper URLs and the remaining configured-provider/email gates.

## Ownership matrix

The [2026-10-14 legacy-removal audit](legacy-removal-audit.md) maps remaining
routes, fallback behavior and infrastructure to the proposed
[finishing changes](../../openspec/README.md#finishing-sequence). The matrix below
includes implemented replacements; deletion remains blocked.

| Route family | Owner with switches enabled | Compatibility and rollback |
| --- | --- | --- |
| `/<biotoolsID>` | Django public detail | `BIOTOOLS_CUTOVER_DETAIL=0` restores AngularJS. Reserved literal routes and real static files are excluded. |
| `/tool/<id>`, `/t/<id>`, `/biotools:<id>`, trailing slash/case variants | Temporary redirect to the stored canonical ID | Queries survive; no permanent redirect cache. Same detail switch. |
| `/t`, `/t/` with supported query fields | Django GET results + Vue enhancement | All 61 functional filter keys and domain membership; usable without JavaScript/assets. `BIOTOOLS_CUTOVER_SEARCH=0` restores AngularJS. `/t/` redirects to `/t`. |
| `/_search/data/` | Django search JSON, not the public REST API | Enabled only with the search switch; read-only, validated parameters. |
| `POST /github-to-biotools` | Django authenticated, CSRF-protected suggestion adapter | Reserved before tool IDs and crawler handlers on both proxies, independently of cutover switches. Empty `BIOTOOLS_GITHUB_BRIDGE_URL` returns 503; manual editing remains available. The internal provider has no published port and never writes registry records. |
| `/t` with unknown or invalid parameters | Django validation response | Actionable 400; no automatic AngularJS redirect or silent constraint removal. |
| Detail/search with `_legacy=1` | AngularJS | Explicit per-request escape hatch, also used by the detail management link. |
| `/<id>/edit`, `/register`, `/requests` and their save/request form endpoints | Django + Vue editor / Django request forms when both editor and bridge switches are enabled | `BIOTOOLS_CUTOVER_EDITOR=0` restores AngularJS without rolling back detail/search or sessions. Trailing-slash page variants work; `_legacy=1` retains the legacy editor. |
| `/login`, `/signup/*`, `/reset-password/*`, `/profile/*`, `/auth/*`, `/orcid/callback/` | Django native forms/allauth with `BIOTOOLS_CUTOVER_ACCOUNTS=1` | Independent switch defaults off in normal Compose; `0` restores legacy ownership. Existing email entry formats and `_legacy=1` survive. Live configured ORCID/email remain readiness gates. |
| `/`, `/about`, `/community`, `/communities`, `/domains`, `/stats`, `/404` and schema/documentation shortcuts | Django public pages/redirects with `BIOTOOLS_CUTOVER_PUBLIC=1` | Independent switch defaults off in normal Compose; `0` or `_legacy=1` restores legacy ownership. Literal routes precede tool IDs. See [public-page evidence](public-information-pages.md). |
| `/domain-manager`, `/subdomain`, `/edit-domain[/<id>]`, `/edit-subdomain[/<id>]`, `/workflows`, `/<id>/manage` | Native Django forms/workflow inspection with `BIOTOOLS_CUTOVER_MANAGEMENT=1` | Independent opt-in switch; current ownership/editor policy, CSRF, confirmation and revision checks apply. Existing aliases and `_legacy=1` survive. See [management contracts](record-domain-management.md). |
| `/register/validate/`, `/<id>/edit/validate/` | Existing editor facade, validation only | Same schema, permission, preservation and revision checks as saves; no persistence/index changes. Follows the editor switch and retains preview aliases. |
| `/api`, `/api/*`, including schema, REST auth, allauth and admin | Existing Django API WSGI entry | Never captured by canonical browser routes or crawler prerendering. |
| `/_migration/html/*` | Existing isolated HTML WSGI entry | Preview/auth/editor URLs remain available and noindex. |
| `/_edam/terms/` | Django EDAM lookup | Stable read-only lookup used by canonical search and editor; the `/_migration/html/edam/terms/` alias keeps the same contract. See [readiness helper evidence](production-readiness.md). |
| `/_migration/html/requests/*` | Django session forms | Create editing/ownership requests, received/sent lists and accept/decline, including no-JavaScript forms. |
| `/_migration/html/api/*` | Opt-in session transport for retained Angular pages | `BIOTOOLS_BROWSER_SESSION_BRIDGE=0` disables it; public `/api/*` authentication is unchanged. |
| `/static/*`, `/dist/*`, images/fonts, Angular templates/components and vendor assets | Proxy static serving | Never sent to Rendertron; no legacy asset removal. |
| `/media/*` | Apache media alias / Caddy file serving | Persistent `media_data` volume, read-only Caddy mount and no directory listing. Native workflow images and retained `/api/media/*` remain available. See [management media notes](record-domain-management.md). |
| `/robots.txt`, `/sitemap.xml`, `/favicon.ico` | Existing proxy behavior | Preview Apache still uses its deny-all robots policy; production indexing policy is a separate operator decision. |

## Query and navigation compatibility

Canonical search accepts all 61 functional backend filter keys, domain, `q`,
`sort`, `ord`, `page`, `per_page`, `advanced` and `view`. Repeated keys follow the
public API's last-value behavior. Unknown or invalid input produces an actionable
400. Native GET and enhanced results share the same validated payload; missing
domains cannot broaden the workspace query. See the
[2026-10-22 compatibility matrix and verification](search-filter-parity.md).
Only an explicitly requested `_legacy=1` selects legacy search.

Angular cross-page navigation requests a new document when entering native public
pages, search or tool detail; ordinary filter changes inside legacy search stay in Angular.
The `_legacy` query parameter is retained by the legacy router. This avoids a
direct-link-only cutover where SPA clicks would silently retain the old owner.
Canonical detail and profile use `/<id>/manage` with the management switch enabled;
otherwise management links retain the legacy workflow. Edit and request links use
the migrated owner when the editor switch is enabled. Editor runtime failure now
offers retry, record navigation and stored JSON export without an Angular fallback.
Related-tool and canonical search-result links use canonical detail URLs.

## Proxy and crawler behavior

Apache rewrites only selected browser paths to `canonical_wsgi.py`, with CGI
execution allowed for that file. Caddy selects canonical handlers before its
bot handler, and runserver dispatches to the same root URLconf. The WSGI marker
cannot be supplied by an HTTP header. Canonical pages use root-relative URLs,
not an internal rewrite path or an accidental `/api` mount.

Human and crawler canonical detail, home/about/community/statistics use the same
server-rendered content and `index, follow`; canonical search and the domain
directory use `noindex, follow`. Errors and preview pages remain
noindex. Personalized canonical responses use `private, no-store` and normal
Cookie variation. Retained legacy human and crawler responses vary on User-Agent.

Rendertron is retained and provisioned in both Compose families. Its origin is
operator-controlled, not taken from an untrusted Host header. Production Apache
uses `BIOTOOLS_RENDER_ORIGIN` (default `https://bio.tools`). The local rehearsal
uses its internal Apache hostname; Caddy uses a container-only legacy HTTP origin
on port 8080, with no published host port. This avoids container-localhost and
self-signed-certificate failures. Internal preview origins are not production
canonical URLs. Rendertron must stay reachable for every retained legacy route.
Both proxies encode the complete target URL inside Rendertron's path so page
queries (including `_legacy=1`, repeated fields and escaped values) are not
mistaken for renderer options. Apache uses its native `int:escape` RewriteMap;
Caddy uses native query escaping followed by a path rewrite. No renderer fork
or extra proxy service is needed.

## Activation and rollback

Public pages additionally use the independent `BIOTOOLS_CUTOVER_PUBLIC` switch.
Apply `elixir.0005_statsdata_tooltypecounts` before activation, build assets and
collectstatic, then recreate backend/proxy services. The nullable column supplies
an already-declared develop model field; public route rollback does not require
dropping it. See the [public rehearsal](public-information-pages.md#rehearsal-and-verification).

The editor/request family additionally requires `BIOTOOLS_CUTOVER_EDITOR=1` and
`BIOTOOLS_BROWSER_SESSION_BRIDGE=1` in the backend and proxy. Its readiness
prerequisites (4.1a-4.1d), canonical proxy checks and rollback rehearsal pass.
Normal Compose defaults the editor switch to `0`; the disposable refresh stack
defaults it to `1`. Explicit activation for the local rehearsal is:

```sh
BIOTOOLS_CUTOVER_EDITOR=1 BIOTOOLS_BROWSER_SESSION_BRIDGE=1 docker compose -f compose.refresh.json up -d --no-deps backend apache caddy
```

Use `BIOTOOLS_CUTOVER_EDITOR=0` with the same services to roll back this family.
Disabling the session bridge also disables canonical editor/request ownership;
account ownership is controlled independently by `BIOTOOLS_CUTOVER_ACCOUNTS`.
Retained handlers remain available through `_legacy=1`.
Keep the bridge enabled when rolling back only the editor. Reload pages after
switching; an open editor retains its draft if its save endpoint becomes unavailable.
The no-JavaScript editor link uses `_legacy=1` to avoid returning to the same page.

Normal development/production Compose defaults detail/search switches to `0`. The
disposable `compose.refresh.json` rehearsal defaults them to `1`. Build modern
assets, collect static files and build legacy scripts before changing ownership.
Production must rebuild the Apache image to include the changed config; the
local rehearsal mounts the config directly. Never rebuild assets during tests.

Set both variables explicitly so changing one family does not inadvertently
change the other. For example, roll back detail while retaining search locally:

```sh
BIOTOOLS_CUTOVER_DETAIL=0 BIOTOOLS_CUTOVER_SEARCH=1 docker compose -f compose.refresh.json up -d --no-deps backend apache caddy
```

Use `1/0` for search-only rollback, `0/0` for both, and `1/1` to re-enable both.
For normal development use `compose.yml` and services `backend caddy`; for
production use `compose.prod.yml` and service `backend`. Recreate services rather
than merely restarting: environment switches are read at process startup.
Recheck a canonical path, a crawler request, `/api/env/`, API schema/account
paths and a static asset after each switch. No database rollback is involved.
Canonical search-result links remain `/<id>` even when detail is rolled back;
the detail switch, not a preview link, selects their owner.

Run the browser harness from `tests/browser` with `BIOTOOLS_TEST_CUTOVER=1`.
`cutover.spec.js --grep 'route ownership'` checks either switch combination using
`BIOTOOLS_EXPECT_DETAIL` and `BIOTOOLS_EXPECT_SEARCH` (default `1`, or `0` for
the rolled-back family). Run once against `http://localhost:8003` and again
against `https://localhost:8443` with `BIOTOOLS_TEST_LOCAL_TLS=1`. Full-suite
flags and fixture requirements are in the browser harness README. Existing
search/advanced tests use canonical URLs when the cutover flag is set.

## Observability and remaining gates

`X-Biotools-Route` identifies `django-detail`, `django-search`, `django-editor` or
`django-requests`, `django-accounts` or `django-public`; `Server-Timing`
reports route duration and search duration. Django's `biotools.routes` logger
emits family, method, status and duration without query strings or credentials.
Caddy access logs and Apache access/error logs remain available through Compose.
Compare family-specific 4xx/5xx rates and latency with the pre-cutover baseline;
roll back the affected family if its acceptance checks regress.

Editor/request cutover and rollback are verified with the session bridge enabled.
Canonical login, signup, recovery, profile and ORCID routes now have native
owners behind the independent account switch. Configured ORCID exchange and deployment security review
remain production gates. Legacy removal is prohibited
while the ownership matrix contains any AngularJS route or fallback.

## Verification evidence (2026-10-05)

- Both backend runtimes pass 125 migration tests with Elasticsearch enabled and
  no skips. The cutover tests cover root WSGI URLs, aliases, reserved paths,
  API header isolation and independent switches. A preservation-guard regression
  also verifies tool types compare as an unordered set, matching the serializer.
- Frontend: 82 unit tests, type-check and production build pass. Existing htmx
  eval and backend dependency/MySQL warnings remain; no new dependency is added
  to the application packages and no database migration is required.
- `test-results-cutover-full-apache/` and `test-results-cutover-full-caddy/` each
  record 57 passes and four intentional legacy-discovery skips, with zero retries.
  They include canonical search/advanced history, error recovery, candidate
  promotion, legacy login/logout, preview CSRF/session expiry and editor writes.
- Canonical rich detail without JavaScript passes on desktop/mobile in the Caddy
  full suite and `test-results-cutover-detail-apache/` (three passes). Search and
  detail screenshots retain the blue branding and fit desktop/mobile viewports.
- Canonical advanced-search payload: 7,603 bytes for ten candidates; local
  filtering makes no extra request until promotion. Backend search scenario
  medians were 2.51-6.48 ms, with payloads up to 42,541 bytes. These are local
  fixture measurements, not production load-test or full-registry latency claims.
- Apache and Caddy configuration validation and strict change validation pass.

All artifact directories above are under `tests/browser/` and are ignored by Git.
Do not publish traces containing credentials or session data.

### Completed rollback rehearsal (2026-10-06)

| Detail/search switches | Apache | Caddy |
| --- | --- | --- |
| `1/1` | Full suite passes | Full suite passes |
| `0/1` | Two ownership/isolation checks pass | Two ownership/isolation checks pass |
| `1/0` | Two ownership/isolation checks pass | Two ownership/isolation checks pass |
| `0/0` | Two ownership checks and nine legacy workflows pass | Two ownership checks and nine legacy workflows pass |

Artifacts: `test-results-rollback-{detail,search,both}-{apache,caddy}/` and
`test-results-rollback-legacy-{apache,caddy}/`. Full rollback covers all four
legacy discovery cases skipped in migrated mode, login/logout and protected
registration, and three proxy isolation scenarios. The Apache focused run also
selected six disabled migrated-auth cases; those passed in the full suites.
Canonical search-result links still target `/<id>` during detail-only rollback.
Both switches were restored to `1/1` after the rehearsal.
The final nine canonical cutover/detail checks pass on each proxy, including
desktop/mobile navigation and rich detail without JavaScript. Artifacts:
`test-results-cutover-restored-apache/` and `test-results-cutover-restored-caddy/`.

Two environment issues interrupted earlier attempts, without requiring changes
to routing or data. The user freed disk space, allowing Elasticsearch to clear
its read-only block, and disconnected a Cisco VPN with a competing
`172.17.0.0/16` route. No VPN routes, database volumes or disk safeguards were
changed. Reconnecting that VPN may interrupt the preview again.

Crawler checks allow 20 seconds per request because Rendertron waits up to
10 seconds for legacy third-party requests before serializing. They assert
rendered tool content, HTTP status and owner, not just an Angular shell.
Authenticated proxy suites sharing one account/database must run sequentially:
legacy logout invalidates the shared API token. An overlapping login/logout run
failed; the isolated rerun passed all nine workflows without automatic retries.

### Editor preservation prerequisite (2026-10-06/07)

Replacement saves copy badge/homepage status and clone publication metadata plus
authors without sharing enrichment rows with historical records. Unchanged
publication identities do not trigger another lookup, including those without
metadata. New/changed identities still use the bounded enrichment service; its
argument-count bug and missing citation-count handling are fixed. The editor
clears stale draft enrichment when identifiers change and rejects forged values.
Protected `biotools:` identifiers are read-only, verified against stored values,
and no longer reordered before editor validation. Unknown-field and unexpected
unrelated-data-loss guards remain. No canonical route changes in this prerequisite.

Both backend runtimes pass 130 migration tests with Elasticsearch enabled.
All 83 frontend tests, type-check and production build pass. Backend checks cover
real enrichment persistence with mocked HTTP responses, cloned history, protected
ID error positions, owner/admin saves, forged values and stale/CSRF rejection.

On 2026-10-07, Apache and Caddy each pass all 21 focused editor/authentication
browser checks, with no skips or retries. These include enriched saves, refreshes,
protected controls, session expiry, CSRF and desktop/mobile layout checks.
Artifacts: `test-results-editor-preservation-{apache,caddy}/`. Screenshots were
inspected at 1440px and 390px. The separate fictional `editor-enriched` seed does
not overwrite existing fixtures or call external publication services.
An initial browser run could not launch until the temporary Chromium cache was
restored. A later run was stopped when Elasticsearch was absent; recreating its
container recovered the existing indexes, after which both complete suites passed.

Authenticated readiness (updated after the permission-editor prerequisite):

- Permission controls from `frontend/partials/tool_edit/toolEditPermissions.html`
  and `frontend/js/permissionsController.js` are now implemented: private/public/group,
  username suggestions and group members. The migrated facade allows owners/admins
  to change `editPermission`, rejects changes by group/public editors, and keeps
  CSRF/revision/unrelated-data guards. Shared API validation now rejects malformed
  permission shapes before comparing members instead of raising an internal error.
- Ownership/editing-right requests and accept/decline from
  `frontend/js/requestsController.js`, using `/api/request` and
  `/api/request/conclude` now also have session-backed Django forms. Canonical
  `/requests` remains legacy-owned. Shared handlers reject anonymous reads and
  malformed decisions, lock the current visible resource, reject repeated decisions,
  and update search metadata on grants/transfers. Old resource versions stay unchanged;
  pending requests and profile counts follow current ownership. Editing grants do
  not downgrade an already-public record.
- Session/token interoperability is opt-in through `BIOTOOLS_BROWSER_SESSION_BRIDGE`.
  Retained Angular pages use the isolated session API, preserving the public token
  API and reusing existing account/resource policies. Migrated and retained sign-in
  and logout share one session; no API token is exposed to browser storage.
  See [browser authentication](browser-authentication.md#retained-page-session-bridge)
  for deployment and transport rollback. Live configured ORCID exchange is still pending.

At this prerequisite milestone, tasks 4.2/4.3 remained open. Their subsequent
editor/request verification is recorded below; neither milestone is production approval.

### Permission verification (2026-10-08)

Both Python runtimes pass 136 migration tests with disposable Elasticsearch
coverage. All 87 frontend tests, type-check and production build pass. Backend
checks cover owner/admin edits, group/public-editor denial, immediate revocation,
creation, malformed/nonexistent users, CSRF, stale revisions and unchanged schema
metadata/history. The public API also rejects malformed permission payloads.

Apache and Caddy each pass all 23 focused editor/auth browser checks, with no skips
or retries. New desktop/mobile scenarios exercise username suggestions, invalid
user recovery, membership removal, all three modes, saves and direct refreshes.
Screenshots were inspected at 1440px and 390px without overflow or overlap.
Artifacts: `test-results-editor-permissions-{apache,caddy}/`.

The earlier database/browser connectivity failures cleared after the user
disabled the VPN. No host routes or security controls were changed. The preview
remains at `http://localhost:8003/_migration/html/editor/tool/editor-enriched/`.

### Ownership and session verification (2026-10-11/12)

Both Python runtimes pass all 147 migration backend tests with Elasticsearch
enabled. All 87 frontend tests and type-check pass; the previously verified
modern asset build is unchanged. The retained Angular scripts were rebuilt.
Backend coverage includes request validation, current-owner authorization,
repeated-decision rejection, public-permission preservation, index-failure
database rollback, and a stale API replacement rechecking ownership under a row
lock. This is not a concurrent load test or a claim of distributed DB/index atomicity.

Apache and Caddy each pass all 30 focused ownership, authentication and editor
browser checks, without skips or retries. The tests cover shared login/logout,
expired sessions, stale browser-token removal, token API isolation, new-account
registration, and ownership/editing requests after resource replacement. Request
forms also run without JavaScript. Desktop/mobile request screenshots at 1440px
and 390px were inspected with no overflow or overlap. Artifacts:
`test-results-ownership-session-{apache,caddy}-full/`.

On 2026-10-12, setting `BIOTOOLS_BROWSER_SESSION_BRIDGE=0` passes both legacy
authentication checks on each proxy: protected registration, login/logout,
localStorage token restoration, session-mount 404 and public API cookie rejection.
Restoring it to `1` passes both checks again on each proxy, now requiring no
browser token and a working session mount. Artifacts:
`test-results-session-{rollback,restored}-{apache,caddy}/`. The Apache rollback
invocation also selected six disabled migrated-auth cases; those passed in the
full suites. The preview is left with the bridge and both read-only switches on.

Optional third-party fonts, badges and analytics are blocked by the browser
fixture so their availability cannot gate local application tests. Application
assets, APIs and writes remain real. Browser launch required execution outside
the agent sandbox; no application security controls were disabled.

Tasks 4.1c/4.1d are complete. At this milestone canonical authenticated routing,
its rollback rehearsal and live ORCID exchange remained open. No production route
was changed. Isolated preview: `http://localhost:8003/_migration/html/requests/`.

### Canonical editor and request verification (2026-10-12 to 2026-10-14)

Tasks 4.2/4.3 are complete for `/register`, `/<id>/edit`, `/requests` and their
mutation endpoints. Trailing-slash page variants work without redirecting POSTs.
The canonical namespace reuses the existing views, validation, CSRF, revision
and preservation checks; remaining HTML helpers keep their isolated mount.
Account links still reach `/profile`, and no canonical account/provider handler
was replaced. Anonymous editor access uses the existing migrated sign-in form
with a safe return URL, including its retained ORCID/recovery/signup links.

Both Python runtimes pass 152 migration tests. Apache and Caddy each pass all
40 focused browser checks without skips or retries, covering desktop/mobile
cross-owner navigation, refresh, real create/edit/request mutations, permissions,
session expiry/reconnection, stale edits, draft retention, API isolation and
crawler ownership. Screenshots retain the blue branding without overflow or
overlap. Artifacts: `test-results-canonical-editor-{apache,caddy}/`.
Modern Vue assets are unchanged from the verified 87-test/type-check/build
milestone; retained Angular scripts were rebuilt and both proxy configs validate.

Navigation testing found a retained profile startup race: an unfinished session
check opened a login dialog over an authenticated profile. Initial authentication
is now unknown until the check completes, and the dialog opens only after a
confirmed sign-out. Desktop/mobile navigation and expired-session tests cover it.
Caddy's container-only crawler origin also forwards the isolated session mount,
so retained pages can fetch their data with the bridge enabled.

| Editor / bridge | Apache | Caddy |
| --- | --- | --- |
| `1/1` | 40 focused checks pass | 40 focused checks pass |
| `0/1` | Four ownership/auth checks pass | Four ownership/auth checks pass |
| `1/0` | Four ownership/auth checks pass | Four ownership/auth checks pass |
| Restored `1/1` | Six ownership/auth/navigation checks pass | Six ownership/auth/navigation checks pass |

Artifacts: `test-results-editor-{rollback,bridge-off,restored}-{apache,caddy}/`.
Rollback checks cover browser/crawler ownership, legacy login/logout and protected
registration, browser token storage, session-mount availability, and unchanged
detail/search/API/static behavior. Both rollback cases require recreating backend
and proxy services, including Caddy. No database rollback is needed.

The disposable preview is left with all cutover switches and the bridge enabled:
`http://localhost:8003/register`, `http://localhost:8003/editor-enriched/edit`,
and `http://localhost:8003/requests`. Normal deployment defaults remain off.
Live configured ORCID exchange has not been attempted; retained routes and
fallbacks still prohibit removing the legacy frontend.

### Native account verification (2026-10-15)

`migrate-account-pages` is complete for its local scope. Both runtimes pass
167 migration backend tests, and Apache/Caddy each pass 43 focused browser
checks, five account-only rollback checks and three restored-owner smoke checks.
The old account statements above are historical milestones, superseded by the
current ownership matrix and [account-page contract/evidence](account-pages.md).
Live configured ORCID/email, production approval and legacy retirement remain
separate gates. Next implementation: `add-schema-driven-resource-ui`.
