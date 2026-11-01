## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

The backend includes multiple authentication-related mechanisms, and installed packages do not prove which flows are active. Migrated browser pages need one explicit session/CSRF strategy that works for ordinary forms, htmx and Vue mutations without breaking external API clients.

## What Changes

- Trace and document current browser and external-client authentication flows before editing.
- Implement migrated browser login/logout/protected-page behavior using the existing compatible session/authentication foundation.
- Ensure htmx and Vue mutations handle CSRF and expired sessions predictably.
- Preserve supported external public API authentication behavior.
- Do not store sensitive long-lived credentials in unsafe browser storage.

## Capabilities

### New Capabilities

- `migrated-browser-authentication`: Users can authenticate to Django/htmx/Vue migrated interfaces with server-enforced session, permission and CSRF behavior while external API authentication remains compatible.

### Modified Capabilities

None.

## Impact

Authentication views/templates/middleware/frontend request helpers and tests may change. Security-sensitive; existing auth flows must be traced rather than inferred from dependencies.
