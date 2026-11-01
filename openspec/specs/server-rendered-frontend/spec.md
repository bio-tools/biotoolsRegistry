# server-rendered-frontend Specification

## Purpose
Provide a Django-owned HTML presentation layer that coexists with remaining legacy routes.
## Requirements
### Requirement: Shell routing works through both develop deployment paths
The isolated Django HTML shell SHALL resolve through Caddy/runserver in development and Apache/WSGI in production while preserving API, account, static and non-migrated legacy routing. Browser and crawler requests SHALL reach the intended owner without inappropriate Rendertron or SPA interception.

#### Scenario: Shell is requested through either proxy
- **WHEN** a browser or crawler requests the isolated shell through either supported deployment path
- **THEN** the complete page, static assets and reversed links resolve correctly and unrelated route ownership remains unchanged

### Requirement: Django can render complete browser pages
The system SHALL be able to serve complete HTML pages from Django without requiring the legacy AngularJS application to render page content.

#### Scenario: Direct request to a migrated test page
- **WHEN** a browser requests a route assigned to the Django-rendered frontend
- **THEN** the server returns a complete HTML document with the page content and standard site shell

### Requirement: New page routing remains isolated during migration
The system SHALL keep existing public REST API routes and non-migrated legacy frontend routes operational while the new Django-rendered frontend is introduced.

#### Scenario: Existing API route during shell introduction
- **WHEN** a client requests an existing public API endpoint after the Django HTML shell is added
- **THEN** the endpoint continues to resolve with its pre-migration API behavior

#### Scenario: Existing legacy route during shell introduction
- **WHEN** a browser requests a route that has not been explicitly migrated
- **THEN** the route continues to be served by the legacy frontend owner

### Requirement: Server-rendered pages support standard browser semantics
Django-rendered pages SHALL provide semantic HTML, conventional links/forms and server-generated error responses suitable for direct navigation and refresh.

#### Scenario: Direct refresh
- **WHEN** a user refreshes a Django-owned page URL
- **THEN** the server renders the requested page directly without requiring prior client-side navigation state

