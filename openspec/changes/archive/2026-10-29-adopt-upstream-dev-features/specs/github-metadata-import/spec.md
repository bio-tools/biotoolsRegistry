## Purpose

Bring upstream GitHub metadata import into the native schema-driven editor while
preserving curated records, authorization and the explicit save boundary.

## ADDED Requirements

### Requirement: Import requests use protected, optional transport
The system SHALL accept repository import requests through an authenticated,
CSRF-protected same-origin POST endpoint, validate an exact supported GitHub
repository URL, enforce target-record permissions, and keep provider credentials
server-side. The bridge SHALL be independently disableable.

#### Scenario: Authorized repository import
- **WHEN** an authorized editor submits a supported repository URL
- **THEN** the adapter sends only the validated repository coordinates and permitted optional tool identifier to the configured bridge
- **AND** both proxies route the request ahead of tool-detail and crawler handlers

#### Scenario: Invalid URL or unauthorized request
- **WHEN** a URL has a look-alike host, embedded credentials or invalid repository coordinates, or session/CSRF/record authorization fails
- **THEN** the adapter rejects the request without calling the bridge or changing the draft or record

#### Scenario: Disabled or failed provider
- **WHEN** the bridge is disabled, unavailable, rate limited, times out or returns malformed/oversized data
- **THEN** the editor shows a bounded, actionable state and retains the existing draft and manual editing functionality

### Requirement: Suggestions follow the active schema and writable-field policy
The system SHALL derive review fields, labels and structured values from the
activated resource descriptor and authoritative server policy. It SHALL NOT
maintain a separate frontend catalogue of bridge-editable schema fields.

#### Scenario: Compatible schema field appears in suggestions
- **WHEN** an activated compatible field or vocabulary value is returned by the bridge
- **THEN** the review uses its advertised shape and labels without a frontend rebuild

#### Scenario: Protected, unknown or incompatible suggestions
- **WHEN** returned data includes protected registry fields, unrecognized fields or values incompatible with the active contract
- **THEN** those values cannot be applied and the review explains the rejection without silently overwriting or dropping existing data

### Requirement: Review preserves current work and nested annotations
The system SHALL present current and suggested values, default existing curated
values to keep, and support replace, selective list merge, keep-all, discard and
escaped raw-output inspection. It SHALL preserve distinct nested annotations.

#### Scenario: Distinct functions share an operation
- **WHEN** current and suggested functions use the same operation but differ in inputs, outputs, formats, notes or commands
- **THEN** they remain distinct selectable values and merging does not discard their differences

#### Scenario: Draft or import changes during review
- **WHEN** the visitor edits the draft, changes review tabs or starts a newer import while an earlier request is pending
- **THEN** review remains tied to the latest draft and request, preserves applicable choices and requires renewed comparison before applying stale choices

#### Scenario: Keyboard and mobile review
- **WHEN** a visitor reviews suggestions using a keyboard or narrow viewport
- **THEN** current values, suggestions, selection controls, pending changes and confirmation remain readable and operable

### Requirement: Applying suggestions does not save a record
The system SHALL apply only explicitly confirmed selections to the editor draft,
reuse its validation/recovery and stable item identities, and require the normal
authorized save action for persistence.

#### Scenario: Apply then reload the stored record
- **WHEN** selected suggestions are applied but the draft has not been saved
- **THEN** the stored record and index remain unchanged and the draft is marked as edited

#### Scenario: Discard, cancel or validation failure
- **WHEN** the visitor discards/cancels suggestions or proposed draft application fails validation
- **THEN** the prior draft and stored record remain intact

#### Scenario: Save after permission or revision changes
- **WHEN** a visitor saves an imported draft after the record's permissions or revision have changed
- **THEN** the normal authoritative permission and stale-write checks apply, and failures preserve recoverable work
