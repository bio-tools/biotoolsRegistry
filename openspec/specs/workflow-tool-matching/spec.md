# workflow-tool-matching Specification

## Purpose
TBD - created by archiving change add-workflow-tool-matching. Update Purpose after archive.
## Requirements
### Requirement: Matching respects function and input/output relationships
The system SHALL return function-specific matches verified against a current visible resource and the same input or output annotation.

#### Scenario: Different functions have the requested properties
- **WHEN** one function has the requested data and another has the requested format or operation
- **THEN** the system does not present their combined properties as a single matching function

#### Scenario: Multiple inputs and formats
- **WHEN** a function has several annotated inputs or outputs
- **THEN** each match identifies the particular IO item and associated formats used as evidence

### Requirement: Operation is a selectable matching filter
The system SHALL allow an EDAM operation constraint and apply it to the selected matching function.

#### Scenario: Same resource, different operation
- **WHEN** a resource contains multiple functions and only one has the selected operation
- **THEN** other functions are not presented as satisfying that operation filter

### Requirement: Match uncertainty is explicit
The system SHALL distinguish exact, directionally related, unknown and conflicting data/format evidence without claiming execution compatibility.

#### Scenario: Missing format
- **WHEN** a relevant input or output lacks a format annotation
- **THEN** the match reports the format as unknown and does not claim an exact format match

#### Scenario: Ontology-related terms
- **WHEN** terms differ but have a supported EDAM hierarchy relationship
- **THEN** the result states the relationship and direction and requires user interpretation

### Requirement: Matching remains complete and schema-aware
The system SHALL validate against active schema and EDAM metadata and accurately report result completeness, pagination and unavailable states.

#### Scenario: Index or vocabulary is stale or unavailable
- **WHEN** the system cannot safely establish the current candidate set or interpret a changed schema
- **THEN** it reports the limitation or failure rather than silently reporting complete compatible results

