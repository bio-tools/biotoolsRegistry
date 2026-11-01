# Migration baseline

Selected on 2026-09-11: **upstream `bio-tools/biotoolsRegistry`, branch `develop`,
commit `9faec5b3b660498fdef9736e65e331728b55f99c`** (2026-05-15).
This is the target for every frontend migration change, not the stale local
`develop` branch or the `origin` remote pointing to `veitveit/biotoolsRegistry`.
Pin the SHA when implementing; advancing it requires another recorded delta review.

The original working tree remains based on `a1fc8b94067f33bc9047efc9c75ebe1579365a07`.
The accepted develop integration is the separate `develop-migration/` checkout.
Historical inventory and completion records remain evidence for the older tree;
the develop review supplements them without changing their source revision.

Refresh progress and source deltas are recorded in [develop-refresh.md](develop-refresh.md).
The four foundations have been revalidated on both develop deployment paths.
Use `develop-migration/` for subsequent implementation and the preview, not the
original worktree. Exact test results and external-provider limitations are in the
refresh record.

## Accepted refresh

[refresh-develop-migration-baseline](../../openspec/changes/archive/2026-10-29-refresh-develop-migration-baseline/proposal.md)
was implemented in the isolated checkout, preserving the original dirty worktree.
Continue the remaining feature dependencies there. This accepts the foundations,
not canonical route cutover or production ORCID/Rendertron configuration.

## Accepted upstream behavior update: 2026-10-27

`adopt-upstream-dev-features` incorporates the reviewed behavior from upstream
`dev` at `400bbe32bbdc5396356b35a8f8b4040a731978e5`. The Git checkout still has
the develop base above and preserved local migration edits; this is not an
upstream merge. The [integration record](upstream-dev-integration.md) supplies
the source disposition, pinned bridge image, schema revision, packaged image
identity and local acceptance evidence. Use that accepted behavior baseline for
management and polish, while retaining separate production-readiness gates.

## Confirmed differences

These source observations guided the deployment tests in the refresh record.
The [pinned develop commit](https://github.com/bio-tools/biotoolsRegistry/commit/9faec5b3b660498fdef9736e65e331728b55f99c)
is one commit ahead of upstream main `bac50e8b09389b24becb319d66cef364dbde9c84`.
That commit changes production Compose, Bower/Gulp and search/detail icon markup.

| Area | Develop evidence | Migration consequence |
| --- | --- | --- |
| Backend runtime | [Requirements](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/backend/requirements.txt) pin Django 5.2.11, django-allauth 65.14.3 and dj-rest-auth 7.1.1. The Dockerfile uses Python 3.13 for builder/dev and a separate Ubuntu-based Apache production stage. | Revalidate dependencies and foundation code on the actual development and production runtimes, not Python 3.8/Django 3.1. |
| Authentication | [URLs](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/backend/elixirapp/urls.py) include ORCID login/connect, social-account listing/disconnection and reset-confirmation routes. Settings retain DRF TokenAuthentication. | Preserve supported account flows and token clients; installed SimpleJWT does not establish active JWT usage. |
| Development routing | [compose.yml](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/compose.yml) runs Django runserver behind [Caddy](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/backend/Caddyfile). | The old HTML WSGI environment marker alone cannot establish an HTML mount through this HTTP proxy. Design and test routing explicitly. |
| Production and crawlers | [Apache](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/backend/runtime/apache.conf) and Caddy include bot/Rendertron handling and search noindex headers; compose.prod.yml differs from development. | Test browser, bot, API and static requests, Vary headers and rollback through both paths. Verify Rendertron provisioning, not just its config reference. |
| Legacy build | [package.json](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/frontend/package.json) declares Gulp 5.0.1; develop updates gulpfile.js and Font Awesome handling. | Do not retain Node 11/Gulp 3 assumptions. Run the actual build and record pre-existing failures; retain one separate modern Vite package. |
| Public behavior | Search/resource handlers, validators, serializers, frontend router/services, detail and editor templates differ from the old tree. Settings' default API page size is 50, formerly 10. | Re-inventory supported contracts and regenerate fixtures; file differences alone do not prove a particular semantic change. |
| Tests and CI | Develop has `.github/workflows/test-api.yml` and backend CRUD/authorization/validation suites under `backend/elixirapp/tests/`. | Reuse existing infrastructure and isolate database/index fixtures. The old inventory's absence-of-CI conclusion is historical, not current. |
| Branding | Blue `#005472` navigation and `biotools_white.svg` replace this fork's orange/ELIXIR branding. | Keep the corrected shell and compare rendered branding with develop; do not regenerate its legacy bundles to recolor them. |

## Change-specific review

| Existing change | Required develop review |
| --- | --- |
| inventory-frontend-migration | Refresh all route/API/search/editor/risk documents; explicitly map additions and removals, including account, statistics and domain surfaces. |
| add-frontend-regression-harness | Rerun against a seeded develop build; adapt accessible selectors and fixtures to observed behavior; review existing CI. |
| add-django-html-shell | Port settings/routing, verify Caddy/runserver and Apache, auth context, static assets, errors and upstream branding. |
| add-htmx-progressive-enhancement | Revalidate Vite/static integration, full/fragment responses, history, errors and CSRF on the newer stack and both proxy paths. |
| add-vue-island-runtime | Reuse the ported Vite package and verify JSON props and htmx lifecycle on the accepted shell. |
| extract-shared-query-services | Characterize develop search/resource/domain behavior and API representations before extracting it. |
| migrate-public-tool-detail | Preserve current metadata, publications, links, permission actions, icon assets and crawler behavior. |
| migrate-browser-authentication | Trace current dj-rest-auth/allauth, ORCID and recovery flows; test permissions and active token authentication. |
| add-vue-search-workspace | Refresh URL/filter/sort/pagination/defaults and rendering expectations from develop. |
| add-advanced-search-filtering | Extend the refreshed authoritative search contract; do not infer behavior from old query code. |
| add-edam-selector | Inspect develop's editor EDAM modal, lookup behavior and validators before selecting the reusable contract. |
| add-resource-editor-data-contract | Recheck serializers, validation paths, replacement/patch behavior and round-trip preservation with current fixtures. |
| migrate-resource-editor-basic | Use the refreshed data contract, auth, permissions and basic-field validation. |
| migrate-resource-editor-nested | Review current nested structures and EDAM behavior; preserve untouched supported fields. |
| cut-over-migrated-routes | Use the refreshed route matrix and verify Caddy, Apache, bot handling, API/schema/account routes and rollback. |
| remove-legacy-angularjs-frontend | Audit develop's Compose files, Gulp/Bower/icon assets, CI, Caddy/Apache and Rendertron before deleting anything. |
| migrate-account-pages | Reuse the implemented session contract and current allauth policy; cover nested email/provider URLs and profile actions, not only login. |
| add-schema-driven-resource-ui | Reconcile bundled schema, serializer shapes, manually maintained backend choices and UI field lists; automate compatible active-contract updates without losing data or specialized function presentation. |
| complete-search-filter-parity | Characterize remaining router/backend parameters, repeated values, domain/EDAM filters and native search; preserve supported URLs without Angular fallback. |
| migrate-public-information-pages | Port current home/community/domain/statistics content and data; inventory redirects and shared images rather than redesigning from the old tree. |
| migrate-record-and-domain-management | Characterize current delete/disown/JSON validation, domain permissions/membership and workflow image inspection; reuse migrated editor permissions and requests. |
| polish-and-validate-migrated-experience | Review the actual migrated pages with sparse/rich schema fixtures, blue branding, keyboard access, mobile/reflow and cross-page acceptance. |
| verify-production-migration-readiness | Separate configured provider/security/indexing/performance/rollback pre-removal checks from clean legacy-free artifact verification; production approval remains explicit. |

The four foundation changes have completed develop revalidation tasks and linked
revision-specific evidence. Their previous completed items remain historical.
Remaining changes must perform their own develop impact review during implementation.
