# Django HTML shell

Baseline note: this document describes the old `a1fc8b9` worktree.
The port has since passed develop revalidation; use the
[current develop runbook](develop-refresh.md#run-and-verify) for startup, both
proxy mounts, verification and rollback. The instructions below remain historical.

The initial browser route is `/_migration/html/`. It is a migration preview, not a
replacement for the home page, search, tool detail or authentication workflows.
It has ordinary navigation/search links and a CSRF-protected session-check form
that adds a one-time message without modifying registry data. No JavaScript is required.
The subsequent [htmx enhancement](htmx-progressive-enhancement.md) adds a linked
GET preview and an optional modern bundle; build it before the backend image to
enable enhanced interactions. Native shell behavior remains available without it.

## Ownership and implementation

| Public path | Owner |
| --- | --- |
| `/api` and `/api/...` | Existing `elixirapp.wsgi` application and `elixirapp.urls`; unchanged API views, authentication and negotiation. |
| `/_migration/html` and `/_migration/html/...` | `elixirapp.html_wsgi`, with the request URLconf set to `elixirapp.html_urls`. |
| Other browser routes | Existing Apache document root and AngularJS fallback. |
| `/static/html/...` | Django-collected shell assets, served as files by Apache. |

The two-segment prefix avoids taking over a valid tool ID or its `/edit` route.
The HTML WSGI entry point adds an internal environment marker; the routing middleware
uses it to select the HTML URLconf. An HTTP header cannot set this marker. Both entry
points share the existing settings and middleware; the API URLconf is not modified.
The middleware runs before CommonMiddleware so slash/error resolution also uses the
correct URLconf. `SCRIPT_NAME` remains intact, so Django reverses form actions to the
mounted path instead of accidentally posting to the API or the SPA.

This uses Django's [request-specific URLconf](https://docs.djangoproject.com/en/3.2/topics/http/urls/)
and the existing Apache [WSGIScriptAlias](https://www.modwsgi.org/en/latest/configuration-directives/WSGIScriptAlias.html)
mounting convention. No proxy rule transfers a production route to Django HTML.

## Templates, assets and errors

- Extend `backend/templates/html/base.html`; override `title`, `extra_head`, `navigation`, `content` and `footer` as needed.
- Templates use semantic landmarks, escaped Django messages, native links/forms and `{% csrf_token %}` for POST forms. Do not introduce SPA globals or client-side authentication assumptions.
- Add shell assets beneath `backend/elixir/static/html/` and reference them using `{% static %}`. The logo is reused from the existing bio.tools asset. There is no Bower/Gulp dependency.
- Use the current upstream branding: blue header/border (`#005472`), white navigation and the white bio.tools wordmark. The local fork at `a1fc8b9` still contains orange navigation in both its source and built CSS; it is not the branding reference. The blue color comes from [upstream navigation CSS](https://github.com/bio-tools/biotoolsRegistry/blob/master/frontend/components/navigationBar/navigationBar.css), and `html/biotools-white.svg` is an unchanged copy of [upstream's logo](https://github.com/bio-tools/biotoolsRegistry/blob/main/frontend/img/biotools_white.svg) (Git blob `1dac441d67f623eba25b5c0dc250ca3217704300`). Keep Bootstrap blue links/primary controls (`#337ab7`) and neutral gray text/borders; green is reserved for success feedback.
- `html/404.html` and `html/500.html` are registered only on the HTML URLconf. API and legacy error handling remain unchanged. Django uses these handlers with `DEBUG=False`; with `DEBUG=True`, its normal technical error pages take precedence.
- The 500 renderer deliberately omits the request context so database-backed authentication/session context cannot cause a second failure. Keep the base/error templates free of required user state, database lookups and exception details. A broken template engine/static storage is outside this fallback's scope.
- Browser authentication migration is still pending. The preview does not treat a legacy localStorage API token as a Django session or provide a new login flow.

## Development stack

Use the existing [installation workflow](../../INSTALL.md). From the repository root,
on a provisioned development database/index:

```sh
docker compose build backend
docker compose up -d mysql elasticsearch backend
docker compose exec backend python manage.py collectstatic --noinput
```

Open `http://localhost:8000/_migration/html/`. Rebuild/recreate the backend when changing
the Apache configuration: it is copied into the image, not bind-mounted. For Python-only
changes, use the existing Apache reload command:

```sh
docker compose exec backend /etc/init.d/apache2 reload
```

`collectstatic` uses the existing `STATIC_ROOT` (by default
`/elixir/application/frontend/static/`) and `STATIC_URL` (`/static/`). Serve that directory
at the configured static URL in deployments using a different web server. Regenerate
assets after editing CSS; do not hand-edit collected copies. This repository already
tracks collected third-party assets; review any generated changes rather than committing
unrelated replacements. No frontend container/build is needed for the shell itself.

The preview does not query MySQL or Elasticsearch for anonymous rendering or its short
cookie-backed message. The existing application still needs its Python dependencies and
normal deployment configuration to initialize. The shell adds no database migration
or Python package; the optional htmx enhancement has its own modern npm package.

## Verification

```sh
docker compose exec backend python manage.py test elixirapp.test_html --verbosity 2
```

These are database-free `SimpleTestCase` checks using the actual project settings and
API URLconf. They cover templates, context, status codes, CSRF rejection/success, one-time
messages, error handlers, static discovery, mounted reverse URLs, API views and the
Apache route-ownership contract. They do not replace a live Apache integration check.

After installing the [browser harness](../../tests/browser/README.md):

```sh
cd tests/browser
BIOTOOLS_BASE_URL=http://localhost:8000 BIOTOOLS_TEST_HTML_SHELL=1 npm test -- shell.spec.js
```

The browser checks run at desktop/mobile sizes with JavaScript disabled, submit the
CSRF form, refresh the page, and attach screenshots. They need no seeded tool or account.
They are opt-in so the public discovery harness still runs against legacy deployments.

## Rollback

Remove the `/_migration/html` WSGIScriptAlias and rebuild/recreate the backend. Existing
API and SPA routing do not depend on the shell. Its middleware, templates and assets can
then be removed separately; no data migration or reversal is needed.

## Validation record

Validated on 2026-09-09:

- All 13 Django tests passed using Python 3.8.20 and the pinned Django 3.1.2. Django reported no system-check issues and skipped database creation because the tests need no database.
- The existing requirements were installed in an isolated `/tmp` environment. Legacy source distributions required build-only constraints `setuptools==57.5.0` and `Cython<3`; project requirements were not changed. `uv pip check` reported all 108 installed packages compatible.
- `collectstatic --noinput` copied 172 files to a temporary static root. The collected CSS and logo matched their sources; tracked legacy assets were not regenerated.
- The two opt-in Playwright tests passed at 1440x1000 and 390x844 with JavaScript disabled. Screenshots were inspected, including the colour logo, non-overlapping navigation, forms, footer and successful message. CSRF form submission and refresh worked at the mounted URL.
- Browser validation used a temporary loopback WSGI server at `http://127.0.0.1:8001/_migration/html/`, dispatching to the actual HTML/API WSGI entry points and serving static assets and the existing frontend. It is a local preview, not a deployment replacement.
- Strict OpenSpec validation and `git diff --check` passed.

No Docker stack was provisioned, and Apache/mod_wsgi was unavailable on the host.
The Apache configuration's mount/fallback contract is tested, but live Apache rewriting
and the full MySQL/Elasticsearch application remain environment-limited checks. Run the
documented Docker workflow before deployment. The local preview is useful for the shell;
the linked legacy data workflows still require the normal backend services and seed data.
