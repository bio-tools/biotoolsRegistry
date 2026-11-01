# develop-migration-baseline Specification

## Purpose
Record the pinned develop baseline and evidence for the frontend migration.
## Requirements
### Requirement: Migration baseline is explicit and pinned
Migration changes SHALL target upstream `bio-tools/biotoolsRegistry` develop at the
revision recorded in the baseline document. Moving that pin SHALL require a recorded
delta review and revalidation of affected contracts.

#### Scenario: Implementation starts from a different revision
- **WHEN** the implementation checkout is not based on the accepted develop revision
- **THEN** further feature implementation waits for explicit integration and compatibility review

### Requirement: Existing local work is preserved
Baseline integration SHALL preserve unrelated changes and all reviewed migration
artifacts, including untracked and ignored files, without destructive worktree operations.

#### Scenario: Original worktree contains uncommitted changes
- **WHEN** upstream develop is prepared for migration work
- **THEN** an isolated integration checkout is used and the original worktree remains intact

### Requirement: Foundation acceptance is revision-specific
The inventory, regression harness, Django shell and htmx foundation SHALL be
revalidated on the pinned develop stack before subsequent feature changes proceed.
Old test results SHALL remain associated with their original revision.

#### Scenario: Old-tree tests pass but develop has not been tested
- **WHEN** a completed foundation change has only old-baseline evidence
- **THEN** its develop revalidation remains pending and cannot satisfy the prerequisite

### Requirement: Both proxy paths preserve ownership
The refreshed shell SHALL support the develop Caddy/HTTP and production Apache/WSGI
paths while preserving supported API, account and non-migrated legacy routes.

#### Scenario: Browser or crawler requests the isolated HTML route
- **WHEN** the route is requested through either supported proxy path
- **THEN** Django HTML renders with correct assets and URL reversal without being intercepted by the SPA or inappropriate prerender fallback

### Requirement: Current behavior and upstream tests inform migration
The refreshed inventory SHALL cover develop route, authentication, search, editor,
schema and deployment behavior, and SHALL identify reusable upstream test coverage
and unresolved fixture/provider prerequisites.

#### Scenario: Develop contains a route missing from the old inventory
- **WHEN** the baseline review finds an additional account or user-facing route
- **THEN** it is recorded with a migration or explicit retention decision before route cutover or legacy removal

