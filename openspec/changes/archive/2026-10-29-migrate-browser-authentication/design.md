## Context

The target architecture favors Django-owned browser authentication and server permissions. Vue should receive only the minimum session/user/CSRF context required for requests; it should not become the authority for permissions.

## Goals / Non-Goals

**Goals:**
- One documented browser authentication model for migrated pages.
- Consistent CSRF for normal, htmx and Vue mutations.
- Predictable expired-session handling.
- External API compatibility.

**Non-Goals:**
- Replacing all identity providers.
- Introducing JWT merely because a package exists.
- Rewriting registration/social/password-reset flows unless required for the migrated login path.

## Decisions

### Trace actual runtime behavior first

Document which installed auth packages/middleware/endpoints are active for browser sessions and API clients. Select the migrated strategy based on current supported requirements, not dependency names.

### Prefer server-side session authority for browser pages when compatible

Django owns user identity, permissions and CSRF. Vue/htmx receive appropriate 401/403/redirect semantics and display a recoverable sign-in path.

### Preserve API client mechanisms

Do not remove token/JWT/other mechanisms currently supported for external clients as a side effect of browser migration.

## Risks / Trade-offs

- **Risk: mixing redirect HTML with JSON consumers** -> Define response behavior by endpoint/request class and test both Vue and htmx session expiry.
- **Risk: CSRF bypass added for convenience** -> No blanket exemptions for migrated session-authenticated mutations.
- **Risk: external clients break** -> Contract tests for supported API auth remain unchanged.

## Migration Plan

Enable migrated login/protected behavior on migration routes first. Canonical route ownership changes later and remains reversible.
