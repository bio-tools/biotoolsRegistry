## Purpose

Provide reusable server-side Python query services for tool retrieval and search so public API views and migrated browser views share authoritative behavior without internal HTTP calls.

## ADDED Requirements

### Requirement: Tool retrieval is available through a shared Python service
The backend SHALL expose a reusable Python-level service for retrieving a tool by its supported identifier while preserving visibility and not-found semantics required by existing callers.

#### Scenario: Existing tool is retrieved
- **WHEN** server-side code requests a visible existing tool through the shared retrieval service
- **THEN** the service returns the domain/query result needed by the caller without serializing it through the public REST API

#### Scenario: Tool is not available to the caller
- **WHEN** a requested tool is missing or not visible under the applicable rules
- **THEN** the service returns or raises a documented domain-level outcome that callers can map to their own presentation or API response

### Requirement: Tool search is available through a shared Python service
The backend SHALL expose a reusable Python-level search service with explicit query, filtering, ordering and bounded pagination or cursor inputs needed by current search behavior.

#### Scenario: Representative search is executed
- **WHEN** server-side code submits supported search text, filters and pagination to the shared service
- **THEN** the service returns the authoritative bounded result set and metadata without requiring an HTTP request to the application's own API

### Requirement: Public REST API compatibility is preserved
Refactoring public API views to use shared query services SHALL preserve supported response fields, status codes, filtering semantics and pagination behavior unless a separate approved specification explicitly changes them.

#### Scenario: Existing public tool-detail request
- **WHEN** an external client performs a supported tool-detail request after the refactor
- **THEN** it receives a response compatible with the pre-refactor public API contract

#### Scenario: Existing public search request
- **WHEN** an external client performs a supported search request after the refactor
- **THEN** query interpretation, supported filters, pagination and response representation remain compatible with the pre-refactor behavior

### Requirement: Serialization remains outside the shared query service
The shared query service SHALL return domain/query results rather than coupling its core behavior to a specific HTML or REST serialization format.

#### Scenario: Same service is used by API and HTML callers
- **WHEN** a DRF view and a Django-rendered or frontend-oriented view use the same query service
- **THEN** each caller can construct its own response representation without duplicating the underlying retrieval or search logic

### Requirement: Server code does not call the local application API over HTTP for shared operations
Django server-side code SHALL NOT call localhost or the deployed public REST endpoint over HTTP to perform tool retrieval or search when the shared Python service can provide the same operation.

#### Scenario: Migrated Django view needs tool search
- **WHEN** a migrated server-side view needs an authoritative tool search
- **THEN** it invokes the shared Python query service directly rather than issuing an internal HTTP request

### Requirement: Shared services avoid obvious duplicate backend work
The refactor SHALL NOT introduce avoidable duplicate database or Elasticsearch requests for representative tool-detail and search operations.

#### Scenario: Representative request is regression-tested
- **WHEN** query-count or Elasticsearch-request instrumentation is applied to a representative detail or search case
- **THEN** the refactored path does not perform duplicated retrieval caused solely by the new service abstraction
