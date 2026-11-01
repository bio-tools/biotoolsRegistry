## Purpose

Allow simple Django-owned browser interactions to update server-rendered fragments efficiently while preserving conventional navigation and form behavior where feasible.

## ADDED Requirements

### Requirement: Server-rendered interactions can be progressively enhanced
The system SHALL allow designated Django-rendered interactions to return a targeted HTML fragment for an htmx request while retaining a complete-page response for the corresponding normal browser request where the interaction is meaningful without JavaScript.

#### Scenario: Enhanced request
- **WHEN** an htmx-enabled interaction requests updated server-rendered content
- **THEN** the server returns the fragment required by the declared target without an unnecessary complete page wrapper

#### Scenario: Normal browser request
- **WHEN** the same interaction is requested without the htmx request context and a direct form/navigation fallback exists
- **THEN** the server returns a complete page representing the same resulting application state

### Requirement: Result-defining navigation can update browser history
An htmx interaction that changes a shareable page state SHALL update browser history when the resulting state has a canonical URL.

#### Scenario: User navigates backward after an enhanced state change
- **WHEN** an htmx interaction changed canonical page state and the user activates browser Back
- **THEN** the browser returns to the previous canonical state rather than an unrelated or blank fragment state

### Requirement: Server mutations enforce CSRF protection
Session-authenticated htmx mutations SHALL be subject to the same CSRF protection as ordinary Django form submissions.

#### Scenario: Mutation without a valid CSRF token
- **WHEN** a session-authenticated htmx mutation is submitted without a valid CSRF token
- **THEN** the server rejects the mutation without changing application data

### Requirement: Interaction failures remain visible and recoverable
The system SHALL present a user-visible error or fallback when an enhanced request fails rather than silently leaving the page in an indeterminate state.

#### Scenario: Fragment request fails
- **WHEN** an htmx request fails because of a server or validation error
- **THEN** the user receives a visible failure state and can retry or navigate without reloading an invalid partial document
