# migrated-browser-authentication Specification

## Purpose
Preserve secure browser sessions, account flows and public API authentication.
## Requirements
### Requirement: Develop account flows remain supported
Browser migration SHALL preserve supported dj-rest-auth/allauth registration, password recovery, ORCID login/connect and social-account listing/disconnection behavior from the pinned develop baseline. Provider-dependent validation SHALL distinguish deterministic local tests from configured-provider integration evidence.

#### Scenario: Existing account recovery link is opened
- **WHEN** a user follows a supported password reset-confirmation URL after migration
- **THEN** the uid/token validation and recovery flow remain available without SPA fallback interception

#### Scenario: ORCID account linking is used
- **WHEN** a user invokes a supported ORCID login, connection or disconnection flow
- **THEN** the existing identity and permission checks remain enforced and unsupported account access is rejected

### Requirement: Migrated protected pages enforce authentication on the server
The system SHALL enforce authentication and authorization for protected migrated pages and mutations on the server rather than relying only on client-side visibility or routing logic.

#### Scenario: Unauthenticated user requests a protected migrated page
- **WHEN** an unauthenticated user requests a page that requires authentication
- **THEN** the server follows the configured authentication flow without rendering privileged page data

### Requirement: Session-authenticated mutations enforce CSRF protection
All session-authenticated mutations issued by migrated ordinary forms, htmx or Vue clients SHALL require valid CSRF protection according to Django security policy.

#### Scenario: Vue mutation without valid CSRF protection
- **WHEN** an authenticated browser submits a Vue-initiated mutation without valid CSRF credentials
- **THEN** the server rejects the mutation without changing application data

### Requirement: Expired browser sessions fail predictably
Migrated browser interfaces SHALL surface an expired or invalid session in a recoverable manner appropriate to the request type.

#### Scenario: Session expires during a Vue mutation
- **WHEN** a user's session has expired before a Vue mutation is processed
- **THEN** the mutation is not applied and the workspace receives an explicit authentication failure that can lead the user back to sign-in

#### Scenario: Session expires during an htmx request
- **WHEN** a user's session has expired before a protected htmx request is processed
- **THEN** the page receives a predictable authentication response and does not replace the target with an unrelated login document fragment

### Requirement: Supported external API authentication remains compatible
Browser-authentication migration SHALL NOT remove or silently change authentication mechanisms currently supported for external public API clients unless separately specified.

#### Scenario: Existing authenticated API client
- **WHEN** an external client uses a supported pre-migration authentication mechanism for the public API
- **THEN** the request continues to be authenticated according to the compatible public API contract

