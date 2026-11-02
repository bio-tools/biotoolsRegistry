# Resource editor specification

## Purpose
Edit biotoolsSchema resources safely using the active schema and vocabulary.

## Requirements
### Requirement: Metadata follows the active schema
The system SHALL derive field labels, choices and validation from a versioned schema/descriptor and backend capabilities. Compatible changes SHALL propagate without frontend edits or a rebuilt frontend.
Incompatible schema changes SHALL be gated, and unsupported or private fields SHALL NOT be advertised as writable, public or searchable.

#### Scenario: A compatible schema field is activated
- **WHEN** the backend advertises a new writable field or changed choices
- **THEN** the editor and relevant public projection expose it using the activated contract

### Requirement: Editing preserves resource data
The system SHALL preserve untouched and unknown supported metadata, stable nested identities and meaningful optional values; client-only identifiers SHALL NOT enter the public payload.
Previously saved deprecated values SHALL remain visible and SHALL NOT be silently removed or replaced during unrelated edits.

#### Scenario: A resource is loaded and saved
- **WHEN** an authorized user edits one field of a resource with nested metadata
- **THEN** unrelated metadata survives the save and backend errors identify the relevant field or item

### Requirement: Scientific annotations remain understandable
The editor SHALL support repeatable functions, operations, inputs and outputs with their associated data and formats, and display the function flow.

#### Scenario: Functions are reordered
- **WHEN** a user edits or reorders nested function items
- **THEN** annotations and validation errors remain attached to the intended items

### Requirement: Mutations are authorized and recoverable
The server SHALL enforce permissions, schema validation, CSRF and revision checks. Failed validation, stale revisions and unavailable metadata SHALL preserve the user's unsaved work.

#### Scenario: A save is rejected
- **WHEN** the record or schema changes while a draft is open
- **THEN** the save is rejected with a recoverable explanation and the draft remains available

### Requirement: GitHub import is optional and reviewable
The GitHub bridge SHALL be optional; imported suggestions SHALL follow the active writable-field policy and require review before explicit application and save.

#### Scenario: The bridge is unavailable
- **WHEN** a user opens the editor without a configured provider
- **THEN** manual editing remains available and no data is saved automatically
