## Purpose

Provide a reusable, accessible interface for selecting valid EDAM concepts in migrated bio.tools search and editing workflows without loading the complete ontology into the browser.

## ADDED Requirements

### Requirement: Users can search within a declared EDAM concept scope
The selector SHALL search only within the EDAM concept scope configured for that field or control and SHALL return bounded matching choices.

#### Scenario: Search for an operation concept
- **WHEN** a selector is configured for EDAM operations and the user enters a lookup query
- **THEN** the choices returned for selection are valid for the configured operation scope

### Requirement: Selected EDAM values use stable identifiers
The system SHALL persist or submit selected EDAM concepts by validated stable identifier rather than trusting a browser-supplied display label as identity.

#### Scenario: Client label does not match identifier
- **WHEN** a submitted selection contains a valid identifier with a manipulated or stale label
- **THEN** the server resolves/uses the authoritative concept identity rather than trusting the supplied label

### Requirement: EDAM selection is keyboard accessible
The selector SHALL support keyboard-only discovery, navigation, selection and removal behavior appropriate to its single- or multiple-selection mode.

#### Scenario: Keyboard-only multiple selection
- **WHEN** a user interacts with a multiple EDAM selector using only the keyboard
- **THEN** the user can search choices, move through choices, select a concept and remove a selected concept without requiring pointer input

### Requirement: Stale lookup responses cannot replace newer choices
The selector SHALL prevent a slower older lookup response from overwriting the choices for a newer user query.

#### Scenario: User types another query before the previous lookup completes
- **WHEN** the newer lookup is issued before the older request completes
- **THEN** the older response is cancelled or ignored and cannot replace the newer query's choice list
