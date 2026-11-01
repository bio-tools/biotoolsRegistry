## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Trace current authentication

- [x] 1.1 Identify actual login/logout/registration/password-reset/social-login routes, middleware/backends and browser credential storage used by the current frontend.
- [x] 1.2 Identify supported external API authentication mechanisms and add/locate contract tests before changing browser behavior.
- [x] 1.3 Document CSRF/CORS/session behavior relevant to Django forms, htmx and Vue requests.
- [x] 1.4 Trace develop's dj-rest-auth/allauth registration, reset-confirmation, ORCID login/connect and social-account listing/disconnection; retain active DRF token authentication rather than assuming installed JWT support is active.

## 2. Implement migrated browser auth

- [x] 2.1 Add/reuse Django-rendered login and logout behavior for migrated routes using the compatible existing authentication backend.
- [x] 2.2 Add server-side protected-page/permission enforcement independent of Vue visibility logic.
- [x] 2.3 Define one CSRF request helper/convention for Vue mutations and verify htmx mutations use the same server protection.
- [x] 2.4 Implement predictable expired-session behavior for normal navigation, htmx fragment requests and Vue JSON mutations.

## 3. Test security behavior

- [x] 3.1 Test valid login, invalid login, logout and unauthorized protected-page access.
- [x] 3.2 Test mutation with missing/invalid CSRF token for both htmx and Vue request styles.
- [x] 3.3 Test session expiry during htmx and Vue requests and verify a recoverable authentication path.
- [x] 3.4 Run external API authentication contract tests and verify supported mechanisms remain compatible.
- [x] 3.5 Test recovery tokens and account-link permissions with deterministic fixtures; record configured ORCID/provider checks separately and leave unavailable integration evidence pending.

## 4. Document and verify

- [x] 4.1 Document the active browser-authentication mechanism and distinguish it from external API authentication.
- [x] 4.2 Verify no sensitive long-lived credential was introduced into localStorage or similarly exposed browser storage.

## Completion evidence

Completed 2026-09-22 on pinned develop `9faec5b3b660498fdef9736e65e331728b55f99c`
in the isolated `develop-migration/` checkout. See the
[authentication contract, route review and evidence](../../../../docs/frontend-migration/browser-authentication.md).
Type-check/build pass; 63 frontend tests, 92 backend tests per runtime and 42
browser tests per proxy pass. Native, htmx and Vue requests retain CSRF protection,
expiry recovery preserves inputs, and existing external token API contracts pass.
Configured ORCID login/connect/callback verification is explicitly PENDING because
provider credentials are unavailable; deterministic token/ownership tests pass.
Canonical route cutover, resource editing and production hardening are not included.
