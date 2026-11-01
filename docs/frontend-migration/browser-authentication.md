# Migrated browser authentication

Implemented on the completed develop-refresh baseline
`9faec5b3b660498fdef9736e65e331728b55f99c`, verified 2026-09-22.
Runtime changes live in `develop-migration/`, not the historical application tree.
Canonical routes and the legacy account workflows have not been cut over.

## Develop account review

Reviewed `elixirapp/settings.py`, `elixirapp/urls.py`, `elixir/views.py`,
`elixir/adapters.py`, the user serializers, installed dj-rest-auth/allauth views
and serializers, recovery email templates, and AngularJS `djangoAuth.js`,
`orcidService.js`, controllers and routes.

- The API's configured authentication class is DRF `TokenAuthentication`.
  Clients send `Authorization: Token ...`. Installed SimpleJWT is not active:
  `USE_JWT=False`. A session cookie alone does not authorize the token API.
- dj-rest-auth has `SESSION_LOGIN=True`, so legacy token login also starts a
  Django session. With the session bridge disabled, AngularJS stores its API
  token in `localStorage.token`; the opt-in bridge below replaces that transport.
- Django uses ModelBackend and allauth AuthenticationBackend. Active middleware
  includes sessions, CSRF, authentication and allauth account middleware; the
  obsolete `MIDDLEWARE_CLASSES` setting is not the active pipeline.
- Username/email login and optional email verification are the current policy.
  The new form reuses the configured dj-rest-auth login serializer, including
  inactive-user and mandatory-verification checks, without issuing an API token.
- Existing `/api/rest-auth/` login, logout, user, registration, verify-email,
  resend-email, password reset/confirmation, ORCID login/connect and social-account
  list/disconnect routes remain unchanged, as do `/api/accounts/` and `/api/schema/`.
- Password-reset emails still target the legacy
  `reset-password/confirm?uid=...&token=...` page, which submits to the API.
  The allauth UID is base36 despite the URL argument's `uidb64` name. The API
  `password/reset/confirm/<uid>/<token>/` is POST-only; GET returns JSON 405,
  not a replacement SPA page. Registration still issues a token and sends email.
- Legacy ORCID uses sessionStorage for callback state and the intended route,
  validates state, and exchanges a code through the existing API. The custom
  social adapter's matching-email and authenticated-connect linking behavior
  is untouched. Local permission tests do not establish provider identity safety.

## Session browser contract

Preview: http://localhost:8003/_migration/html/auth/login/

The isolated HTML mount now provides `auth/login/`, POST-only `auth/logout/`,
protected `account/`, GET `auth/session/`, and POST `auth/check/`. The account
page shows the current user's identity and a session check; it is not a profile
or resource editor. Its check writes only a timestamp into the Django session.
Login, logout and the check work without JavaScript. Existing blue branding is
retained. Django validates login's `next` URL and rotates session/CSRF state.

`browser_login_required` enforces the session server-side. An API token header
cannot grant access to these views, and account data always comes from
`request.user`, not a client-selected identity. Protected responses are no-store.

| Request | Missing/expired session | Authenticated CSRF rejection |
| --- | --- | --- |
| Ordinary navigation/form | Redirect to login with a safe return destination | HTML 403 |
| htmx | Empty 401 with `X-Login-URL`; no login-document swap or automatic redirect | Empty 403 with `X-CSRF-Failed` |
| Vue JSON | JSON 401, `authentication_required`, `loginUrl` | JSON 403, `csrf_failed` |

Deliberate htmx logout returns `HX-Redirect` after clearing the session. Expiry
does not: the page and unsaved inputs stay in place. Sign-in opens another tab;
explicit Reconnect obtains fresh masked CSRF credentials. A different account
is rejected when the page has an existing user identity. Failed mutations are
never automatically replayed; the user retries after reconnecting.

`frontend-modern/src/browser-auth.ts` is the shared JSON request helper and
htmx convention. It reads the masked template CSRF meta value, adds
`X-CSRFToken` for unsafe methods, uses same-origin cookies, refuses API
Authorization headers and cross-origin/credential-bearing URLs, and rejects
redirected fetches. Recovery refreshes the meta value and native hidden CSRF
inputs. Forms retain `{% csrf_token %}` and Django middleware checks remain
enabled; there are no CSRF exemptions. The custom failure view changes only
isolated HTML responses, not API behavior. See Django's
[CSRF guidance](https://docs.djangoproject.com/en/5.2/howto/csrf/) and
[authentication views](https://docs.djangoproject.com/en/5.2/topics/auth/default/).

No new long-lived credential is stored in localStorage or sessionStorage.
htmx stores only `htmx-current-path-for-history`; history snapshots remain disabled.
The session cookie is HttpOnly and SameSite=Lax. The development CSRF cookie is
SameSite=Lax; both cookies currently have Secure=False for local HTTP previews.
Caddy's existing wildcard CORS header does not enable credentialed cross-origin
requests; the helper is same-origin only. Local Caddy's HTTPS origin is trusted
explicitly for CSRF in `compose.refresh.json`.

**Logout scope:** migrated logout clears the Django session, not external API
tokens. With the session bridge enabled, retained pages use that same session,
discard stale localStorage tokens and share logout state. With it disabled,
retained pages still require token login. Public API logout retains its existing
token-revocation behavior. Registration, recovery and ORCID keep their existing pages.

## Retained-page session bridge

`BIOTOOLS_BROWSER_SESSION_BRIDGE=1` enables the bridge in both backend runtimes.
Normal development/production Compose defaults it to `0`; the disposable refresh
stack defaults it to `1`. Build the existing Angular scripts when deploying it.

Angular checks the no-store `/api/browser-session/` configuration once per page
load, then routes same-origin `/api/` requests to `/_migration/html/api/` when
enabled. Configuration failure fails closed; reload to retry. Stale browser tokens
are discarded, Authorization is removed and Angular's native CSRF-cookie support
reads the current token for unsafe requests. There is no token-to-session exchange:
an old token-only browser without a live session must sign in again.

The isolated Django dispatcher resolves existing DRF views, retains their
serializers/permissions, and selects SessionAuthentication only for this mount.
Its outer Django view is not CSRF-exempt: login, signup and recovery require CSRF
too. Mixed Authorization/session credentials are rejected. Login, registration,
ORCID login/connect reuse the existing policy without issuing browser API tokens;
logout ends only the session. Non-DRF account/admin/static views are not dispatched.
Verification/recovery email URLs retain the public `/api` URL configuration.
The external API still rejects session-only authentication.

Rollback, without changing detail/search switches:

```sh
BIOTOOLS_BROWSER_SESSION_BRIDGE=0 docker compose -f compose.refresh.json up -d --no-deps backend apache caddy
```

Reload retained pages and sign in again using the legacy token flow. The isolated
session API now returns 404. Migrated session pages remain available. Re-enable
with `BIOTOOLS_BROWSER_SESSION_BRIDGE=1` and recreate the same services.
The transport switch alone does not cut over any canonical URL. When the editor
switch is also enabled, turning the bridge off restores legacy editor/request
ownership too. Recreate Caddy as well so its routing agrees with the backend.
`/login`, signup, recovery, profile and ORCID handlers remain legacy-owned.

Verified on 2026-10-11/12: both Python runtimes pass 147 migration tests, and
Apache/Caddy each pass all 30 focused ownership/authentication/editor browser
checks. Transport rollback and restoration each pass two authentication checks
per proxy, including public token API isolation and browser credential storage.
The preview is restored to bridge-enabled mode. See the
[route evidence](route-ownership.md#ownership-and-session-verification-2026-10-1112)
for artifacts and remaining canonical-route/provider gates.

The 2026-10-12 to 2026-10-14 editor/request cutover subsequently passes 152 backend
tests on both runtimes and 40 focused browser checks on each proxy. Editor-only
and bridge-disabled rollback each pass four checks per proxy; restoration passes
six. Canonical login, signup, recovery, profile and ORCID handlers remain unchanged.
See [canonical editor verification](route-ownership.md#canonical-editor-and-request-verification-2026-10-12-to-2026-10-14).

## Verification and limits

- Frontend type-check and production build passed; **63 unit tests passed**,
  including seven authentication-helper/component tests. Build: JS 186.96 kB
  (57.03 kB gzip), CSS 7.70 kB (1.89 kB gzip). No dependency was added.
- **92 migration backend tests passed on both Python 3.13 and Apache/Python 3.10**,
  including 13 new authentication tests. Coverage includes CSRF/origin rejection,
  session expiry, email/username and policy checks, safe redirects, logout,
  supported token API behavior, unsupported JWT/session-only API access, reset
  token validity/expiry/replay, registration, and social-account ownership.
- Deterministic tests use isolated users, sessions, local email and social-account
  fixtures. Existing resource tests mock enrichment writes; live search tests use
  test indices. No registry records are changed by the browser-auth workflow.
- Browser verification includes login/error/logout at 1440px and 390px, no-JS
  forms, Vue/htmx expiry, retained annotation input, second-tab sign-in,
  reconnection, CSRF rejection, storage checks, and recovery-route isolation.
  Screenshots were visually inspected; layout checks assert no horizontal overflow.
  **All 42 browser tests passed on Apache and Caddy**, with no skips or automatic
  retries. The initial Caddy run timed out on every route; a direct HTTPS check
  subsequently returned 200 and a fresh full run passed without code changes.
  The transient timeout's cause was not established. Final ignored artifacts are
  `test-results-browser-auth-apache-full/` and
  `test-results-browser-auth-caddy-verified/` under `tests/browser/`.
- Existing MySQL conditional-constraint, naive-date, deprecated allauth setting,
  unordered social-list pagination and htmx build warnings remain.

| Provider evidence | Status |
| --- | --- |
| ORCID routes resolve to existing login/connect views | Passed locally |
| Anonymous connect denied; missing provider credentials rejected | Passed locally, no provider call |
| Own social accounts listed/disconnected; foreign disconnect rejected | Passed with deterministic fixtures |
| Configured ORCID login, callback/state, connection and provider identity matching | **PENDING: no configured ORCID credentials; no live provider exchange attempted** |

Before production cutover, validate configured ORCID login/connect/callback and
account linking with controlled provider accounts. Also review deployment
secrets, allowed hosts, HTTPS/proxy trust, Secure cookies and login throttling.
Existing permissive development settings and the social linking policy were not
hardened by this change. Passing local tests is not production deployment approval.

The later resource editor must use session-protected browser endpoints with
server-side resource permissions. Do not send cookies to the token API and assume
they authorize resource writes, or copy the legacy token into the Vue workspace.

## Reproduce

From the develop checkout with its disposable database and test fixtures:

```sh
docker compose -f compose.refresh.json exec -T backend python manage.py test elixirapp.test_browser_auth --noinput --keepdb
```

Repeat with `apache` for Python 3.10. In `frontend-modern/`, run
`npm run type-check`, `npm test`, and `npm run build`. Refresh collected static
assets and restart Apache after backend changes. The backend test discovery and
existing modern frontend CI include these tests.

In `tests/browser/`, set the dedicated fixture username/password in the environment:

```sh
BIOTOOLS_BASE_URL=http://localhost:8003 BIOTOOLS_TEST_BROWSER_AUTH=1 npm test -- browser-auth.spec.js
```

For Caddy use `https://localhost:8443` and `BIOTOOLS_TEST_LOCAL_TLS=1` only for the
local self-signed certificate. Set `PLAYWRIGHT_BROWSERS_PATH` consistently with the
Chromium installation when using a custom cache. Enable the other documented
suite flags for full regression coverage. Traces can contain credentials and
private responses: keep ignored test artifacts private, never commit them.
