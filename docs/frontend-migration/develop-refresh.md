# Develop baseline refresh

Inspected revision: upstream `bio-tools/biotoolsRegistry` develop,
`9faec5b3b660498fdef9736e65e331728b55f99c`. Review started 2026-09-11;
runtime validation completed 2026-09-13. This record supplements, rather than
relabels, the original `a1fc8b9` inventory.

## Work preservation

The original `trial_rewrite_codex` worktree was not switched, reset or stashed.
Its tracked settings/Apache edits, untracked shell/templates/assets/tests/docs,
and ignored OpenSpec changes were inventoried. Unrelated `.understand-anything`,
CSV/archive files, installer and user `.gitignore` changes were not transferred.
Generated node_modules, Python caches, modern bundles and browser artifacts were
excluded from the transfer and dependencies/assets rebuilt independently.

Integration checkout: `develop-migration/` inside the original workspace, cloned from upstream and
verified with `git rev-parse HEAD`. Only reviewed migration files were copied;
upstream settings, requirements, URLs, Compose and frontend sources were retained.
It was initially prepared at `/tmp/biotools-develop-migration` and then preserved
in the workspace as a separate Git checkout, ignored by the parent repository.
Copied directory permissions were made readable by container users. A test run
interrupted by the initial permission mismatch is not baseline evidence.

Disposable Compose configuration: `develop-migration/compose.refresh.json`, derived
from upstream Compose with separate `biotools-refresh-*` containers, volumes and
network. Database/index ports bind loopback only. Existing services and databases
are not used. Elasticsearch's test heap is bounded at 512 MB after an overnight
exit 137; the run against the stopped service is not compatibility evidence.
With 16 GB free on the large host disk, percentage watermarks also blocked writes;
the disposable cluster uses absolute 10/7/5 GB low/high/flood thresholds instead.
Disk protection was not disabled. No host data or unrelated Docker images were purged.

## Routes and deployment

This section records the refreshed baseline before cutover. The current
[route ownership matrix](route-ownership.md) records subsequent read-only
cutover, Rendertron provisioning and rollback verification status.

Comparing [app.js](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/frontend/js/app.js)
against the original inventory gives **41 states, one added and none removed**:
`orcid_callback`, `/orcid/callback/`, `OrcidCallbackController`,
`partials/orcidCallback.html`. The existing 40 state declarations, including the
declared search parameters, remain. Keep the callback on the legacy owner until
the authentication change replaces it with tested equivalent behavior.

The unchanged state list does not mean unchanged behavior: profile/account,
domain editing, search display and detail metadata have changed behind those URLs.
Home, search, editor, statistics, communities/domains, profile, recovery, requests,
workflows and informational routes remain legacy-owned during this refresh.

Develop uses Caddy -> runserver; production uses Apache/WSGI and Rendertron.
Caddy contains a Rendertron target but its development Compose has no Rendertron
service. Production Compose does include it. Preserve non-migrated crawler rules
and search noindex headers; do not claim bot parity for legacy pages without a
working prerender service. Isolated HTML and API paths must bypass prerendering.

## API and authentication

[Project URLs](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/backend/elixirapp/urls.py)
now use dj-rest-auth and current allauth. Additional supported surfaces include
`/api/schema/`, Swagger at `/api/`, ORCID login/connect,
social-account listing/disconnection, and reset-confirmation uid/token paths.
Registry route families retain their public aliases, with noncapturing optional
regex groups. Do not assign a browser catch-all ahead of these routes.

[djangoAuth.js](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/frontend/js/lib/djangoAuth.js)
still persists a token in localStorage and uses `Authorization: Token`.
ORCID callbacks post a code to `/api/rest-auth/orcid/` or `/connect/`; account
disconnection posts to the social-account endpoint. The browser ORCID service
stores and consumes an OAuth state token plus intended return route in
sessionStorage. Backend views use the configured callback URL and ORCID adapter.
The migration must not copy token storage into new browser pages or mistake an
installed SimpleJWT package for the active authentication mechanism.

[Custom serializers](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/backend/elixir/serialization/user_serialization/user.py)
require email for regular registration, expose socialAccounts/email_verified in
user details, and retain custom reset email templates. Allauth's account adapter
rewrites verification links to the frontend. Settings enable social email
authentication/auto-connect; the custom social adapter also connects an existing
email match and accepts authenticated linking with an email mismatch warning.
These are security-review requirements, not proof that linking is safe. Real ORCID
authorization, email delivery and configured callback behavior need provider
credentials and remain separate from deterministic local tests.

Domain management now admits owners **or editors** and uses different serializers
for public versus managing users. Preserve editor membership, permission checks
and private/public response distinctions when extracting query services.

## Search and detail

[services.js](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/frontend/js/services.js)
sets the default page size to **50**, offers 10/25/50/100, and sends `per_page`
for nondefault sizes. The paginator directive resets page on size changes and
offers direct page input. `per_page` is not declared in the router's search URL,
so URL refresh/history preservation needs an explicit regression test rather than
assuming the control state is canonical.

Backend search and resource listing parse `per_page`, fall back on invalid integers
and cap at 100. Their lower bound and invalid `page` handling are not validated
equivalently; preserve supported behavior and separately test malformed inputs.
Other query construction remains substantially the same. Cards/Table replace
Compact/Detailed labels; table name is pinned and Added/Updated columns exist.

Detail now advertises JSON/XML alternate links, publication/modification dates,
BIP/Dimensions publication widgets and additional ELIXIR communities; COVID
shortcuts were removed. Keep supported scientific metadata and permission actions,
and explicitly decide third-party widget parity rather than silently dropping it.
Statistics adds `toolTypeCounts` without adding a route family.

## Editor and data integrity

[The EDAM modal](https://github.com/bio-tools/biotoolsRegistry/blob/9faec5b3b660498fdef9736e65e331728b55f99c/frontend/partials/tool_edit/toolEditEdamModal.html)
is new. Its controller edits a copy, commits on modal success and dismisses on
cancel. It supports data/operation/format trees, term suggestions, filtering,
synonym/definition hints and EDAM-browser links. Data selection writes nested
`data.term`/`data.uri`; operation/format selection writes direct term/uri pairs.
Retain the cancel/commit distinction and concept-specific payload shape.

The authoritative resource model and serializer remove the old `community`
relation. Do not resurrect the old BioLib/community field solely to satisfy old
fixtures. `elixirCommunity`, collection IDs and domain memberships are different
supported concepts and must not be removed with it. Refresh enums from current
serializers instead of copying the old license/language/tool-type lists.

The high-risk replacement-save model remains: PUT validates, hides the previous
resource, creates its replacement and updates Elasticsearch. Nested missing values
become empty lists in creation; set-based deduplication is used for some scalar
lists. Old null cleanup/client-only fields and server error mapping still need
round-trip coverage. A passing basic edit must not be treated as nested-data parity.

## Reusable tests and known baseline failures

Upstream `.github/workflows/test-api.yml` builds Compose, grants test-database
privileges, runs Django tests and tears services down. Existing tests provide
CRUD/validation/permission fixtures, a mapping, and EDAM 1.25 setup. They mutate
the `test` Elasticsearch index and change global index settings, so run only in
disposable services, serially with respect to other index-dependent test suites.

Unmodified upstream backend and frontend Docker images built successfully.
`manage.py check` passed. Gulp failed at task registration with
`AssertionError: Task function must be specified`: Gulp 5 declarations still used
Gulp 3 dependency arrays. The integration adapts task composition/completion and
preserves binary font/image copying; it does not change dependency declarations.

The healthy immutable-image API run discovered 21 tests and finished with two
authorization-module import errors (`backend.elixirapp...`) and one failing
`test_format_invalid` subcase for an empty format. These failures predate migration.
The integration corrects the two module import paths to enable their coverage;
it does not change API format semantics to satisfy the existing assertion. The
complete selected run after correcting imports and restoring healthy services
passes all **57 authorization/permission/CRUD/parameter tests**. The earlier
empty-format failure is retained as an order/fixture-sensitive baseline observation.

## Validation status

Modern Vite and repaired legacy Gulp builds passed; Gulp was checked on both host
Node 22 and the unchanged Node 11 Docker image. Binary font/image outputs were
compared byte-for-byte with their Bower sources. The ported shell/htmx Django suite
passed **24 tests on each runtime**, Python 3.13 (dev) and Python 3.10.12 (production),
both with Django 5.2.11. Coverage includes assets, explicit HTTP/WSGI mounts,
account/schema resolution, fragments/history, and missing-token/untrusted-origin rejection.

The complete browser suite passed **16 tests through Caddy HTTPS and 16 through
Apache HTTP**, with no skips or retries: seeded search/filter/sort/history/detail,
login/logout/protected registration, native forms, enhanced interactions, error
recovery and browser/bot/API/static routing. Desktop 1440px and mobile 390px
screenshots were inspected: blue header, correct logo, readable controls, no overflow.
Both complete browser suites and both 24-test Django suites were repeated after
moving the integration into the durable workspace checkout. A sandbox-blocked
Chromium launch was excluded; browser verification ran with explicit approval.

Two proxy issues were fixed and regression-tested: Caddy TLS termination needs an
explicit CSRF trusted origin; Apache's internal SPA rewrite lost the search
noindex header. The latter now checks the original request with a conditional
[Header directive](https://httpd.apache.org/docs/2.4/mod/mod_headers.html#header).
Apache merges User-Agent variation instead of overwriting fragment Vary headers.

Actual rollback was exercised on both proxies by removing only the isolated HTML
mount, verifying SPA ownership and unchanged `/api/env/`, and restoring the mount.
No canonical feature route was cut over. Real ORCID authorization/email delivery
and legacy Rendertron deployment remain explicit prerequisites for later auth and
cutover changes, not claims made by this infrastructure refresh.

## Run and verify

Run these commands from the preserved `develop-migration/` checkout, not the old
parent worktree. The fixture account is local-only and has no production access.

```sh
docker compose -f compose.refresh.json up -d mysql elasticsearch backend caddy apache
docker compose -f compose.refresh.json exec -T backend python manage.py test elixirapp.test_html elixirapp.test_htmx
docker compose -f compose.refresh.json exec -T apache python manage.py test elixirapp.test_html elixirapp.test_htmx
cd tests/browser
BIOTOOLS_BASE_URL=http://localhost:8003 BIOTOOLS_TEST_HTML_SHELL=1 \
BIOTOOLS_TEST_TOOL_ID=migration-fixture BIOTOOLS_TEST_QUERY=Migration \
BIOTOOLS_TEST_USERNAME=migration-test BIOTOOLS_TEST_PASSWORD=Migration-test-only-2026 \
PLAYWRIGHT_BROWSERS_PATH=/tmp/biotools-playwright npm test
```

For Caddy use `BIOTOOLS_BASE_URL=https://localhost:8443 BIOTOOLS_TEST_LOCAL_TLS=1`;
the opt-in accepts only the local test certificate in the browser harness and does
not change application TLS validation. Browser traces may contain credentials;
keep them local, ignored and access-restricted. Node 22+, the locked npm packages,
Bower assets and installed Playwright Chromium are required. The legacy Dockerfile
still declares Node 11; the build repair retains Gulp 5 and uses its supported APIs.

For a fresh disposable database, run migrations, grant the test user database
creation privileges, build frontend-modern and collect static assets before testing.
`tests/browser/seed.py` runs under `manage.py shell` with
`BIOTOOLS_ALLOW_TEST_SEED=biotools-refresh` and `BIOTOOLS_TEST_PASSWORD` supplied.
It refuses existing records/indexes and uses the normal registration endpoint and
production index-generation command, bounded to two indexing workers. The older
API fixture mapping cannot support browser name sorting and must not replace it.
API tests and browser fixture setup must run serially because upstream tests mutate
index state. Recreate disposable fixtures after an API run; never purge a shared index.

Preview: `http://localhost:8003/` is the develop registry with one test record;
`http://localhost:8003/_migration/html/preview/` is the migrated HTML interaction.
The old `localhost:8001` preview is not this checkout. Stop this stack with
`docker compose -f compose.refresh.json stop`; volumes remain available for resuming.

For rollback, remove the HTML WSGIScriptAlias from Apache, or the two HTML path
patterns from Caddy's `@django` matcher, and reload that proxy. Preserve the API
mount, collected assets and database. Reapply the mount to restore the preview.
Production Apache config is baked into its image, so rebuild the image after
editing `backend/runtime/apache.conf`; an in-container reload alone is temporary.
