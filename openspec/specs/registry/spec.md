# Registry specification

## Purpose
Provide searchable, directly accessible registry records and account journeys.

## Requirements
### Requirement: Public routes and API remain compatible
The system SHALL provide server-rendered public pages, tool details, supported aliases, redirects and the existing public REST API.

#### Scenario: Direct navigation
- **WHEN** a user or crawler opens a valid tool or public-page URL directly
- **THEN** the server returns the corresponding complete page without requiring JavaScript

### Requirement: Search state is authoritative and reproducible
The system SHALL preserve supported filters, sorting and pagination in URLs and apply server-scoped filters to the complete result set. Candidate-local filters SHALL be clearly scoped to loaded results.
Advanced conditions SHALL use declared fields and operators, not executable user expressions; derived-score filters SHALL identify their definition or version.

#### Scenario: Search state changes
- **WHEN** a user changes filters or navigates Back, Forward or reloads
- **THEN** results reflect the URL and stale asynchronous responses cannot replace newer results

### Requirement: EDAM selection uses stable concepts
The system SHALL support scoped, keyboard-accessible EDAM lookup and retain concept URIs through selection and storage.

#### Scenario: Vocabulary changes
- **WHEN** a term label changes for an existing concept
- **THEN** stored annotations retain the stable URI and can display the updated label

### Requirement: Account and API authentication stay separate
The system SHALL provide native account journeys with server-side authorization, CSRF-protected browser mutations and compatible token-authenticated public API access.

#### Scenario: Session expires
- **WHEN** an authenticated browser session expires during work
- **THEN** the user receives a recoverable authentication response without exposing API credentials or silently losing the draft
