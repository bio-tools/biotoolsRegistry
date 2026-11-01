## Purpose

Integrate reviewed upstream dev behavior into the migration without losing native
route ownership, schema-driven metadata, persistence guarantees or rollback.

## ADDED Requirements

### Requirement: Integration has a pinned, reviewed scope
The system SHALL record exact upstream and migration revisions, a disposition for
each changed feature/configuration area, and regression evidence before updating
the accepted migration baseline.

#### Scenario: Upstream moves during implementation
- **WHEN** upstream dev advances beyond the reviewed revision
- **THEN** the additional delta is explicitly reviewed or left for a later pinned update rather than silently changing the acceptance target

#### Scenario: Existing migration behavior already covers an upstream change
- **WHEN** a reviewed feature is already equivalent in the native implementation
- **THEN** compatibility evidence is retained without duplicating the feature or reintroducing an Angular dependency

### Requirement: Expanded vocabularies propagate through shared contracts
The system SHALL incorporate the reviewed licence/community vocabularies through
the active backend schema/policy and generated descriptor, retaining supported
historical values and keeping editor, search, detail and API validation aligned.

#### Scenario: Newly accepted licence or community
- **WHEN** the reviewed vocabulary is activated
- **THEN** supported new choices are available to native controls and accepted by the authoritative JSON/XML validation path without separate frontend lists

#### Scenario: Existing values and compatible rollback
- **WHEN** old records use deprecated supported licences or the operator rolls back a compatible descriptor
- **THEN** records remain readable and recoverable and unsupported edits fail explicitly without destructive normalization

### Requirement: Unchanged updates preserve state
The system SHALL distinguish unchanged authorized updates from real changes in
shared write handling, communicate that result to native/API clients, and avoid
unnecessary timestamp/history/index/notification changes.

#### Scenario: Repeated unchanged update
- **WHEN** a valid authorized update repeats content already represented by the established comparison state
- **THEN** it returns an unchanged result and does not create another resource version or change timestamps, index contents or notifications

#### Scenario: Order or nested content changes meaningfully
- **WHEN** a submitted update changes an ordered annotation, a significant duplicate, nested value or writable permission
- **THEN** it is not discarded as unchanged by blanket sorting or deduplication

#### Scenario: Stale or unauthorized unchanged payload
- **WHEN** an otherwise identical payload fails current authorization, validation or optimistic concurrency checks
- **THEN** the normal failure applies before any unchanged-success shortcut

### Requirement: Upstream interaction improvements fit native workflows
The system SHALL reconcile dashboard filter discovery, active-value clearing and
record/domain user-picker behavior with existing native controls, retaining
nested filters, URL semantics, scope and accessible failure handling.

#### Scenario: Scoped filter option selection
- **WHEN** a visitor searches used-term options, selects or clears a value within a domain/query
- **THEN** supported query parameters, scope, pagination reset and browser history remain consistent across enhanced and native results

#### Scenario: User-picker race or duplicate
- **WHEN** a user-picker response arrives after a newer search or includes already-selected users
- **THEN** stale results cannot replace current suggestions and duplicate selections are prevented while keyboard/error states remain usable

### Requirement: Runtime integration preserves deployment boundaries
The system SHALL reconcile environment parsing, image packaging, proxy routing,
taskrunner and CI with the native migration, preserving persistent data, retained
assets, API isolation and independent bridge/route rollback.

#### Scenario: Explicit false configuration
- **WHEN** a supported boolean setting is configured with an explicit false representation
- **THEN** it is disabled rather than enabled by the truthiness of a non-empty string

#### Scenario: Production-like artifact starts without source mounts
- **WHEN** the reconciled artifact starts in the disposable acceptance stack without host application source mounts
- **THEN** backend, modern and retained content assets, required legacy routes and taskrunner operate with the recorded interpreter/configuration versions

#### Scenario: Bridge disabled or integration rolled back
- **WHEN** the bridge is disabled or the tested prior configuration/artifact is restored
- **THEN** manual editing and retained route families work without deleting saved data or persistent volumes

#### Scenario: Automated verification
- **WHEN** CI verifies the integration
- **THEN** API, descriptor/vocabulary, modern type/unit/build and affected browser contracts are exercised with deterministic bridge fixtures and isolated cleanup
