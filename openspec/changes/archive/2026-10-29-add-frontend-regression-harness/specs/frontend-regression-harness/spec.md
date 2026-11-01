## Purpose

Provide framework-independent browser regression coverage that can validate both the legacy frontend and migrated Django/htmx/Vue implementations.

## ADDED Requirements

### Requirement: Browser regression tests are implementation-independent
The regression harness SHALL test user-visible behavior without depending on AngularJS-specific controllers, scopes or internal implementation objects.

#### Scenario: Frontend framework changes
- **WHEN** a legacy route is replaced by a migrated implementation with equivalent user-visible behavior
- **THEN** the same browser regression scenario can be executed without rewriting it solely because the frontend framework changed

### Requirement: The harness supports configurable deployment targets
The browser regression harness SHALL support running against a configurable base URL so the same suite can exercise local, production-like or deployed environments where fixtures permit.

#### Scenario: Developer selects a local target
- **WHEN** the documented base-URL configuration points to a locally running stack
- **THEN** the browser suite executes against that target without source-code changes

### Requirement: Critical public discovery workflows are covered
The regression suite SHALL cover the core public discovery flow including search, at least one filter, result navigation, a tool-detail deep link and relevant URL/history behavior.

#### Scenario: Stateful search regression
- **WHEN** the test performs a text search and applies a supported filter or ordering control
- **THEN** it verifies the visible result state and the URL state needed to reproduce that search

#### Scenario: Tool detail deep link regression
- **WHEN** the test opens a representative tool-detail URL directly
- **THEN** the page loads successfully without requiring prior navigation through the search interface

### Requirement: Browser history behavior is regression-tested
The regression suite SHALL verify refresh and Back/Forward behavior for representative stateful search URLs.

#### Scenario: Navigate backward after changing search state
- **WHEN** a user changes result-defining search state and then activates browser Back
- **THEN** the tested application restores the state represented by the previous URL

### Requirement: Authentication coverage is included when deterministic fixtures exist
The regression suite SHALL test representative login, logout and protected-route behavior when deterministic credentials or fixtures are available, and SHALL document the blocker when they are not.

#### Scenario: Authentication fixture is available
- **WHEN** the test environment provides deterministic authentication fixtures
- **THEN** the suite verifies successful login, logout and denial or redirection for a representative protected route

#### Scenario: Authentication fixture is unavailable
- **WHEN** deterministic authentication cannot be established in the supported test environment
- **THEN** the limitation and required prerequisite are documented rather than replaced with an unreliable test

### Requirement: Failures produce actionable diagnostics
The browser harness SHALL preserve useful diagnostics for failed scenarios, including at least screenshots or traces and relevant console/network information where supported by the selected tooling.

#### Scenario: Browser test fails
- **WHEN** a browser regression scenario fails in local or CI execution
- **THEN** the configured test artifacts provide enough context to identify the failing page and interaction without relying only on a terminal assertion message

### Requirement: Regression infrastructure does not intentionally change product behavior
The harness change SHALL NOT alter production behavior solely to make tests pass.

#### Scenario: Stable selector is needed
- **WHEN** accessible role, label or semantic selectors are insufficient for a reliable browser test
- **THEN** a narrowly scoped stable test selector may be added without changing the product interaction semantics
