# Workflow planning specification

## Purpose
Help users plan connected tool functions without promising execution.

## Requirements
### Requirement: Matching preserves function relationships
The system SHALL match selected input or output data and formats within the same function and SHALL support an optional EDAM operation constraint on that function.

#### Scenario: Annotations occur in different functions
- **WHEN** data, format or operation evidence belongs to different functions of one resource
- **THEN** it is not presented as one matching function

### Requirement: Match uncertainty and live data are explicit
The system SHALL distinguish exact, related, unknown and conflicting evidence, disclose that paginated results read live registry data, and report unavailable vocabulary or incomplete scans rather than claiming complete matches. Only currently visible resources may be returned.

#### Scenario: An annotation is missing or obsolete
- **WHEN** a candidate cannot be confirmed against the selected terms
- **THEN** the interface reports uncertainty rather than claiming compatibility

### Requirement: Designs are editable and recoverable
The system SHALL let users select functions, connect steps, edit their design and recover unsaved work. The existing annotated-image gallery SHALL remain available.

#### Scenario: A save fails
- **WHEN** a design cannot be saved or a revision conflicts
- **THEN** the user retains the draft and receives a recovery path

### Requirement: Drafts and sharing are controlled
Saved designs SHALL be private by default, revision protected and shared only through explicit, revocable read-only links. Unauthorized users SHALL NOT see private draft contents.

#### Scenario: A share is revoked
- **WHEN** the owner revokes a link
- **THEN** that link no longer grants access to the design

### Requirement: Portable designs are not executable workflows
Import and export SHALL use validated, versioned planning descriptions and SHALL NOT claim to generate executable workflows. Invalid imports SHALL NOT replace the current draft; unresolved references and notes SHALL be preserved for review.

#### Scenario: A user exports a design
- **WHEN** the exported description is shared or reimported
- **THEN** it preserves the planning design without presenting it as runnable code
