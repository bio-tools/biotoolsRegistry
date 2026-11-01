# workflow-designer Specification

## Purpose
TBD - created by archiving change add-workflow-designer. Update Purpose after archive.
## Requirements
### Requirement: Users select functions using data, formats and operations
The system SHALL let users choose data and format constraints and optionally filter matching tool functions by EDAM operation.

#### Scenario: Selecting a next step
- **WHEN** a user chooses an output and an operation filter
- **THEN** matching candidates show the specific function and input, its operation, data/format evidence and any uncertainty

### Requirement: Users can tailor connected workflow designs
The system SHALL support editable step instances and explicit connections between inputs and outputs, including branching and multiple inputs/outputs.

#### Scenario: Branch and adjust a design
- **WHEN** a user connects one output to two steps and then edits or removes a connection
- **THEN** the remaining steps and connections are preserved and the diagram and accessible list agree

#### Scenario: Uncertain connection
- **WHEN** the annotation is missing, related or conflicting
- **THEN** the designer explains the state and does not claim guaranteed compatibility or execution

### Requirement: Drafts are recoverable and interactions accessible
The system SHALL preserve in-progress designs through recoverable errors and offer keyboard-operable alternatives to pointer-only interactions.

#### Scenario: Matching service fails
- **WHEN** candidate lookup fails during editing
- **THEN** the design remains intact and the user can retry or export the draft

#### Scenario: Enhanced assets unavailable
- **WHEN** the designer cannot start
- **THEN** the user sees an honest unavailable state and can navigate to the existing workflow gallery

### Requirement: Existing workflow gallery remains available
The system SHALL keep the existing read-only image workflows and their links available independently of new structured designs.

#### Scenario: Existing image workflow
- **WHEN** a visitor opens a previously available workflow image
- **THEN** its image and annotations remain inspectable without being converted into an editable design

