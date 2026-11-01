## Purpose

Provide the first safe migrated resource-editing workflow for basic bio.tools fields while preserving all resource metadata not yet exposed by the new editor.

## ADDED Requirements

### Requirement: Authorized users can edit basic resource metadata
The migrated editor SHALL allow an authorized user to create or modify the supported basic resource fields and submit them for authoritative backend validation and persistence.

#### Scenario: Successful basic edit
- **WHEN** an authorized user changes a valid supported basic field and saves
- **THEN** the backend persists the change and the editor presents the saved authoritative resource state

### Requirement: Unauthorized editing is prevented server-side
The migrated editor SHALL enforce create/edit permissions on the server for page access and mutation.

#### Scenario: Unauthorized save attempt
- **WHEN** a user without permission attempts to submit a migrated editor mutation
- **THEN** the server rejects the mutation and resource data is not changed

### Requirement: Backend validation remains authoritative
The migrated editor SHALL present authoritative backend validation errors without treating client-side validation as sufficient for successful persistence.

#### Scenario: Backend rejects a field value
- **WHEN** the submitted editor state fails backend validation
- **THEN** the resource is not changed, the user's entered values remain available, and the validation error is presented at the corresponding field or error summary

### Requirement: Out-of-scope resource metadata is preserved
Editing the basic migrated fields SHALL NOT unintentionally clear or alter existing resource metadata that is not yet editable in this editor slice.

#### Scenario: Edit basic field on a rich existing resource
- **WHEN** a resource contains nested scientific, publication, link, credit or relationship data and the user edits only a basic field
- **THEN** successful persistence preserves the unrelated existing metadata

### Requirement: Unsaved changes are protected from accidental navigation
The editor SHALL warn the user before a normal navigation action would discard unsaved user changes, except after a successful save or explicit discard.

#### Scenario: Navigate away with unsaved changes
- **WHEN** the user has modified editor state since the last save and initiates navigation that would discard it
- **THEN** the user is given an opportunity to remain on the page or explicitly discard the changes
