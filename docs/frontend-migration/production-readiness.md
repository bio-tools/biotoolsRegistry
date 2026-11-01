# Production readiness work in progress

This is local evidence, not production approval. The user accepted the migrated
interface and workflow designer on 2026-10-31 and authorized removal of the old
source on 2026-11-01 before completing the outstanding checks separately. The
legacy-free release gate and deployment remain incomplete. Earlier dated sections
below describe the state and rollback options at the time of each rehearsal.

## Production image migration: 2026-10-31

The root Dockerfile's `prod` target now builds the Django/htmx/Vue application,
serves it with Apache, and retains historical schema resources and collected
static files. It does not package the Angular application or build with Bower
or Gulp. `compose.prod.yml` uses that image for both backend and taskrunner,
removes the unused Rendertron service, and no longer accepts individual legacy
route cutover switches. The previous production image and its matching Compose
configuration must be retained for rollback; the removed switches cannot restore
Angular in the new image.

Production Compose now requires the existing MySQL application and root passwords,
the Django secret key, allowed hosts as a JSON array, and an explicit email
backend. Debug defaults off and session and CSRF cookies default to secure.
Configure the actual public origin, SMTP and ORCID credentials, CSRF trusted
origins and TLS/proxy settings through the deployment's secret and configuration
mechanism. Trust forwarding headers only when direct access is restricted and the
trusted proxy strips client-supplied headers. Changing MySQL environment variables
does not change passwords in an already initialized database.

The Apache image still serves a deny-all `robots.txt`, matching the previously
documented production image configuration. The intended live indexing policy and
`/api/sitemap.xml` must be reviewed for the actual origin. Compose still publishes
MySQL and Elasticsearch ports and Elasticsearch authentication is disabled; the
deployment's network controls must be verified. Take verified database and media
backups, identify the prior deployable artifact and configuration, and verify
migrations, providers, search/index health and rollback before activation.

The local `prod` image was built and its npm runtime dependency audit reported no
vulnerabilities after updating `source-map-js`. Vite and Vitest were updated to
patched versions; the full npm audit still reports five moderate advisories in
test-only dependencies. These results do not establish the actual production host,
configuration, data, provider credentials or readiness; no live deployment has
been performed.

The reviewed image is
`sha256:09598aae6ff818ac7dd7aa0f36cc306bab205e4aa5de08fcdafb11a23589045a`.
On the isolated refresh database and index, it passed Apache configuration and
Django checks, 79 backend tests (one expected legacy-router skip), and 12 browser
checks through HTTPS with secure session/CSRF cookies. These included public and
API routes, sitemap, historical schemas, media, no-JavaScript search, workflow
design/matching/sharing, and asset failure recovery. The local email backend was
console-only; ORCID, SMTP, production-origin policies and real data were not
tested. Modern type checking, 118 unit tests and production build also passed.
The disposable secure rehearsal can be started alongside the refresh stack with:

```sh
docker build --target prod -t biotools-refresh/production:review .
docker compose -f compose.refresh.json -f compose.native-rehearsal.yml up -d --no-deps production-secure production-secure-caddy
```

It listens at `https://localhost:8447/` with a local certificate, shares the
disposable refresh database and index, and mounts media read-only. Never use the
test credentials or console email backend on production.

On 2026-10-31 the user confirmed that no authorized ORCID/email test environment
is available. Configured live provider and email checks remain incomplete; the
console backend and deterministic provider tests do not substitute for them.

After the actual deployment's prerequisites are verified and its existing image,
configuration, database and media backups are retained, the operator can build the
image and apply the versioned migrations before starting the new application:

```sh
docker compose -f compose.prod.yml build backend
docker compose -f compose.prod.yml run --rm --no-deps backend python manage.py migrate --noinput
docker compose -f compose.prod.yml up -d --no-deps backend taskrunner
```

These commands assume the existing database and index are running and the required
production settings are supplied. They have not been run on the live deployment.
Rollback after the image change requires the previous image and its matching Compose
configuration; database and descriptor compatibility must be rehearsed separately.

## Disposable backup and prior-image rehearsal, 2026-10-31

`compose.backup-rehearsal.yml` started a separate MySQL 8.0.43 with no host port
and `/var/lib/mysql` on tmpfs. The normal preview's database, index and media
volumes were not used for this rehearsal. The current backend applied all
migrations through `elixir.0007_workflow_design` to its `backup_source` database.
The guarded `backend/elixirapp/tests/backup_restore_fixture.py` seeded a dummy
owner, resource with nested EDAM annotations, domain and editor, domain-name lock,
and private workflow draft with revision and share digest.

`mysqldump --single-transaction --no-tablespaces --set-gtid-purged=OFF` produced
a dump inside the scratch container, which was restored into a separate
`backup_restored` database. The current application verified the restored nested
annotations, permissions, domain lock, workflow graph, revision and digest. A
dummy media file was archived with `tar`, restored separately and matched by
SHA-256 (`85470a1743372c000e191fad62f8f4b4e3a0c4e9695258763528d6c8fbf91d47`).

The locally retained prior image `biotools-refresh/upstream:review` (image ID
`e9be6fb9fad2`) then started against the restored database with an unavailable
test index. Its Angular home and `/api/env/` returned successfully, and its ORM
read the restored resource and domain/editor data. The current backend could
still read the workflow draft afterward. The scratch services were stopped after
verification; their tmpfs data was disposable. No existing volumes were purged.
This does not prove that the local prior image is the actual deployed release,
that an Elasticsearch backup exists, or that a real production backup can be
restored. Production operators must verify those independently.

For a real rollout, retain the tested current and prior image IDs and matching
configuration, back up the actual database and media, and record index recovery
and migration compatibility. Observe the `biotools.routes` route/method/status/
duration logs, application errors, authentication and index health; smoke-test
home, search, detail, login, editor, API, admin, static assets and media from the
public origin. Roll back on sustained errors, lost authentication, failed writes,
missing assets or incorrect data after pausing writes and preserving evidence.
No production observability service or rollback thresholds are assumed here.

The earlier selective-route rollback checks passed through both Apache and Caddy;
the [route record](route-ownership.md#completed-rollback-rehearsal-2026-10-06)
and [schema activation record](schema-driven-ui.md#same-build-activation-and-rollback-2026-10-21)
describe their scope and data-preservation limits. The new production image has
no Angular switch: its rollback uses a retained prior image and configuration,
as in the disposable restore above. Restoring the actual deployment still requires
its own artifact, database/index/media backups and compatible descriptor state.

The production-like HTTPS Apache and Caddy/Django rehearsals also passed three
helper checks each on 2026-11-01: canonical and compatibility EDAM endpoints,
CSRF rejection, demo isolation, and authenticated editor/search lookup. The
packaged production-image checks additionally covered secure cookies, API/admin
isolation, crawler pages, canonical URLs, sitemap, deny-all robots, static assets
and media. These local checks do not establish the live deployment's origin,
indexing policy or proxy trust.

An initial full-suite rerun on 2026-11-01 was interrupted after 232 of 352 tests
when upstream EDAM test setup was found to rewrite generated files in the preview's
shared backend-data volume. The 60 generated JSON files now match the corresponding
preview database values, and the four vocabulary trees captured before the run
also match those rewritten files. Earlier on-disk contents of the other derived
files were not captured, so their prior bytes cannot be independently confirmed.
Subsequent full-suite testing uses `compose.full-tests.yml`: read-only source and
legacy-asset mounts, a private tmpfs copy of the EDAM seed, the Django test
database and a separate Elasticsearch service. The partial run is not full-suite
evidence.

The isolated rerun was also stopped before completion when its buffered log
appeared stalled; a subsequent verbose run showed that the older authorization
tests progress slowly. The interrupted run is not a full-suite pass. The rebuilt production
image (`sha256:08c427bfa30bdb501316dfa28785e8c35e18a3bbf001b198a121e96dbc0f1c0b`)
passed all five packaged HTTPS browser checks, including secure sign-in cookies,
native routes, crawler behavior and desktop/mobile workflow rendering.

The subsequent isolated full backend run completed on Python 3.13: 352 tests in
257 seconds, passing with 10 opt-in live-Elasticsearch tests skipped. It used the
private EDAM tmpfs and separate search service described above. An existing test
helper was also bounded to report an error if search results never appear instead
of retrying indefinitely.
All 10 skipped tests then passed separately on the isolated search service using
a temporary source index cloned from the preview index's mapping and analysis
settings, read without changing the preview index. The first separate attempt
failed because the preceding full suite had left the isolated source index with
a different mapping; that attempt does not establish an application regression.

## Permanent browser helpers and demonstration pages

Canonical search and editor now use `/_edam/terms/` for EDAM lookups. The old
`/_migration/html/edam/terms/` continues to call the same lookup without a
redirect, retaining query strings and existing clients. Both endpoints retain
the lookup's validation, no-store behavior and public-read semantics. The new
route is owned by Django for browser and crawler requests and returns `noindex`;
it does not change public `/api/*` authentication.

With the intended account/editor/search cutovers enabled, canonical production
pages use `/auth/session/`, `/auth/check/`, `/_search/data/`, canonical editor
save/validation routes and `/github-to-biotools` where configured. Legacy
session bridge and preview aliases remain for already-running clients and
selective rollback. They are not a reason to retain demonstration pages as a
production dependency, and they must be rechecked before legacy removal.

`BIOTOOLS_MIGRATION_PREVIEW_DEMOS=0` hides the isolated migration landing,
message-preview, counter-island and EDAM demonstration pages, returning 404.
It does not block the EDAM alias, session bridge, editor/search preview aliases
or normal canonical pages. The production image stages and `compose.prod.yml`
default the setting to `0`. Ordinary development retains its default of `1`;
deployments that do not use those production artifacts must set it explicitly.
This setting is not a replacement for authentication or the cutover switches.

## Local verification, 2026-10-29

- 77 affected backend/editor/account/search tests passed on Python 3.13 and
  Apache's Python 3.10; four integration tests were skipped on each runtime.
- 38 HTML/helper/cutover tests passed on each runtime after demo isolation.
- Apache and Caddy configuration validation passed. Browser and Googlebot requests
  through both proxies verified the new and old EDAM endpoints, validation and
  CSRF behavior; canonical search and editor used the new endpoint. Existing
  enhanced search journeys passed at desktop/mobile sizes on both proxies.
- A disposable Compose override set `BIOTOOLS_MIGRATION_PREVIEW_DEMOS=0` on both
  backend runtimes. Each proxy passed three checks: canonical search/editor,
  old/new lookup contract, demo 404s and retained preview-editor redirect.
  Browser reports: `tests/browser/test-results-readiness-prodmode-{apache,caddy}`.
  The initial helper test expected 405 for a POST without CSRF; the actual
  middleware correctly rejected it with 403, and the corrected check passed.
- The local preview was restored to its normal development configuration after
  the rehearsal. Backend logs are `/tmp/biotools-readiness-helper-tests.log`,
  `/tmp/biotools-readiness-helper-apache-tests.log`,
  `/tmp/biotools-readiness-preview-tests.log` and
  `/tmp/biotools-readiness-preview-apache-tests.log`.

## Domain concurrency and index recovery

The versioned Domain table intentionally permits several historical rows per
name. Migration `0006_domain_name_lock` adds a unique per-name lock table; the
shared creation serializer acquires its normalized name's row lock inside the
transaction and checks active versions again after acquiring it. The lock stays
held through the outer API/native-form transaction and index write. Successful
name locks are retained so later deletion and recreation reuse the same lock;
failed creates roll the lock back. Existing domain versions are not rewritten.
This serializes application create paths; direct database/ORM writes that bypass
the serializer can still violate the invariant and require separate control.
Before upgrading, check for and resolve existing duplicate active names, back up
the database, apply the additive migration before enabling the new code, and
avoid mixed old/new application versions handling domain creation. The disposable
preview had no duplicate active names before migration.

A real MySQL concurrent test forces two case-variant POST requests to validate
before either creates a domain, repeated for five independent names. On Python
3.13 and Apache Python 3.10, each pair produced one success and one rejection,
exactly one active domain and one index update. Tests also cover failed-index rollback/retry, reused deleted
names and existing owner/editor rules: 18 tests passed per runtime. Four native
domain create/edit/delete journeys passed on each proxy at desktop/mobile with
and without JavaScript. Logs: `/tmp/biotools-readiness-domain-final.log` and
`/tmp/biotools-readiness-domain-final-apache.log`.

MySQL and Elasticsearch still cannot commit atomically. An index operation may
take effect even when the application receives a timeout or a later database
commit fails. The operator must pause writes to the affected identifier, inspect
the visible database version and exact index document IDs, and retain evidence
before repair. If exactly one database version is visible, reindex its current
serializer representation under the existing exact document ID (domain IDs are
normalized names). If none is visible, remove only its exact stale index document.
If active database versions or index documents are duplicated or ambiguous, stop
and resolve them explicitly; do not choose a version or delete unrelated hits.
Refresh the index, verify detail and search/domain results, and only then allow
retries. A further failure may be ambiguous and requires repeating the inspection.

The guarded disposable rehearsal in
`backend/elixirapp/tests/readiness_index_reconciliation.py` actually applied an
Elasticsearch write and then simulated a timeout. It inspected the rolled-back
database and repaired creation, update and deletion of a domain, and disown and
deletion of a tool. It ran on both runtimes with external integrations disabled
and console-only email; uniquely named fixtures were removed from active results.
This validates a recovery procedure, not cross-system atomicity or a production
backup/restore rehearsal.

The production image was not rebuilt or deployed for these changes. Configured
ORCID/email, comprehensive accessibility, production indexing policy, agreed
performance budgets, backup/restore and the release-candidate inventory remain open.

## Release configuration findings, recorded 2026-10-29

The 2026-10-31 production image migration above supersedes the statements here
about the current Compose cutover switches and security defaults.

The checked-in settings and Compose files are templates, not evidence of the
actual deployment's overrides. They require operator review before production:

- Without deployment-specific overrides, Django defaults to debug enabled,
  wildcard allowed hosts and a repository-defined fallback secret. The secure
  session and CSRF cookie settings default to off.
  The production Compose file also contains development-oriented database
  defaults and publishes MySQL and Elasticsearch ports; Elasticsearch security
  is disabled. Do not use these defaults as an approved production configuration.
- The production image and Apache configuration supply a deny-all `robots.txt`.
  Confirm the desired indexing policy, sitemap, proxy/canonical-origin handling
  and crawler behavior for the actual public deployment before release.
- The disposable preview has debug disabled, but uses wildcard hosts, non-secure
  cookies suitable for its local HTTP address, console email and no configured
  ORCID application credentials. The optional GitHub bridge is disabled. These
  observations do not establish the configuration of the real deployment.
- The production Compose cutover switches default to off. A release candidate
  must record and verify the intended route switches and browser session bridge
  on each proxy/runtime; a successful disposable preview is not that evidence.

Do not copy secret values into this record. Confirm TLS termination, trusted
proxy headers, host/origin restrictions, secure cookies, network exposure and
secret delivery against the actual deployment before the security gate can pass.

The settings now accept `BIOTOOLS_ALLOWED_HOSTS` as a JSON array,
`BIOTOOLS_SESSION_COOKIE_SECURE` and `BIOTOOLS_CSRF_COOKIE_SECURE` as booleans,
and optionally `BIOTOOLS_SECURE_PROXY_SSL_HEADER` as a JSON pair. Set the proxy
header only after confirming that the trusted edge strips or overwrites
client-supplied forwarding headers. Production Compose forwards explicitly set
security, ORCID and email values, and can use consistent configured MySQL/index
credentials across services; it retains its existing development-oriented
fallbacks until the operator supplies secure values. SMTP password and TLS mode
are now configurable; operators must choose mutually compatible TLS/SSL settings.
Do not put actual credentials in tracked files or evidence. Environment selection,
invalid-value rejection, host validation, secure CSRF cookies and HTTPS header
handling passed local tests, including secure session and CSRF cookies on login,
as did Compose interpolation with disposable values. The 47 security, account
and route tests passed on each Python runtime.
No live email, ORCID call or production proxy trust was verified.

## Partial local artifact inventory

- The preserved implementation checkout is based on develop commit
  `9faec5b3b660498fdef9736e65e331728b55f99c` and contains uncommitted migration
  changes; the commit ID alone therefore does not identify a releasable artifact.
  The reviewed upstream integration was pinned at
  `400bbe32bbdc5396356b35a8f8b4040a731978e5`.
- The active resource descriptor revision is
  `41c6bde30ed530b2de333f02fc848b54da4951624662807703e68c47d451277a`.
  The local frontend bundle is `assets/main-Cwc_Nbcf.js`, SHA-256
  `68903208a7a9a451fca10b956f1c2ccb59bc2231482e83318f3242771cf8a50c`.
  Development uses Python 3.13.15; the Apache preview uses Python 3.10.12.
- Active EDAM revision digests: topic
  `8ae560dfda0caed0fe2b99d18489bf134d090432e72c3a234282a3e9dae8d512`, operation
  `e74fec865a41266fc08da57b7c67774555a29d66ac626d146fe350b48d34545d`, data
  `738792d80e7296688ae90514618aca1bb0a40c19c9436940b384f79b911a2e0e`, format
  `8f92e45f8423253c7b377765d2dfb440301403e35f8534af542612dbd46ee05a`.
- The local database has migrations through `elixir.0006_domain_name_lock`.
  The optional provider is disabled; the reviewed pinned bridge image and its
  limitations are recorded in [upstream integration evidence](upstream-dev-integration.md).
  The [route matrix](route-ownership.md) and [dependency audit](legacy-removal-audit.md)
  inventory current routes, aliases, callbacks and retained assets.
- `docker compose -f compose.prod.yml config --quiet` validated syntax only.
  No actual production settings, credentials, deployed artifact identity or
  production-like load dataset were inspected. Complete tasks 1.1 and 1.3 against
  the real release candidate after experience acceptance; do not treat this
  partial local inventory as their completion.

### Asset and service boundaries to carry into the release inventory

| Item | Current source or destination | Remaining decision |
| --- | --- | --- |
| Modern and Django/admin/API static | `backend/elixir/static/` collected into `/elixir/application/frontend/static/` | Preserve manifest, generated bundle and collected assets when replacing the shared frontend static root. |
| Public images and logo | Retained `backend/elixir/static/public/img/` and `html/` static assets | Verify byte identity and routes in the final artifact; do not delete historical assets before classification. |
| Legacy UI, fonts and templates | `frontend/dist/`, components, partials and vendor assets under the proxy document root | Needed for rollback and still-active legacy infrastructure until the pre-removal gate authorizes cleanup. |
| Schema and reference files | Backend `elixir/biotoolsSchema/` and historical `frontend/resources/` | Keep the active schema/descriptor and classify historical distributions and public consumers before deleting or relocating them. |
| Workflow media | Persistent `media_data` mounted at `/elixir/application/media_cdn` | Preserve and back up existing media; Caddy reads it and Apache serves it without directory listing. |
| Robots and sitemap | Apache aliases deny-all robots; sitemap/API routing follows current proxy configuration | Agree and verify production indexing policy and public origin. |
| Legacy services | Frontend build/runtime and Rendertron in Compose/proxy configuration | Inventory is not permission to remove; prove each dependency unused and verify the clean artifact afterward. |

Local sizes and counts are not a production asset inventory. Classify the 841
historical `frontend/resources/` files and any external consumers against the
actual release candidate before deleting them.

## Cleaned-source verification, 2026-11-01

On the local `trial_rewrite_codex` working tree, the complete isolated backend
suite ran 351 tests successfully with 10 opt-in live Elasticsearch tests skipped.
Those 10 then passed against a separate temporary Elasticsearch service using a
read-only copy of the preview index mapping. The backend runner used a private
EDAM tmpfs; it did not use the preview's generated vocabulary files as writable
storage. The modern frontend type check and all 118 unit tests also passed.
The remaining browser checks are being run against an independently provisioned
MySQL, Elasticsearch, EDAM and media stack with disposable fictional fixtures.

The cleaned-source browser run covered 137 scenarios on the disposable Apache
stack: 127 passed, eight were skipped for alternative configurations, and two
editor tests failed because the test navigated before sign-out completed. The
editor test was corrected to await sign-out; all four editor-route tests then
passed on rerun. Four formerly skipped Angular-only discovery checks were rewritten
for native search and detail and passed separately. The other four skips were
covered separately: secure cookies, disabled demos and disabled GitHub import
passed on the local HTTPS image, and the schema-update rehearsal passed through
an isolated Apache and Caddy pair. The schema rehearsal used a temporary copy of
the existing test configured for disposable database/search services; it verified
added, removed and restored fields and terms, persisted values, and the unchanged
frontend bundle. No live ORCID, SMTP or production deployment was tested.
Local browser traces and screenshots were consolidated under the ignored
`tests/browser/test-results-final-20261101/` directory.

## Cleaned candidate inventory, 2026-11-01

This is the local candidate, not an identification of the live deployment. The
active branch is `trial_rewrite_codex` at `a1fc8b94067f33bc9047efc9c75ebe1579365a07`,
with uncommitted migration work built from develop baseline
`9faec5b3b660498fdef9736e65e331728b55f99c`. The reviewed upstream integration
was pinned to `400bbe32bbdc5396356b35a8f8b4040a731978e5`. The locally built
production image is `sha256:ef56bed6bbc432d50426422f3d1f65b4579860f67e24f3865819e481151f4d87`;
its source is not yet represented by a commit. The optional bridge is disabled
unless configured; the reviewed image is pinned to
`sha256:d9dc5a5484247b9eedc9e204aea999bcd82fce79e5fea8bdfe4681b50203ec61`.
Its live credentials, provenance and capacity remain unverified.

The active biotoolsSchema 3.3.0 XSD SHA-256 is
`d34152910ce66ba644fd596d82a37baaf1b4dbbe55abe1bf41935fc12490e3f0`;
the generated descriptor revision is
`41c6bde30ed530b2de333f02fc848b54da4951624662807703e68c47d451277a`
and its file SHA-256 is
`1071a7a41af22858555509f0294cf543bab14eabe37e0d30de3e9d07bcaa43fb`.
The built `assets/main-4sLvRjQW.js` SHA-256 is
`6c261eb85ec8168758972a4c073a50bffdb9aaf1212dc95ba7c197a52a51553d`.
The local vocabulary is EDAM 1.25. Raw SHA-256 digests of the preview database's
ontology JSON are topic `04b1012ad7fe0c39f2dcf5b619923827c35dc912c64d08d2722c91d821313f61`,
operation `6d1f0778531eac04e1f4d1e6056fe93c4dc08d354b2c7198df22c62ba3e02ffc`,
data `d5af0c7fb32c216a3557fac1b8511def7a1be2af15a8e8d5c06fc9a3196cd33d`,
format `d1a93eac9c04731ea3088fbccf4d5b6df8deb7f6ae7d9dfab2f56226be373e2f`
and obsolete `6724a77f1b5a398bfc8c458119b6a15ac23a181f3dc6ecf6cdb58a56f9d5eb00`.
The preview database reports migrations through `elixir.0007_workflow_design`.
These hashes describe local data, not production vocabulary state.

The route inventory for the audited B01-B13 dependencies is:

- B01 accounts: `/login`, `/signup`, `/signup/verify-email/...`,
  `/reset-password/...`, `/profile/...`, `/auth/...`, and `/orcid/callback/`.
  Email verification/reset and ORCID callback origins must be configured for the
  actual deployment; the local provider checks are not live-provider evidence.
- B02 and B08 search/detail/editor: `/t`, `/_search/data/`, `/:id`, `/tool/:id`,
  `/t/:id`, `/register`, `/:id/edit`, `/requests` and their save/validation routes;
  native no-JavaScript fallbacks remain available. `/_edam/terms/` is the stable
  vocabulary helper; `/_migration/html/` compatibility endpoints remain for
  browser sessions and existing clients.
- B03 and B07 public pages and redirects: `/`, `/about`, `/community`,
  `/communities`, `/domains`, `/stats`, `/404` and the fixed `/schema`,
  `/governance`, `/events`, `/mail`, `/faq`, `/apidoc`, `/changelog`, `/helpdesk`,
  `/projects` and `/roadmap` redirects.
- B04-B06 management and workflows: `/:id/manage`, `/domain-manager`, `/subdomain`,
  `/edit-domain[/id]`, `/edit-subdomain[/id]`, `/workflows`, `/workflows/design/`
  and `/_workflow/{matches,function,compare,designs,shared}/` with design IDs and
  share routes. The image workflow gallery and non-executable designer coexist.
- B09-B12 runtime/build: Angular/Bower/Gulp, Rendertron and their services are
  removed; Django/htmx/Vue assets are built by Vite and collected by Django.
  `/api/`, admin, `/static/`, `/resources/`, `/img/`, `/json/` and `/media/` remain
  explicit boundaries. CI builds the native image and runs modern checks.
- B13 optional GitHub bridge: `/github-to-biotools` uses the configured internal
  provider, if enabled, with a disabled/manual-entry fallback. No production
  bridge is assumed to be configured.

`registry-assets/` retains 841 schema/reference files, 60 historical images and
2 JSON references; 305 local collected static files include generated artifacts.
The packaged image builds and collects its own static files. Actual deployed
static/media destinations, callback origins, credentials, external consumers,
robots/indexing policy and retained backups must still be checked by operators.

The cleaned production image also passed the accepted local workflow-search
performance limits against the 34,519-record corpus and EDAM 1.25 snapshot on
isolated MySQL 8.0.43. The broad scan's p95 was 289.6 ms and slowest page 385.8
ms; four simultaneous first-page requests took at most 621.5 ms. Operation-filtered
uncertain results had p95 874.3 ms and maximum 904.4 ms. See the
[workflow matching evidence](workflow-tool-matching.md#full-corpus-rehearsal-2026-10-31).
General search, editor, management and actual production performance budgets
remain open and are not implied by this in-process workflow measurement.
