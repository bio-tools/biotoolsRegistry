## Purpose

Canonical account pages still require AngularJS although session authentication already exists. Completing the pages is necessary to retire the legacy frontend without breaking account recovery, profile management or ORCID.

## ADDED Requirements

### Requirement: Canonical account journeys are native
The system SHALL serve the supported canonical account pages and nested email/recovery links without AngularJS, using the existing account verification policy.

#### Scenario: Email link opened directly
- **WHEN** a user opens a valid verification or recovery link previously issued by the registry
- **THEN** the native page completes the existing policy-controlled flow and preserves a safe return destination

#### Scenario: Invalid or reused token
- **WHEN** a user submits an expired, invalid or consumed account token
- **THEN** the native page reports a safe failure without changing credentials or requiring AngularJS

### Requirement: Profile and account mutations preserve policy
The system SHALL expose current profile, password/email, verification resend and connected-account functionality using authenticated server-side authorization and CSRF-protected mutations.

#### Scenario: Profile without JavaScript
- **WHEN** an authenticated user opens /profile with JavaScript disabled
- **THEN** account information and native account forms work and owned/shared resource links remain available

#### Scenario: Forged or expired mutation
- **WHEN** a profile mutation lacks valid authentication or CSRF protection
- **THEN** the server rejects it without altering account data

### Requirement: ORCID callbacks preserve login and connection boundaries
The system SHALL validate provider state and callback intent server-side and enforce existing account connection and disconnection rules without exposing provider secrets or browser API tokens.

#### Scenario: Mismatched provider state
- **WHEN** an ORCID callback has missing or mismatched state
- **THEN** the server rejects the callback without signing in or linking an account

#### Scenario: Connecting an existing account
- **WHEN** an authenticated user completes an allowed ORCID connection
- **THEN** the connection applies to the authorized account and returns to a safe local page

### Requirement: Browser and API authentication remain separate
The system SHALL provide stable browser session helper URLs while preserving public token API authentication and transition compatibility.

#### Scenario: External token client
- **WHEN** an external client uses a supported public API token after account-page cutover
- **THEN** its authentication contract is unchanged

#### Scenario: Expired enhanced request
- **WHEN** a Vue or htmx request encounters an expired browser session
- **THEN** the existing recovery protocol uses the permanent login/session URLs without losing an editor draft
