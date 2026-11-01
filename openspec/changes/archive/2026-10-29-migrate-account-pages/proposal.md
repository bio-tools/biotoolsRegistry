## Baseline

Target: upstream develop pinned at `9faec5b3b660498fdef9736e65e331728b55f99c`, implemented only in `develop-migration/`. Review the current migration work on top of that baseline, not the older outer runtime.
See the [dependency audit](../../../../docs/frontend-migration/legacy-removal-audit.md) and [finishing sequence](../../../README.md#finishing-sequence).

## Why

Canonical account pages still require AngularJS although session authentication already exists. Completing the pages is necessary to retire the legacy frontend without breaking account recovery, profile management or ORCID.

## What Changes

- Replace canonical login, signup, email verification, password recovery and profile pages with Django forms and optional htmx.
- Preserve password/email changes, verification resend, connected ORCID accounts and owned/shared resource lists.
- Give production session helpers stable URLs and preserve safe return destinations, existing email links and provider callbacks.
- Reuse existing allauth/dj-rest-auth policy and the session-only browser contract; keep external token API behavior unchanged.

## Dependencies

Depends on completed `migrate-browser-authentication` and `cut-over-migrated-routes`. Record disown is owned by `migrate-record-and-domain-management`; keep its link to the retained implementation until that change lands.

## Capabilities

### New Capabilities

- `native-account-pages`: Native canonical account, recovery, profile and ORCID pages reuse the browser session contract.

### Modified Capabilities

None. Existing completed migration contracts remain in force; this change closes the remaining scope rather than reopening their historical acceptance.

## Impact

Django account views/forms/templates/URLs, account email-link construction, shared browser-auth helper URLs, both proxies, navigation and account/browser/API regression fixtures. Audit B01 and the auth portion of B08.
