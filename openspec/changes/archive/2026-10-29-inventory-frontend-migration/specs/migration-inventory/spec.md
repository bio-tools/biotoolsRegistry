## Purpose

Establish a complete, evidence-based baseline of legacy frontend behavior and explicit architectural ownership rules before runtime migration begins.

## ADDED Requirements

### Requirement: Legacy user-facing routes are inventoried
The migration documentation SHALL enumerate every known user-facing legacy frontend route and record the implementation elements and behavior needed to migrate it safely.

#### Scenario: Route is implemented by the legacy frontend
- **WHEN** a route is present in frontend routing configuration or is reachable through user-facing navigation
- **THEN** the migration inventory records the route, its controller/component/directive/template chain where identifiable, relevant URL state, authentication requirements and mutable actions

#### Scenario: Route behavior is uncertain
- **WHEN** a route or behavior cannot be determined confidently from repository evidence
- **THEN** the inventory marks the uncertainty explicitly rather than inferring undocumented behavior

### Requirement: Frontend API usage is mapped to features
The migration documentation SHALL map observed frontend API requests to the routes or features that issue them and record relevant client-side payload or response transformations.

#### Scenario: Frontend service calls an API endpoint
- **WHEN** repository code contains a frontend request to a backend endpoint
- **THEN** the API-usage inventory identifies the caller, endpoint, feature context and any material transformation or validation performed around the request

### Requirement: Search and editor behavior are documented separately
The migration baseline SHALL describe current search-state behavior and resource-editor behavior in sufficient detail to derive regression tests and later implementation specifications.

#### Scenario: Search behavior affects reproducibility
- **WHEN** a search interaction changes query, filters, sorting, pagination, result display or browser history
- **THEN** the search inventory records how that state is represented and restored in the legacy implementation

#### Scenario: Editor behavior can alter submitted resource data
- **WHEN** the legacy editor validates, normalizes, reorders, defaults or transforms nested resource data before submission
- **THEN** the editor inventory records the behavior and the repository evidence supporting it

### Requirement: Frontend ownership boundaries are explicit
The migration architecture SHALL define which layer owns top-level routes, htmx-managed fragments, Vue-managed DOM regions, public API compatibility and migration cutover decisions.

#### Scenario: Complex search workspace is classified
- **WHEN** the architecture classifies the future search-results experience
- **THEN** Django owns the route and server authority, Vue owns the cohesive search workspace subtree, and htmx is prohibited from mutating DOM inside that Vue-owned subtree

#### Scenario: Complex resource editor is classified
- **WHEN** the architecture classifies the future resource editor
- **THEN** Django owns the page, permissions and server authority while Vue owns the complex editor subtree and htmx does not mutate inside it

### Requirement: Migration risks are evidence-based
The migration documentation SHALL maintain a risk register for behavior that is untested, ambiguous, security-sensitive, performance-sensitive or capable of causing data loss.

#### Scenario: High-risk undocumented behavior is found
- **WHEN** repository inspection finds important behavior without reliable regression coverage or clear semantics
- **THEN** the risk register records the evidence, uncertainty, potential impact and proposed validation or regression coverage

### Requirement: Inventory work does not alter runtime behavior
The inventory change SHALL NOT intentionally modify application runtime behavior.

#### Scenario: Inventory change is reviewed
- **WHEN** the change is ready for completion
- **THEN** runtime application code has not been changed except for documentation-only references that cannot alter execution
