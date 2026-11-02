# Frontend runtime specification

## Purpose
Maintain accessible, secure and testable Django, htmx and Vue delivery.

## Requirements
### Requirement: Server rendering is progressively enhanced
The system SHALL serve complete pages and essential native forms through Django, with htmx and explicitly mounted Vue islands enhancing supported interactions.

#### Scenario: JavaScript or an asset fails
- **WHEN** an interactive asset is unavailable
- **THEN** essential navigation and native fallbacks remain usable and failures are visible

### Requirement: Shared assets and data survive deployment changes
Deployment SHALL preserve public static, schema, media, admin and API routes and SHALL NOT require the retired AngularJS, Bower, Gulp or Rendertron services.

#### Scenario: The production image starts
- **WHEN** the native image is built and run
- **THEN** Django, Apache and the built frontend serve the application without a legacy frontend container

### Requirement: Interfaces are accessible and safe
The system SHALL support keyboard navigation, responsive layouts, safe rendering of server-provided data, CSRF-protected mutations and clear recovery for failed requests. Vue island lifecycle SHALL remain correct after htmx fragment replacement.

#### Scenario: A request fails
- **WHEN** an enhanced interaction fails or times out
- **THEN** the error is visible and unsaved user input is preserved

### Requirement: Regression tests use disposable data
The project SHALL exercise backend, frontend and browser behavior using isolated fixtures and preserve persistent database, index and media data during rehearsals.

#### Scenario: A write test runs
- **WHEN** a test creates or changes records
- **THEN** it uses an explicitly disposable environment and does not modify production data
