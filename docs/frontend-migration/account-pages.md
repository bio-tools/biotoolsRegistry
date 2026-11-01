# Native account pages

Baseline: pinned develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
Runtime implementation lives only in `develop-migration/`. This is a disposable
local rehearsal, not a production deployment.

## Routes and compatibility

| Route | Native owner / behavior |
| --- | --- |
| `/login` | Existing session-only credential form; safe local `next`, no API token issuance. |
| `/signup`, `/signup/success` | Installed allauth registration; required email and existing registry username validation. |
| `/signup/verify-email/<key>`, `/signup/verify-email/success` | Existing allauth verification tokens and configured confirmation policy. |
| `/reset-password`, `/reset-password/sent/` | Native recovery form and generic acknowledgement for known/unknown addresses. |
| `/reset-password/confirm?uid=...&token=...` | Compatible old email link; redirects to allauth's native token validation route. |
| `/reset-password/key/<uid>-<token>/`, `/reset-password/confirm/success` | Token validation, session-bound clean reset form and completion. |
| `/profile` | Account details, verification status, connected identities, owned/shared tools and requests. |
| `/profile/email/`, `/profile/email/resend/` | Current serializer's email-update policy; explicit verification resend, POST only. |
| `/profile/password/`, `/profile/password/set/` | Installed password-change/set forms and session preservation. |
| `/profile/connections/` | Installed disconnect form, scoped to the current user; retains last usable login method. |
| `/auth/orcid/login/`, `/auth/orcid/connect/` | CSRF-protected POST initiation, provider secrets and state kept server-side. |
| `/orcid/callback/` | Installed OAuth callback and state validation; unconfigured provider fails locally with 503. |
| `/auth/orcid/signup/`, `/auth/orcid/cancelled/`, `/auth/orcid/error/` | Native provider completion/failure pages. |
| `/auth/session/`, `/auth/check/`, `/auth/logout/` | Permanent recovery GET, CSRF-protected check POST and logout POST. |
| `/auth/inactive/`, `/auth/reauthenticate/` | Native allauth account-policy support pages. |

Canonical Django templates and server-generated editor/htmx recovery responses
reverse the permanent helpers automatically. Existing `/_migration/html/`
helpers remain working aliases in their original isolated URL configuration.
The session bridge remains in use by retained Angular consumers; public
`/api/*` token authentication does not accept browser sessions.

Account forms work without JavaScript. Optional htmx logout and Vue editor
reconnection use the existing session recovery protocol. Retained navigation
enters canonical account routes via a document request; `_legacy=1` remains an
explicit escape hatch. Disown is still linked to `/profile?_legacy=1` pending
`migrate-record-and-domain-management`; it was not silently removed or duplicated.

## Policy and security

- Login reuses the existing dj-rest-auth serializer without creating a token.
  Signup, reset, password changes and disconnect reuse installed allauth forms.
- Email changes use the existing serializer: update the primary address, clear
  verification, then offer resend. Duplicate/unchanged addresses produce a
  generic form error. Changes run atomically.
- All mutations require CSRF; private profile forms require the authenticated
  user. Logout does not delete unrelated public API tokens.
- Native ORCID login never automatically links an existing user by matching email.
  An existing connection can sign in; a new connection requires an authenticated
  connect flow bound to the initiating user's ID and provider state. Changing
  users mid-flow, replay, forged state and foreign account ownership are rejected.
  This intentionally avoids the legacy adapter's implicit email-based linking.
  The legacy/API adapter branch is unchanged during coexistence.
- Personalized responses are private/no-store and noindex. Account responses
  use `Referrer-Policy: same-origin`: account URLs are not sent to external sites,
  while same-origin browser forms retain the origin/referrer needed for CSRF.
- Newly generated reset emails retain the old uid/token query-link format so
  unread email survives a route rollback. Verification links retain their old
  canonical key format. The native reset handler removes the token from the form
  URL using allauth's existing session-bound reset flow.

## Activation and rollback

`BIOTOOLS_CUTOVER_ACCOUNTS=1` selects these routes before crawler handling in
Apache/Caddy and before generic tool-ID matching in Django. Account ownership
is independent of detail/search/editor and session-bridge switches. Normal
Compose defaults to `0`; only the disposable refresh stack defaults to `1`.

From `develop-migration/`:

```sh
BIOTOOLS_CUTOVER_ACCOUNTS=0 docker compose -f compose.refresh.json up -d --no-deps backend apache caddy
BIOTOOLS_CUTOVER_ACCOUNTS=1 docker compose -f compose.refresh.json up -d --no-deps backend apache caddy
```

Recreate all three services so their environment switches agree. No database
rollback or token invalidation is needed. After a rollback, reload account forms
and restart any in-flight ORCID/reset flow; already-open native forms are not
portable to the legacy handler. Old and newly issued email entry links still
use the shared canonical formats.

Build retained scripts and collect modern static assets before verification.
Do not rebuild/restart during a browser run. The existing isolated preview and
external REST endpoints remain available throughout coexistence.

## Verification

Backend tests: `elixirapp.test_account_pages`, alongside existing authentication,
bridge, cutover, editor, request and query tests. Provider responses are mocked
at the OAuth exchange boundary; they are not live ORCID verification.

Browser tests: `tests/browser/account-pages.spec.js`, plus existing auth,
browser-auth, canonical-editor, ownership-session, resource-editor and cutover
suites. Set `BIOTOOLS_TEST_ACCOUNTS=1`, disposable credentials, and
`BIOTOOLS_TEST_EDITOR_WRITES=1` for signup/email/password mutation cases.
For rollback ownership checks set `BIOTOOLS_EXPECT_ACCOUNTS=0` and run
`account-pages.spec.js --grep 'route ownership'`. Run through both Apache
(`http://localhost:8003`) and Caddy (`https://localhost:8443`, local TLS opt-in).
Artifacts stay local: traces may contain session data and must not be published.

### Local evidence (2026-10-15)

- All 167 migration backend tests pass on both Python 3.13 and Apache's Python
  3.10 runtime, with disposable Elasticsearch checks enabled and no skips.
- All 43 focused account/auth/cutover/editor/request browser checks pass through
  each proxy with no retries or skips. Artifacts:
  `tests/browser/test-results-accounts-regression-{apache,caddy}/`.
- The nine account checks include desktop/mobile layouts, JavaScript-disabled
  forms, actual disposable signup/email/password changes, legacy navigation,
  recovery errors, unavailable provider and unchanged public API isolation.
- Desktop/mobile profile screenshots were inspected: blue registry branding,
  readable controls and no horizontal overflow or overlapping content.
- All 87 modern unit tests and type-checking pass. Modern source/bundles are
  unchanged; retained scripts were rebuilt and shell styles collected.
- Apache/Caddy configuration validation passes. Existing MySQL conditional-
  constraint and runtime warnings remain; no database migration or new dependency.

Browser verification caught and fixed same-origin form rejection caused by an
overly restrictive referrer policy, and search literals shadowed by the tool-ID
matcher in the combined URL configuration. Focused backend tests also cover
email save-time conflicts and provider-email collisions without implicit linking.

Account-only rollback passes five checks through each proxy: browser/crawler
ownership, nested email/provider entry paths, retained login/logout and protected
registration, independent editor ownership, search/detail and API/static isolation.
Artifacts: `test-results-accounts-rollback-{apache,caddy}/`. The first Apache
crawler request failed because Rendertron briefly could not reach the recreated
Apache container; a fresh run after connectivity recovered passed all five.
Allow services and renderer-origin connectivity to settle before acceptance checks.

After restoring the switch, three smoke checks per proxy pass for native
ownership, mobile sign-in/profile/sign-out and retained navigation. Artifacts:
`test-results-accounts-restored-{apache,caddy}/`. The preview is left enabled at
`http://localhost:8003/profile` and `https://localhost:8443/profile`.
All 25 OpenSpec changes pass strict validation; planning/evidence mirrors agree.

## Remaining deployment gates

Real ORCID exchange requires configured credentials and the registered canonical
callback URL. Real verification/reset delivery requires configured email transport.
Neither external service is certified by fixtures or the console-mail preview.
Production cookie/TLS/origin policy, rate-limit storage, security review and
deployment approval belong to `verify-production-migration-readiness`.
Public pages, management actions and search/editor fallbacks still need Angular;
this change does not authorize deleting the legacy frontend.

