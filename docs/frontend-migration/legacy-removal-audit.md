# Legacy frontend removal audit

Date: 2026-10-14. Result: **BLOCKED: do not delete the legacy frontend.**

## Baseline and method

Audited the then-current dirty `develop-migration/` implementation checkout, whose HEAD
is pinned upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
This is a source/configuration audit of that checkout plus its migration evidence,
not an audit of the older outer application's runtime or a production inspection.
Paths below are relative to the implementation checkout. This document is mirrored
in the outer documentation tree for planning.

Read the Angular router and its linked controllers/templates; compare Django
canonical/preview routes and search parsing; trace template assets, backend
settings, both proxies, all three application Compose configurations, Dockerfiles,
CI, contributor hooks, setup docs and regression tests. Repository searches used
`rg` for `frontend/`, `angular`, `bower`, `gulp`, `rendertron`, `dist/`,
`index.html`, route declarations and fallback links. Installed vendor trees and
generated bundles were not treated as independent application source.
The [develop impact matrix](baseline.md#change-specific-review) and
[route ownership evidence](route-ownership.md) were reviewed.

No server restart, deletion, runtime edit, dependency installation, browser test
or production request was performed for this audit. Earlier test results in the
ownership record are historical evidence, not a fresh audit test run.

## Route and behavior blockers

The entries below record the original audit. See the dated disposition update
for implemented replacements; a proposal alone is not proof of migration.

### Disposition update: 2026-10-15

B01 now has native account pages behind `BIOTOOLS_CUTOVER_ACCOUNTS`, including
profile settings, email/recovery links and server-side ORCID handling. Backend
policy fixtures pass; configured live ORCID and real email delivery remain
production-readiness gates. See [account evidence](account-pages.md).
Profile disown remains an explicit legacy link owned by B04, not a completed
management migration.

The account-helper part of B08 now uses permanent `/auth/session/`,
`/auth/check/`, `/auth/logout/` and `/login` on canonical pages. Old preview
aliases and the retained-page session bridge remain intentionally available.
At that date other B08 fallbacks and B02-B07/B09-B12 still blocked deletion. Normal production
switches remain off; this update does not claim a production rollout.

### Disposition update: 2026-10-22

B02 and the search-fallback portion of B08 are resolved locally by
`complete-search-filter-parity`. All 61 functional backend filter keys plus
domain membership work through the shared query service; repeated keys retain
last-value semantics. Native GET results, constraints, comparison, paging and
errors work without JavaScript or modern assets. Unsupported input returns 400,
not an automatic Angular redirect. See the
[compatibility matrix and acceptance evidence](search-filter-parity.md).

The explicit `_legacy=1` rollback, legacy grid layout preferences, editor
fallbacks, remaining helper aliases and B03-B07/B09-B12 are still retained.
Search comparison data is available natively; exact saved grid layout migration
is a polish/retirement review item, not a claim that legacy assets are disposable.
No production activation or legacy deletion is authorized by this update.

### Disposition update: 2026-10-24

B03/B07 have native replacements behind `BIOTOOLS_CUTOVER_PUBLIC`: home,
about/community pages, searchable public domain directory, four existing
statistics sources, fixed server redirects and genuine missing-page responses.
The public-content portion of B10 now has 40 byte-identical images in retained
Django static storage. Original images/URLs remain for rollback. Source inventory,
data semantics, tests and the observed external-target failures are recorded in
[public-page evidence](public-information-pages.md).

This does not close domain administration, workflow browsing, record management,
editor fallbacks, infrastructure cleanup or the rest of B10. Six external shortcut
destinations failed the recorded reachability checks; their current destinations
remain intact pending content-owner review in production readiness. No production
activation, legacy deletion or clean legacy-free release is claimed here.

| ID | Dependency and source evidence | Required disposition / owner |
| --- | --- | --- |
| B01 | `frontend/js/app.js` account states; `frontend/js/lib/djangoAuth.js`; `frontend/components/profile/profileController.js` and `profile.html`. Canonical login, signup, verification, recovery, profile and ORCID callback still use Angular. Profile includes email/password changes, resend verification, connected accounts and owned/shared resources. | `migrate-account-pages`: native pages using existing account policy and browser sessions. Keep public token APIs unchanged. Profile disown action belongs to B04. |
| B02 | `backend/elixirapp/search_workspace.py:canonical_page/parse_search` allow only 12 simple filter keys plus q/sort/ord/page/per_page/advanced; unknown keys redirect to `_legacy=1`. `frontend/js/app.js` declares many additional keys, including domain and EDAM IDs. Repeated values are rejected by the modern parser. | `complete-search-filter-parity`: characterize supported backend semantics, preserve bookmarks and repeated-value behavior; never silently discard filters. Domain queries already have shared service support in `backend/elixir/queries.py`. |
| B03 | `frontend/js/app.js` public states and `frontend/components/{home,about,community,stats}/`, `partials/subdomains/domains.html`. Home, informational pages, public domain list and statistics remain Angular. | `migrate-public-information-pages`: Django pages and appropriate small enhancements; preserve live content/data, search links and public navigation. Statistics use four API data sources, not static placeholder charts. |
| B04 | `frontend/partials/toolEdit.html` Remove/Validate controls; `partials/tool_edit/toolEditJSON.html` editable JSON; `frontend/js/controllers.js` mutation handlers; `frontend/components/profile/profileController.js` disown. `backend/templates/html/tool_detail.html` still has a legacy Manage record link. Modern `ResourceEditor.vue` exports drafts but has no raw JSON editor, standalone validation or delete/disown controls. | `migrate-record-and-domain-management`: migrate supported delete/disown and JSON editing/validation workflows using authoritative policies. Reuse the already migrated permissions editor and request inbox; do not implement them twice. Unproven historical versioning is not automatically a supported feature. |
| B05 | `frontend/js/subdomainController.js`, `partials/subdomains/`: domain create/edit/delete, resource membership and editor management at domain-manager/subdomain and edit-domain/edit-subdomain aliases. `backend/elixir/view/domain.py` owns API policy; some UI restrictions alone are not an authorization boundary. | `migrate-record-and-domain-management`: native protected forms and current-owner authorization, with mutation failure/index consistency tests. Public domain directory belongs to B03; domain-filter search to B02. |
| B06 | `frontend/js/workflowController.js`, `partials/workflows/{workflows,modal}.html`: public workflow list/filter and annotated image inspection from `/api/w`, image media URLs and coordinate scaling. No browser workflow authoring screen was identified. | `migrate-record-and-domain-management`: preserve browsing, filtering, images and annotation interaction. Do not invent a workflow authoring application; preserve existing staff/API workflows. |
| B07 | `frontend/js/app.js` redirect states and 404; `frontend/partials/schema.html` meta-refresh. Fixed outbound redirects and literal paths currently depend on the SPA. | `migrate-public-information-pages`: server redirects and real error status pages; reserve literal routes before tool-ID matching. Check destinations at implementation time; external availability was not verified here. |
| B08 | `backend/templates/html/{search,resource_editor}.html` use `_legacy=1` for unenhanced/failed-asset fallback. `html.py`, both proxies and Angular router keep an explicit escape hatch. `html_urls.py` still hosts production-used session/EDAM helpers beneath `/_migration/html/`. | Search change supplies native GET results; management change supplies a truthful, non-destructive editor failure state without a legacy link. Account change moves production auth helpers to stable routes; remaining helpers get explicit permanent destinations during readiness. Remove obsolete escape hatches/bridge only in the retirement change after replacement tests. |

### Complete route-family assignment

The router's concrete states are accounted for below, including nested URL forms.
Aliases are compatibility requirements, not new product pages.

- Accounts (B01): `/login`, `/signup`, `/signup/success`,
  `/signup/verify-email/success`, `/signup/verify-email/:key`,
  `/reset-password`, `/reset-password/confirm?uid&token`,
  `/reset-password/confirm/success`, `/profile`, `/orcid/callback/`.
  The abstract verify-email parent is not a standalone workflow.
- Public information (B03/B07): `/`, `/about`, `/community`,
  `/communities`, `/domains`, `/stats`, `/schema`, `/404`;
  redirects `/governance`, `/events`, `/mail`, `/faq`, `/apidoc`,
  `/changelog`, `/helpdesk`, `/projects`, `/roadmap`.
- Management (B04-B06): `/domain-manager`, `/subdomain`,
  `/edit-domain/:id`, `/edit-subdomain/:id`, `/workflows`;
  record actions reached from detail/editor/profile. Their destination URLs must
  be specified during implementation without exposing mutations through GET.
- Partially cut over (B02/B08): `/t`, `/:id`, `/tool/:id`, `/t/:id`,
  `/:id/edit`, `/register`, `/requests`, plus native save/request endpoints.
  The extra legacy `subdomain` state overlaps `/t`; it is not a new page.
- Preserve server-owned boundaries: `/api/*`, Django admin/allauth/rest-auth,
  media, robots, sitemap, favicon and static URLs. Their location under a legacy
  document root does not make their content disposable.

## Infrastructure and shared dependencies

| ID | Dependency and source evidence | Required disposition / owner |
| --- | --- | --- |
| B09 | `frontend/index.html` loads `dist/vendor.min.*` and `dist/app.min.*`; Angular templates load component/partial files. `frontend/{package.json,package-lock.json,bower.json,gulpfile.js,Dockerfile}` and vendor/fonts/images produce the legacy bundle. Gulp is 5 in this develop tree; the legacy Dockerfile still names Node 11. | Retain until B01-B08 have replacements; `remove-legacy-angularjs-frontend` removes only legacy-owned build/source/output. Inventory non-Angular resources before deleting directories. No dependency upgrades are part of this audit. |
| B10 | `backend/elixirapp/settings.py` defaults STATIC_ROOT to `/elixir/application/frontend/static/`; Swagger favicon points to `/img/favicon.ico`. Public pages use `frontend/img/logos/*`. Proxies serve frontend as document root. `frontend/resources/`, robots/favicon and collected admin/allauth/DRF assets must not be assumed obsolete. | Public-page migration owns referenced content images. Readiness records asset destinations; retirement relocates retained assets/static serving and verifies admin/API/media/robots/sitemap. Preserve schema/reference resources until their consumers and distribution use are classified. |
| B11 | `backend/{Caddyfile,runtime/apache.conf}` still serve index.html fallback and Rendertron for retained pages. `compose.yml`, `compose.prod.yml`, `compose.refresh.json` define legacy frontend service/bind mounts/dependency volumes and Rendertron; Caddy has a private renderer origin. | Readiness rehearses all-route ownership through both proxies. Retirement removes only retired fallback/service/mount/renderer dependencies and bridge transport after consumers migrate. Keep MySQL, Elasticsearch and media data; no volume purge. |
| B12 | `.github/workflows/test-api.yml` starts full Compose (indirect frontend dependency), alongside modern unit/type checks. `.pre-commit-config.yaml` targets/excludes frontend paths; legacy ESLint/Prettier config remains. Backend `test_html.py` asserts SPA fallback and `test_cutover.py` reads app.js; browser cutover/auth suites intentionally assert legacy behavior. `INSTALL.md`, `CONTRIBUTING.md`, browser README and migration runbooks describe the legacy stack. | Retirement adapts CI/hooks/tests/docs to the replacement contracts, retaining API/auth/security coverage. Do not delete the API job just because it starts Compose. Add modern build/full browser acceptance in readiness; preserve historical migration evidence with dated supersession notes. |

Modern source assets already live in `backend/elixir/static/html/`;
`frontend-modern/vite.config.js` emits `backend/elixir/static/modern/` and
`backend/elixir/templatetags/modern_assets.py` reads its manifest. These are
**retained**, not Angular dependencies. Their collected deployment output still
depends on the static-root/proxy work in B10.

## Additional upstream dependency: B13 (2026-10-25)

Upstream `dev` at `400bbe32bbdc5396356b35a8f8b4040a731978e5` adds a GitHub
metadata bridge editor/review workflow, internal service and proxy endpoint.
Its Angular implementation is not yet replaced in the migration. B13 is owned
by [`adopt-upstream-dev-features`](../../openspec/changes/archive/2026-10-29-adopt-upstream-dev-features/proposal.md).
The [upstream review](upstream-dev-review.md) also records vocabulary, dashboard,
save, picker and runtime changes that must be reconciled before final acceptance.
This is a newly identified dependency, not evidence that an earlier completed
change implemented the bridge. Add its native endpoint/service and assets to
the final route/configuration inventory; keep the bridge optional and retain
explicit manual editing when it is unavailable. No new deletion is authorized.

### B13 local replacement accepted: 2026-10-27

The native Django adapter and Vue review now replace the reviewed Angular import
workflow. [Integration evidence](upstream-dev-integration.md) covers both proxies,
desktop/mobile/keyboard review, explicit save, provider failure and independent
disable. Retain the optional pinned provider configuration, protected endpoint,
schema sources and modern bundle. Live provider credentials/capacity remain a
readiness check. The source-free packaged build includes both asset families;
this verifies packaging for B09/B10 but does not remove the remaining management,
fallback and infrastructure dependencies. B13 no longer blocks local functional
acceptance; legacy deletion still requires the full refreshed release audit.

### Management replacement update: 2026-10-28

B04-B06 and the editor-runtime portion of B08 now have native implementations:
record disown/removal, raw JSON draft editing and validation-only requests,
domain CRUD/membership/editor controls, and workflow filtering with accessible
scaled annotations. The [management record](record-domain-management.md) records
the actual owner/superuser/editor policy, protected domains, current-record races,
database/index failure handling and acceptance evidence. Rich editor runtime
failure offers stored JSON export/retry and no longer depends on Angular.

Retain the new management templates, schema-driven editor and shared picker,
workflow media and the persistent media volume. The management switch and explicit
legacy rollback remain; existing legacy assets/services, helper aliases, visual
acceptance and production gates still block deletion. Concurrent domain-name
creation and ambiguous database/index outcomes are explicit readiness inputs.

2026-10-29 readiness update: application domain creation now serializes by
normalized name, and recovery from applied-but-unconfirmed index writes was
rehearsed. The additive migration and operational limits are documented in
[production readiness evidence](production-readiness.md#domain-concurrency-and-index-recovery).
This does not close the pre-removal gate or authorize legacy deletion.
This update does not authorize legacy removal or production activation.

## Removal decision and verification gates

### Release-candidate recheck: 2026-10-31

This is the earlier recheck; the production build and Compose changes below
supersede its statements about the current production configuration.

The functional native replacements now include the workflow designer and draft
sharing. However, `compose.yml` and `compose.prod.yml` still default the cutover
switches to off, both proxy configurations still provide an Angular/Rendertron
fallback, and the root Dockerfile still builds and packages the legacy bundle.
Those references are active and cannot be removed until a tested replacement
deployment and the pre-removal readiness checks are in place.

The legacy directory is not exclusively application code: `frontend/resources/`
contains 841 tracked historical schema/reference files, some linked by existing
documentation. Preserve their public URLs and contents when moving them. The
collected `frontend/static/` tree also serves Django/admin/DRF and modern assets;
`media_data` serves user and workflow media. The Swagger favicon is now sourced
from Django static files, and the native shell uses the same retained icon; the
old icon path remains available to the still-supported legacy frontend. The
other asset destinations and both proxy paths still require verification.

Local recheck: the modern type check, 118 unit tests and Vite production build
passed; 78 Django tests covering cutover, public pages, browser authentication,
management and workflow drafts passed. `collectstatic` installed the retained
icon, which Apache served with HTTP 200; the Caddy-backed API documentation used
the new static URL. The running Apache WSGI process still needs a restart to load
the changed Swagger setting. Strict OpenSpec validation passed in both workspaces.
These checks do not demonstrate a legacy-free build or the external-provider and
rollback prerequisites.

Visual acceptance, configured ORCID/email, agreed representative performance
budgets, backup/restore and rollback rehearsals remain open; see
[production readiness](production-readiness.md). This recheck does not mark
the legacy-free build or the pre-removal gate complete.

### Legacy-free packaged rehearsal: 2026-10-31

The `native` target was promoted to `prod` later on 2026-10-31. The old `prod`
stage was removed from the current Dockerfile; preserve the prior production image
and its compatible configuration for rollback before any actual rollout.

The root Dockerfile now has a `native` candidate target alongside the existing
`prod` target. It builds the modern frontend and packages Django static files and
the historical `frontend/resources/` tree, without building or copying the
Angular application, Bower, Gulp, or a Rendertron service. Its Apache routing
serves Django browser pages, the existing API and preview helper mounts, static
files, historical resources and persistent media. Old `_legacy=1` links resolve
to the native page in this target. The candidate deliberately keeps the old
`prod` target and normal Compose defaults until the remaining cutover checks pass.

Rehearsal commands from the repository root:

```sh
docker build --target prod -t biotools-refresh/production:review .
docker compose -f compose.refresh.json -f compose.native-rehearsal.yml up -d --no-deps native native-caddy
docker compose -f compose.refresh.json -f compose.native-rehearsal.yml up -d --no-deps native-dev native-caddy-dev
```

The packaged rehearsal is `http://localhost:8005/`, or `https://localhost:8444/`
through the local Caddy TLS proxy. A separate Caddy-to-runserver rehearsal is at
`https://localhost:8446/`. Both share the disposable refresh database and search
index, and mount media read-only. Neither is a production
deployment and requires the existing refresh services and fixture data. Use the
browser guide for the opt-in native-package checks. Do not run write scenarios
against a non-disposable database. The local proxy sets the forwarded scheme;
the rehearsal trusts that header and exposes Apache only on loopback. Production
must restrict direct access to its own trusted proxy before enabling such trust.

Image `sha256:a2d6aaee9924ec38358d0afd9b01127235bc8e4ed01d63908c3c050be960696c`
built successfully; its frontend document root contained only `resources` and
`static`. Apache configuration and Django system checks passed. Four browser
checks passed for native browser/crawler routing, API/admin, preserved schema and
media, denied directory listing, non-JavaScript search, and desktop/mobile
workflow rendering. Seven workflow designer, matching and draft-sharing browser
checks passed through both HTTP Apache and HTTPS Caddy, including keyboard and
failed-asset recovery, against the preceding image
`sha256:85d749c001ff7cfe9b5a887bcd5682dacdb58f5b1270c3e946a0f3d385f3cff7`.
The mobile workflow test failed once under HTTPS and passed on rerun. The final
image changed backend test code only; it passed 78 cutover, public-page, browser
authentication, management and workflow-draft tests, with one expected skip for
the deliberately absent legacy router. The old production and rehearsal Compose
files no longer declare their unused Bower/node-modules volumes; no volumes were
removed.

The second Caddy rehearsal serves only the collected static files, historical
resources and media directly and forwards other routes to the development Django
WSGI entry point. Eleven browser/workflow checks and six account checks passed
there, including desktop/mobile and JavaScript-disabled sign-in. Twelve cutover
backend tests passed, including explicit native dispatch tests for API, preview
and unknown paths. Seven additional browser checks passed for workflow-image
alignment and keyboard access, failed-image and failed-asset recovery, and the
no-JavaScript editor fallback. This candidate does not yet replace the normal
development Compose configuration. The full browser/API suite, live provider configuration,
production-sized performance, release rollback and a final clean-source build
remain to be verified. The Angular source and existing production fallback remain
present; this change is not complete.

Standard development Compose now uses the native Caddy/Django path and no longer
defines Angular or Rendertron services. The refresh rehearsal and rollback still
retain them. The new production image uses native routes, but there is no evidence
here that the live production deployment has been migrated.

### Cleanup inventory, 2026-11-01

The intended source cleanup includes `frontend/components/` (56 tracked files),
`frontend/partials/` (71), `frontend/js/` (17), `frontend/css/` (17),
`frontend/lib/` (110), both legacy index files, the frontend Dockerfile, Bower,
Gulp, npm and legacy lint configuration. The installed `bower_components/`,
`node_modules/` and `dist/` are generated and are not evidence that the source is
unused. `compose.refresh.json`, `backend/Caddyfile`, `backend/runtime/apache.conf`
and `backend/Dockerfile` still support the old rehearsal; related route rollback
and legacy-only test assertions must be retired together, after the readiness gate.

Retain all 841 tracked `frontend/resources/` schema/reference files and their
`/resources/` URLs. The new production image and standard Caddy serve them there.
`frontend/static/` has 170 tracked files as well as generated Django/admin/DRF
and modern assets; relocate or regenerate it and verify its consumers before
removing its directory. `frontend/img/` has 60 tracked files: public-page images
and the favicon have native copies, but remaining public image URLs must be
classified before removing the originals. Preserve `frontend/json/edam.json`,
`frontend/json/model.json` and the old public `robots.txt` until their consumers
and the deployed indexing policy are resolved. Keep the persistent MySQL,
Elasticsearch, backend-data and media volumes; changing Compose does not remove
or reset them. Hooks, CI and documentation must be updated with the final removal.
`remove-legacy-angularjs-frontend` tasks 0.1, 0.2, 1.2, 1.3 and 1.4 can be
recorded as completed audit work. Task 1.1 remains unchecked because its required
condition is not met. No deletion/build-cleanup task is complete.

1. Implement the schema-driven UI foundation and four functional changes in the [finishing sequence](../../openspec/README.md#finishing-sequence).
   Every B01-B08 route/action must have a tested native replacement or explicitly
   approved retirement, with a documented destination for old links.
2. Complete experience acceptance and pre-removal readiness. Record live configured
   ORCID/email evidence, security/SEO checks, representative performance thresholds,
   helper URL ownership, deployment assets and rollback instructions.
3. Refresh this audit against the release candidate. Missing replacement
   dependencies still block deletion. Audited legacy build/proxy references may
   remain only as the enumerated cleanup set, with tested replacement destinations.
4. Remove the legacy stack using the existing removal change, then run the final
   readiness gate on a clean, legacy-free production-like build. Retest both proxy
   paths, native fallback, deep links, public APIs, admin and media.
5. Actual production deployment requires operator approval and a documented
   rollback release. Readiness documentation is not that approval.

## Limits

### Schema dependency update: 2026-10-21

`add-schema-driven-resource-ui` is complete for its local acceptance scope.
Retain `backend/elixir/biotoolsSchema/`, including the selected XSD, explicit
registry policy and approved generated descriptor; the editor, public detail,
search and validators now consume them at runtime. They are not disposable
Angular build artifacts. Keep the schema generator/check command in CI and the
Ontology-backed EDAM lookup. See [schema-driven evidence](schema-driven-ui.md).

The same-build schema activation/rollback rehearsal passed through both proxies,
including real persistence for a newly advertised nested field. This reduces
duplicated UI metadata but does not resolve B02-B12 or authorize legacy deletion.
Existing public owner metadata remains explicitly classified; permission authors
are not exposed by generic rendering.

Additional requirement recorded after the initial audit:
[`add-schema-driven-resource-ui`](../../openspec/changes/archive/2026-10-29-add-schema-driven-resource-ui/proposal.md)
addresses manually maintained field lists/labels/choices and automatic propagation
of compatible activated schema/vocabulary updates. It is a finishing prerequisite,
not a claim that every current schema-specific component depends on Angular.
Its schema sources and generated assets must be retained when classifying B09/B10.

No production configuration, traffic logs, external redirects, real email delivery,
live ORCID exchange, clean legacy-free build, load test or accessibility session was
checked in this audit. Static searches establish active dependencies, not the
absence of every dependency outside this repository. Existing test evidence does
not certify all retained workflows. These limits are explicit readiness gates.

### Source removal, 2026-11-01

The user authorized removal before the remaining production-readiness tests, to be
completed separately on the new frontend. The `frontend/` AngularJS source,
Bower/Gulp configuration, frontend and Rendertron Compose services, old Apache
and Caddy fallback configurations and route-selection switches were removed.
The API and browser-session helper, EDAM helper and compatibility URLs remain.

The former `frontend/resources`, `frontend/img`, `frontend/json` and
`frontend/static` trees were moved into `registry-assets/`. `/resources/`,
`/img/`, `/json/`, `/static/` and the favicon remain available through both
proxy configurations. Persistent database, index, backend-data and media
volumes were not purged. A local temporary archive was made before removing
legacy source, including the previously modified frontend files; prior releases
and their deployment configurations must still be retained for actual rollback.

The native route, account, editor, management, EDAM, bridge and workflow backend
checks passed (106 tests), as did the Vue type check and 118 unit tests. The
cleaned production image was built locally. The full browser suite, configured
ORCID and email, live deployment settings, actual production backups and other
release checks remain open in the removal and readiness changes.

### Checkout consolidation, 2026-11-01

The migrated `develop` checkout was moved to the repository root, replacing the
separate older checkout; its work remains uncommitted. The earlier local
`trial_rewrite_codex` branch was restored as a local branch without switching
away from `develop`. No push was performed. The previous checkout, including its
Git metadata and uncommitted files, is preserved in the private, ignored
`.previous-checkout-backup.tar.gz` file. It is also excluded from Docker builds.
To inspect or restore it, extract the archive into a separate directory rather
than over the active checkout. The local preview services were recreated with
bind mounts pointing at the new repository path; persistent volumes were retained.

The user subsequently requested `trial_rewrite_codex` as the active branch. Its
original commit was retained and the migration working files were preserved
without staging or committing them. The local `develop` branch was restored to
its original pre-consolidation commit `07652075014479541fdd1b9b6d07b0fbd750bf25`;
the newer migration baseline remains at `origin/develop`. Since the branches
diverged, the uncommitted diff against the trial branch includes the newer
develop baseline as well as the migration.
