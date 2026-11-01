## Purpose

Make supported schema fields and vocabulary changes flow automatically from the
activated backend contract into the resource UI without duplicated frontend
field definitions, while preserving data and authoritative validation.

## ADDED Requirements

### Requirement: Effective metadata has a versioned authoritative source
The system SHALL derive a versioned effective resource UI descriptor from a selected biotoolsSchema artifact, backend JSON capabilities and explicit registry policy, recording schema and vocabulary provenance.

#### Scenario: Schema and backend disagree
- **WHEN** ingestion finds a schema choice or field inconsistent with current backend representation or persistence
- **THEN** the compatibility report identifies the discrepancy and activation requires an explicit tested resolution rather than silent narrowing or false write support

#### Scenario: Schema-owned options change
- **WHEN** a compatible selected schema revision is activated
- **THEN** backend validation and UI option metadata derive from the same source without manually copying enum lists

### Requirement: Compatible metadata changes propagate without frontend edits
The system SHALL apply supported field labels, help, choices and constraints from the active runtime descriptor without frontend source changes or a frontend bundle rebuild.

#### Scenario: Label and allowed value update
- **WHEN** an activated compatible revision changes a label and adds an allowed value
- **THEN** a new page load using the unchanged frontend build displays the updated label and offers the value accepted by the backend

#### Scenario: Supported optional nested field added
- **WHEN** the backend activates a supported optional nested field with persistence and write capability
- **THEN** the unchanged frontend build renders and round-trips that field through generic controls even without a field-specific component

### Requirement: Specialized presentation does not hide schema additions
The system SHALL retain useful specialized function and ontology presentation while exposing supported unhandled fields through a generic fallback.

#### Scenario: Function section gains metadata
- **WHEN** a supported field is added inside a function structure without a matching specialized renderer
- **THEN** the input-operation-output diagram remains usable and the new field is available through generic presentation without data loss

#### Scenario: Public or search capability is absent
- **WHEN** a field exists in schema metadata but lacks public visibility or backend search support
- **THEN** the frontend does not expose private data or offer an unsupported search control

### Requirement: Schema and vocabulary changes preserve existing values
The system SHALL distinguish display labels from stable field/value identifiers and SHALL preserve existing deprecated or unknown values visibly without silently deleting, coercing or replacing them.

#### Scenario: Previously saved enum value is removed
- **WHEN** a record contains a value no longer offered for new selection
- **THEN** the UI displays the stored value and follows the explicit server preservation or correction policy without erasing it during an unrelated edit

#### Scenario: EDAM term label changes
- **WHEN** the activated ontology revision changes a term label or marks it obsolete
- **THEN** lookup presentation reflects that revision while retaining URI identity and requiring an explicit action for a semantic replacement

### Requirement: Incompatible changes are compatibility-gated
The system SHALL reject incompatible activation or require explicit tested migrations for field/value identifier renames, type/cardinality changes, new required fields and unsupported constructs.

#### Scenario: Field key is renamed
- **WHEN** a selected schema changes a stored field identifier rather than its label
- **THEN** the system requires a tested alias or data migration policy and does not infer equivalence from similar text

#### Scenario: Backend cannot persist a new field
- **WHEN** ingestion discovers a schema field without supported backend storage or serialization
- **THEN** activation is blocked or the field is explicitly quarantined read-only with diagnostics, never presented as safely writable

### Requirement: In-flight drafts and metadata failures are non-destructive
The system SHALL keep descriptor revision separate from record revision and handle changed or unavailable metadata without silently resubmitting under a different contract or losing drafts.

#### Scenario: Schema changes while editing
- **WHEN** a user submits a draft loaded under an older effective descriptor
- **THEN** the server checks compatibility and revalidates or returns a recoverable conflict while preserving the user's draft and export

#### Scenario: Descriptor unavailable or invalid
- **WHEN** runtime metadata cannot be loaded or interpreted safely
- **THEN** the UI provides a non-destructive unavailable/read-only state and does not treat missing choices or fields as empty record values

### Requirement: Updates are reproducible and tested with an unchanged client
The change SHALL provide automated ingestion/generation/drift checks for a selected schema revision and prove compatible changes using the same frontend artifact.

#### Scenario: Update rehearsal
- **WHEN** schema and vocabulary fixtures are updated during acceptance
- **THEN** tests show supported labels, values and nested fields updating without a frontend rebuild while incompatible revisions fail the documented gate

#### Scenario: Unreviewed upstream publication
- **WHEN** an upstream schema release is published
- **THEN** it does not change production behavior until the selected revision passes compatibility checks and is explicitly activated
