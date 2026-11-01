## Scope

Cover /login, /signup and success/verification children, /reset-password and
confirmation/success children, /profile and /orcid/callback/. Preserve uid/token
query links and verification keys already sent by email. Profile includes account
information, password/email changes, resend verification, connected accounts,
owned/shared resources and navigation to migrated requests.

## Decisions

- Extend existing browser_auth and installed account policy, not a second identity
  system. Native forms remain usable without JavaScript; htmx is optional.
- Keep provider secrets, state validation and callback processing server-side.
  Reuse installed allauth behavior, preserve login-versus-connect intent and
  enforce safe local return URLs. Do not expose API tokens to browser storage.
- Authorize every private profile/action on the server. Preserve the existing
  verification and last-usable-login-method rules; model permission fixtures
  before implementation rather than copying UI conditions as policy.
- Move session/login/logout helpers used by Vue/htmx to permanent browser routes.
  Keep old helper links working during transition; do not remove the legacy
  bridge while retained Angular consumers remain.
- Do not duplicate delete/disown or permission editing. Profile resource lists
  link to the management change's actions when available.

## Implementation Policy Clarifications

Native ORCID connections require an explicit authenticated, state-bound connect
flow. They do not inherit the legacy adapter's implicit email-based linking:
matching a provider email alone must not authenticate as an existing account.
Existing connections still sign in; public API/legacy branches are unchanged.
New reset emails retain the old uid/token query URL so unread messages survive
rollback. See `docs/frontend-migration/account-pages.md` for the route contract
and in-flight flow limitations.

## Verification and Rollback

Test native, htmx and enhanced return paths through Apache and Caddy; verification
and recovery valid/expired/reused tokens; failed/expired sessions; CSRF; account
enumeration-safe errors; provider cancellation/state mismatch/account conflict;
connect/disconnect permission checks and unchanged external token APIs.
Deterministic provider tests do not count as live ORCID verification: the configured
provider/email rehearsal belongs to production readiness.
Rehearse reversible route ownership while legacy still exists, including callback
and email URLs. Never roll back by invalidating unrelated API tokens.

## Non-Goals

No new identity providers, user-role model or redesign of public REST endpoints.
