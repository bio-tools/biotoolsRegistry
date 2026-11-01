## Purpose

Protect bio.tools resource data during editor migration by making round-trip preservation, client-only state removal and nested validation targeting explicit and testable.

## ADDED Requirements

### Requirement: Loading and resaving does not silently delete untouched resource data
The migrated editor data path SHALL preserve resource fields and nested structures that the user did not intentionally change, subject only to documented authoritative backend normalization.

#### Scenario: Save after editing one basic field
- **WHEN** an existing resource with additional nested metadata is loaded and the user changes only one in-scope basic field
- **THEN** saving the resource preserves unrelated existing metadata rather than omitting or clearing it unintentionally

### Requirement: Client-only editor identity does not enter the public resource payload
The editor MAY use stable client-side identifiers for repeated items, but those identifiers SHALL NOT be persisted as bio.tools resource fields unless they are part of the authoritative schema.

#### Scenario: Reordered repeated items are submitted
- **WHEN** repeated editor items with client-only rendering IDs are reordered and saved
- **THEN** the submitted resource represents the intended order/content without including the client-only IDs

### Requirement: Meaningful optional-value distinctions are preserved
The editor conversion SHALL preserve distinctions among absent, null, empty and populated values wherever the authoritative schema/API treats those states differently.

#### Scenario: Optional values survive an unrelated edit
- **WHEN** a resource contains optional values whose absent/null/empty distinction is meaningful and the user edits an unrelated field
- **THEN** the editor submission does not collapse those values into a different semantic state

### Requirement: Backend validation errors can target nested editor fields
The migrated editor SHALL be able to associate authoritative backend validation errors with the corresponding top-level or nested repeated editor field from the submitted snapshot.

#### Scenario: Validation error in a nested output
- **WHEN** the backend rejects a field inside a specific function output in the submitted resource
- **THEN** the editor can present that error at the corresponding function/output field rather than only as an unlocated global message
