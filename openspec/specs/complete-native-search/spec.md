# complete-native-search Specification

## Purpose
Preserve supported search filters and URLs in native and enhanced search.
## Requirements
### Requirement: Supported search URLs retain their meaning
The system SHALL interpret supported legacy search parameters and aliases through the shared query service without silently dropping or broadening constraints.

#### Scenario: Domain and ontology bookmark
- **WHEN** a user opens a supported bookmarked query combining a domain with EDAM identifier constraints
- **THEN** native search returns the characterized matching resource set without redirecting to AngularJS

#### Scenario: Repeated or invalid parameters
- **WHEN** a query contains repeated keys or invalid values
- **THEN** supported repetition follows the documented compatibility matrix and unsupported input produces an actionable error instead of disappearing

### Requirement: Native and enhanced search share a contract
The system SHALL provide usable server-rendered GET search results and pagination when JavaScript or modern assets are unavailable.

#### Scenario: Unavailable JavaScript
- **WHEN** a user submits a native search form with JavaScript disabled
- **THEN** the response contains matching resources, active constraints and working pagination without a legacy frontend

#### Scenario: Backend search failure
- **WHEN** the search backend fails or returns incomplete results
- **THEN** native and enhanced views show a recoverable error rather than a misleading empty or complete result set

### Requirement: Search state and filter scope are preserved
The system SHALL preserve supported URL state across navigation while distinguishing candidate-local filters from full-registry filtering.

#### Scenario: History navigation
- **WHEN** a user changes filters, sorting or pagination and uses Back or Forward
- **THEN** the visible state and results match the restored URL

#### Scenario: Promoted filter
- **WHEN** a user promotes a supported candidate-local filter to full-set search
- **THEN** the server applies it to the full query and produces a reproducible URL

### Requirement: Parity is evidence-backed
The system SHALL maintain a compatibility matrix linking supported filters and result workflows to backend and browser tests, with explicit approval for any intended retirement.

#### Scenario: Previously declared but nonfunctional parameter
- **WHEN** characterization cannot establish a working legacy behavior
- **THEN** the matrix records the limitation and agreed disposition rather than claiming successful parity

#### Scenario: External API use
- **WHEN** the frontend parity implementation is deployed
- **THEN** supported public API search representations remain compatible

