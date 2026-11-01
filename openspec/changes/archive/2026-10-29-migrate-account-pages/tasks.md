## 1. Contract

- [x] 1.1 Review audit B01/B08 and enumerate canonical/nested/email/provider URLs and current account policy fixtures on the pinned develop implementation.
- [x] 1.2 Specify permanent helper URLs and profile-to-management links; record Apache/Caddy routing and rollback boundaries.

## 2. Implementation

- [x] 2.1 Implement session-backed native login/signup/verification/recovery forms and safe return navigation with existing allauth/dj-rest-auth policy.
- [x] 2.2 Implement profile, password/email changes, verification resend and connected-account management without issuing browser API tokens.
- [x] 2.3 Implement server-side ORCID login/connect/callback handling and permanent session helpers; retain compatibility aliases during coexistence.
- [x] 2.4 Update canonical routing, navigation, generated email URLs and all Vue/htmx helper callers without removing the retained-page bridge.

## 3. Verification

- [x] 3.1 Add backend tests for authorization, CSRF, tokens, session expiry, safe redirects, provider error/state paths and external API authentication isolation.
- [x] 3.2 Run native/no-JavaScript and enhanced account journeys, deep links and rollback through both proxies; record live-provider tests separately from fixtures.
- [x] 3.3 Update route ownership and audit dispositions; record evidence and remaining configured-provider/email readiness gates.

Completed 2026-10-15 in `develop-migration/`. Evidence and limitations:
`docs/frontend-migration/account-pages.md`. Live ORCID/email delivery and
production approval remain readiness gates, not completed local tests.
