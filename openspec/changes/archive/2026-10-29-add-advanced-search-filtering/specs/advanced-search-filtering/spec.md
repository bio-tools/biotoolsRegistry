## Purpose

Enable extensive post-search filtering and analytical exploration while keeping complete-result semantics authoritative on the server and bounded exploratory state responsive in the browser.

## ADDED Requirements

### Requirement: Advanced filters use validated structured conditions
The system SHALL represent advanced result filters as validated structured conditions over supported fields and operators rather than executable user-provided expressions.

#### Scenario: Unsupported filter field or operator
- **WHEN** a client submits an advanced filter using a field or operator that is not declared as supported
- **THEN** the server rejects or ignores it according to the documented validation contract without executing arbitrary code

### Requirement: Candidate-local filtering is explicitly scoped
When a filter is applied only to a bounded client-side candidate set, the workspace SHALL identify that scope and SHALL NOT present candidate-only counts as authoritative counts for all server matches.

#### Scenario: Local threshold over a partial candidate set
- **WHEN** the server query has more matches than are present in the browser candidate set and a local threshold filter is applied
- **THEN** the workspace indicates that the filter/count applies to the candidate set rather than all matches

### Requirement: Supported advanced filters can be applied authoritatively to the complete result set
The system SHALL provide a server-authoritative execution path for advanced filters that are declared server-capable so that complete-result counts, navigation and exports can use equivalent semantics.

#### Scenario: Promote a candidate filter to full-set refinement
- **WHEN** a user requests full-set application of a server-capable filter currently used for local exploration
- **THEN** the backend applies the validated filter to the complete matching result set and returns authoritative count/navigation metadata

### Requirement: Result-defining advanced filters are reproducible
Advanced filters that affect the server-authoritative result set SHALL be represented in canonical URL state or by a stable server-side saved-filter/search identifier referenced from the URL.

#### Scenario: Reopen an advanced filtered search
- **WHEN** a user opens a canonical URL or saved-search link containing advanced server filter state
- **THEN** the workspace reconstructs an equivalent authoritative filtered search

### Requirement: Derived numeric scores can be filtered without fixing one scoring model
The search contract SHALL allow optional backend-declared numeric derived-score fields to expose enough identity metadata for the workspace to filter them reproducibly without assuming a specific score algorithm.

#### Scenario: Versioned derived score
- **WHEN** search results expose a derived numeric score whose definition can change between model or rule versions
- **THEN** the score metadata identifies the relevant definition/version sufficiently for saved or shared threshold state to retain its intended meaning

### Requirement: Analytical extensions share search state
Selection, comparison or visualization features that change or interpret visible results SHALL consume the same structured search/filter state rather than maintaining an independent conflicting result identity.

#### Scenario: Visualization applies a supported filter
- **WHEN** an analytical panel applies a result-defining supported filter
- **THEN** the active filter state, visible results and canonical server search state update through the same search-state mechanism
