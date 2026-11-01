# public-tool-detail-page Specification

## Purpose
Present public tool records through directly renderable, schema-aware pages.
## Requirements
### Requirement: Public resources have directly renderable detail pages
The system SHALL render a public resource detail page directly from its canonical resource identifier without requiring prior navigation through a client-side application.

#### Scenario: Direct request for a public resource
- **WHEN** a user requests the detail URL for an existing public resource
- **THEN** the server returns a complete page containing the resource identity, description and available structured metadata

### Requirement: Optional resource data is handled safely
The detail page SHALL render resources with missing optional fields or empty nested collections without failing or presenting fabricated values.

#### Scenario: Sparse resource
- **WHEN** a public resource lacks one or more optional metadata sections
- **THEN** the page renders successfully and omits or marks those sections appropriately without inventing content

### Requirement: Structured metadata remains discoverable
The detail page SHALL expose available scientific, technical and attribution metadata needed to understand the resource, including nested functions/operations and relevant EDAM identifiers or labels where they exist.

#### Scenario: Structurally rich resource
- **WHEN** a resource contains functions, operations, input/output metadata, publications, links, credits or relationships
- **THEN** the corresponding available information is presented in an identifiable page section

### Requirement: Invalid or inaccessible resources do not masquerade as valid pages
The system SHALL return an appropriate not-found or access-policy response for resource identifiers that cannot be presented publicly.

#### Scenario: Unknown resource identifier
- **WHEN** a user requests a resource identifier that does not exist
- **THEN** the server returns the configured not-found response rather than an empty successful detail page

