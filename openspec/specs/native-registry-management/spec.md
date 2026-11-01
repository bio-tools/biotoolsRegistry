# native-registry-management Specification

## Purpose
Provide safe native record and domain management and preserve workflow-image inspection.
## Requirements
### Requirement: Record actions preserve authorization and data safety
The system SHALL provide native record removal and disowning with explicit confirmation, CSRF protection and authorization against the current record state.

#### Scenario: Ownership changes before submission
- **WHEN** a previously authorized user submits a destructive action after losing the necessary rights
- **THEN** the server rejects the action without changing the record or index

#### Scenario: Confirmed record action
- **WHEN** an authorized user confirms a supported record action
- **THEN** the existing policy is applied and the resulting profile/detail/search state is consistent

### Requirement: JSON editing and validation preserve drafts
The system SHALL support raw JSON draft edits and validation-only requests using the existing schema contract, without bypassing metadata preservation or mutation checks.

#### Scenario: Invalid JSON draft
- **WHEN** a user submits malformed or unsupported JSON to the editor
- **THEN** the current draft is retained and actionable errors are displayed without a save

#### Scenario: Validation without saving
- **WHEN** a user validates a well-formed draft
- **THEN** authoritative errors or success are returned without persisting or reindexing a resource

### Requirement: Domain management is native and policy controlled
The system SHALL support existing domain-management routes and aliases with server-enforced ownership/editor rules and consistent resource membership updates.

#### Scenario: Unauthorized domain mutation
- **WHEN** a user without required current rights submits a domain update or deletion
- **THEN** the server rejects it irrespective of whether the UI displayed the control

#### Scenario: Domain write or index failure
- **WHEN** a domain mutation encounters a persistence or index failure
- **THEN** the user receives an error and the documented consistency/recovery contract prevents a false successful outcome

### Requirement: Workflow inspection is preserved without new authoring scope
The system SHALL provide native workflow browsing, filtering and accessible annotated-image inspection while preserving existing staff/API interfaces.

#### Scenario: Inspecting a scaled workflow image
- **WHEN** a visitor selects an annotation using keyboard, touch or pointer
- **THEN** the matching details and safe link remain accessible and aligned with the displayed image

#### Scenario: Workflow data or image unavailable
- **WHEN** workflow data or media cannot be loaded
- **THEN** the page shows a recoverable unavailable state rather than an empty successful result

### Requirement: Editor failure states do not require legacy code
The system SHALL provide a non-destructive, accessible editor unavailable state when modern JavaScript cannot run, without relying on AngularJS.

#### Scenario: Editor assets unavailable
- **WHEN** a user opens an editor whose JavaScript is disabled or fails to load
- **THEN** native content identifies the unavailable editor and offers applicable record/export navigation without a legacy link

#### Scenario: Legacy management link replaced
- **WHEN** a user follows Manage record or a profile record action after migration
- **THEN** the destination is the authorized native workflow rather than the legacy detail/editor

