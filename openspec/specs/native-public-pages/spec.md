# native-public-pages Specification

## Purpose
Provide native public information, domain-directory and statistics pages.
## Requirements
### Requirement: Public routes are server owned
The system SHALL serve supported home, information, community, domain-directory and statistics routes without an AngularJS runtime.

#### Scenario: Direct public deep link
- **WHEN** a visitor opens or refreshes a supported public route with JavaScript disabled
- **THEN** Django returns useful content and working navigation including domain-search links

#### Scenario: Literal route collision
- **WHEN** a request matches a reserved public route name
- **THEN** the public route takes precedence over generic tool-detail matching

### Requirement: Public redirects and errors are explicit
The system SHALL preserve documented schema and outbound redirect routes as server responses and return genuine error statuses for missing pages.

#### Scenario: Schema or documentation shortcut
- **WHEN** a visitor requests an existing supported shortcut
- **THEN** the server returns the documented redirect to its reviewed destination without loading the SPA

#### Scenario: Missing page
- **WHEN** a visitor or crawler requests an unknown route
- **THEN** the response uses the appropriate not-found status and native error page

### Requirement: Statistics preserve data meaning
The system SHALL render the existing supported statistics datasets with accessible values and distinct empty and unavailable states.

#### Scenario: Statistics data available
- **WHEN** the existing statistics sources return data
- **THEN** the page shows the corresponding measures and visual summaries without invented values

#### Scenario: Statistics source unavailable
- **WHEN** a required statistics source fails
- **THEN** the page identifies unavailable data rather than presenting it as zero

### Requirement: Public content and assets survive retirement
The system SHALL use retained assets for public content and supply route-appropriate browser/crawler metadata through both supported proxies.

#### Scenario: Retained public assets
- **WHEN** the legacy frontend service is absent from the final acceptance stack
- **THEN** public logos, content images and navigation still render from the retained asset pipeline

#### Scenario: Crawler request
- **WHEN** a crawler requests a migrated public page through Apache or Caddy
- **THEN** it receives meaningful native content and the documented indexing policy without needing Rendertron

