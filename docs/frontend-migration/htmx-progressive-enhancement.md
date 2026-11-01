# htmx progressive enhancement

Baseline note: this document describes the old `a1fc8b9` worktree.
The port has since passed develop revalidation; use the
[current develop runbook](develop-refresh.md#run-and-verify) for startup, both
proxy mounts, verification and rollback. The instructions below remain historical.

`/_migration/html/preview/` is a read-only, non-domain message preview. It exercises
the migration infrastructure without changing search, authentication, registry
data, API routing or the legacy frontend build. The shell links to it.

## Request and template convention

- Complete pages live in `backend/templates/html/<page>.html` and extend `html/base.html`.
- Swappable HTML lives in `html/fragments/<page>.html`. A complete page includes the same fragment, whose single root has a stable target ID.
- `elixirapp.html.is_htmx(request)` selects fragments only for `HX-Request: true`, excluding history-restoration requests. This header is a rendering hint, never authorization.
- Compute and validate state once in the view. Only template selection varies. Send `Vary: HX-Request, HX-History-Restore-Request` so caches cannot serve fragments as full pages.
- Use ordinary `action`/`method` or `href` alongside the htmx attribute. The preview uses a Django form for required/max-length validation and normal template escaping. Invalid GETs return HTTP 400 with form errors; successful requests return 200. POST is not allowed here.

## Shared behavior

The [modern package](../../frontend-modern/README.md) pins and locally bundles
htmx 2.0.10. The base template includes its manifest-selected module only on
Django-owned pages. No global link boosting or legacy-page inclusion is added.

Set `hx-indicator` to a server-owned status element with `htmx-indicator`, and
`hx-disabled-elt` to the submitting controls. CSS reserves indicator space; htmx
restores controls after completion. The base page's persistent `request-error`
alert handles HTTP, network, timeout and swap errors. The failed fragment is not
inserted, the existing state remains available, and the user can correct/retry
or follow the reload link. Requests time out after 10 seconds. A new request
clears the old alert. Native browser submissions render full error pages/forms.

Result-defining GET forms use `hx-push-url="true"`. The URL contains the same
parameters as the ordinary form, so refresh and direct links reproduce state.
History snapshots are disabled (`historyCacheSize = 0`), and history misses use
a normal page reload (`refreshOnHistoryMiss = true`). This intentionally trades
instant Back/Forward for complete canonical pages without persisting potentially
private HTML in localStorage. History-restoration requests always receive full
pages even if an HX header is present.

Keep Django session, authentication, authorization and CSRF middleware active.
Future enhanced POST forms must retain `method="post"`, `action` and
`{% csrf_token %}`: htmx submits the hidden token with the form, and Django checks
it just as for ordinary submission. Do not exempt views, use GET for mutations,
or infer a logged-in session from a legacy API token. A valid token does not
replace authorization. This change adds no mutation interaction; the existing
native session-check form remains unchanged. Tests additionally prove that an
HX header cannot bypass its CSRF rejection. Authenticated domain mutations need
account-backed authorization and CSRF regression tests when introduced.

## DOM ownership

htmx owns only Django-rendered fragments. Targets MUST NOT point inside a mounted
Vue-owned root, and Vue must not mount inside an independently swappable htmx
fragment without coordinated lifecycle handling. If a future swap contains whole
Vue roots, lifecycle infrastructure must unmount them before replacement and
mount their replacements afterward. Until that infrastructure exists, do not
swap containers containing mounted Vue roots. No Vue runtime or speculative
lifecycle hooks are added here. See the [ownership ADR](adr-001-frontend-ownership.md).

## Verification

```sh
cd frontend-modern
npm ci
npm run build
cd ../backend
python manage.py test elixirapp.test_html elixirapp.test_htmx --verbosity 2
python manage.py collectstatic --noinput
cd ../tests/browser
BIOTOOLS_BASE_URL=http://localhost:8000 BIOTOOLS_TEST_HTML_SHELL=1 npm test -- shell.spec.js htmx.spec.js
```

No registry seed or test account is needed for these focused checks. The modern
build must be present for the enhanced browser cases. The backend asset test
explicitly skips when it is absent; the other tests still exercise native HTML.

The browser cases cover desktop/mobile swaps, unchanged outer DOM, canonical
Back/Forward and refresh, visible loading, server/network/validation errors and retry, and
ordinary GET navigation with JavaScript disabled or its bundle unavailable.
See [htmx documentation](https://htmx.org/docs/) for the underlying attributes
and events. To roll back enhancement only, remove the base `modern_script`
include; normal forms and the Django shell remain functional.

## Validation record

Validated on 2026-09-10 with Python 3.8.20, Django 3.1.2, Node 22.23.2,
Vite 8.2.2, Playwright 1.63.0 and Chromium 153.0.8010.12:

- All 21 focused Django tests passed with the assets built, without database creation.
- `npm ci --offline --cache /tmp/biotools-npm-cache` and `npm run build` passed. The unchanged entry produced the same hash on rebuild. No type/lint commands exist in the modern package.
- `collectstatic --noinput` copied the manifest and hashed entry to a temporary static root; the collected manifest matched its source. Tracked legacy collected assets were left untouched.
- The seven focused browser scenarios passed twice (14 passes, zero retries). Desktop/mobile screenshots were inspected for readable controls, logo rendering, layout and overflow.
- Strict OpenSpec validation and whitespace checks passed.

Browser checks use the actual Django HTML/API WSGI entry points through a temporary
loopback dispatcher at `http://127.0.0.1:8001`, not Apache. No MySQL/Elasticsearch
stack or Apache/mod_wsgi is available here, so live proxy integration, the full
database-dependent backend suite and seeded legacy discovery were not rerun.
The existing route-isolation tests passed; no legacy route/build files changed
in this change. Before deployment, run the documented provisioned-stack workflow.

Initial browser failures exposed an exact-label selector mismatch (Django appends
a colon) and a test run overlapping a Vite rebuild. The selector was corrected;
the repeated passing run used completed assets without concurrent rebuilds.

The temporary Python environment, Chromium installation and preview server were
recreated after they disappeared from `/tmp`. All 108 backend packages passed
`uv pip check`; the legacy source builds used build-only constraints
`setuptools==57.5.0` and `Cython<3`, without changing project requirements.
Final verification includes the real validation-error browser assertion and
session-section spacing adjustment: all 21 Django tests and 14 browser runs
passed (9.5 seconds, zero retries). The Vite build, collection of 174 static
files, collected-manifest comparison and strict OpenSpec validation also passed.
The final desktop/mobile screenshots were inspected. Task 4.3 is complete;
the provisioned-stack limitations above still apply.
