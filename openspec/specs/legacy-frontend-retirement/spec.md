# legacy-frontend-retirement Specification

## Purpose
TBD - created by archiving change remove-legacy-angularjs-frontend. Update Purpose after archive.
## Requirements
### Requirement: Legacy frontend removal is dependency-gated
The change SHALL audit the release candidate's routes, runtime paths, build steps, proxy rules and CI requirements, and replace or retain every identified dependency before removing its source. The user authorized source removal before separately completing production checks.

#### Scenario: Active dependency remains
- **WHEN** the removal audit finds an active dependency on legacy frontend source, assets, services or build outputs
- **THEN** destructive removal stops and the dependency is documented as a blocker

#### Scenario: Audit finds no active dependencies
- **WHEN** the route-ownership record and repository/deployment audit confirm that the legacy frontend is unused
- **THEN** removal may proceed and the audit records how each historical dependency was retired or replaced

### Requirement: Legacy AngularJS build/runtime dependencies are removed after migration
Once the dependency gate is satisfied, the repository SHALL remove AngularJS application runtime dependencies and obsolete Bower/Gulp configuration that serve only the retired frontend.

#### Scenario: Legacy source is retired
- **WHEN** the cleanup change completes successfully
- **THEN** no production runtime or build path requires AngularJS, Bower or legacy Gulp configuration

### Requirement: Deployment no longer requires the legacy frontend service
After retirement, local and production-like deployment SHALL operate without a dedicated legacy frontend container, obsolete mounts/volumes or SPA fallback rules used only by AngularJS.

#### Scenario: Production-like stack starts after cleanup
- **WHEN** the documented production-like stack is built and started after legacy removal
- **THEN** Django, htmx and Vue/Vite assets serve the migrated application without starting a legacy frontend service

### Requirement: Modern frontend and API behavior are preserved
Removing legacy infrastructure SHALL preserve migrated browser routes, the modern Vue/Vite asset pipeline and supported public REST API behavior.

#### Scenario: Browser regression suite after removal
- **WHEN** the complete browser regression suite runs against the cleaned stack
- **THEN** migrated search, detail, authentication and editing workflows continue to satisfy their approved requirements

#### Scenario: Existing API client after removal
- **WHEN** an external client uses a supported public REST API endpoint after legacy frontend retirement
- **THEN** the endpoint remains available independently of the removed browser frontend stack

### Requirement: Obsolete CI and documentation are removed or updated
The retirement change SHALL remove CI jobs, caches, artifacts and documentation that apply only to the retired frontend, while retaining commands and documentation for the Django + htmx + Vue/Vite architecture.

#### Scenario: Contributor follows setup documentation
- **WHEN** a contributor follows the documented setup after legacy removal
- **THEN** the instructions do not require Bower, AngularJS, legacy Gulp or a retired frontend container

### Requirement: Shared non-legacy assets and data are retained
The retirement change SHALL classify assets co-located with the old frontend and preserve required public content, schema/reference resources, Django/admin/API static assets and media, without deleting database, index or media data volumes.

#### Scenario: Collected static assets share the legacy directory
- **WHEN** the old frontend directory or mount is retired
- **THEN** required static content is served from its verified replacement location and API/admin/content asset requests continue to work

#### Scenario: Compose cleanup
- **WHEN** obsolete legacy service and volume declarations are removed
- **THEN** persistent database, index and media data are preserved and cleanup does not purge their volumes

### Requirement: Cleanup precedes final readiness
The retirement change SHALL require the functional finishing changes and experience acceptance, and SHALL provide a clean artifact for the separate remaining readiness checks.

#### Scenario: Initial audit finds unfinished routes
- **WHEN** the audit identifies retained Angular routes or fallback consumers
- **THEN** audit tasks may be recorded as complete but deletion remains blocked until replacements and the refreshed audit satisfy the gate

#### Scenario: Cleanup is implemented
- **WHEN** the enumerated legacy source, service, renderer, fallback and unused bridge dependencies are removed
- **THEN** the cleaned artifact passes this change's regression checks and proceeds to final readiness verification without implying authorization to deploy production

