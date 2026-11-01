# resource-editor-nested-science Specification

## Purpose
Support editing scientific functions, operations, inputs and outputs with stable identity.
## Requirements
### Requirement: Function editing exposes the scientific flow
Each function SHALL present editable inputs, operations and outputs in a connected
input-to-operation-to-output diagram with compact EDAM controls. The flow SHALL
remain readable and keyboard-operable on desktop and mobile without a separate
unsynchronized preview.

#### Scenario: Edit a function on a narrow screen
- **WHEN** a curator opens a function on a mobile viewport
- **THEN** inputs, operations and outputs appear in that reading order with directional connectors and without horizontal overflow

### Requirement: Users can edit repeatable resource functions
The migrated editor SHALL support adding, editing and removing multiple resource functions according to the authoritative resource model.

#### Scenario: Add a second function
- **WHEN** an authorized user adds and completes a second valid function and saves
- **THEN** both functions are persisted with their intended nested scientific metadata

### Requirement: Functions can contain validated operations, inputs and outputs
Each editable function SHALL support the authoritative repeatable operation, input and output structures, including validated EDAM-backed fields where required.

#### Scenario: Add an input with EDAM data and format concepts
- **WHEN** a user adds an input and selects valid EDAM data/format concepts
- **THEN** the submitted nested resource contains the corresponding validated stable EDAM identifiers in the expected input structure

### Requirement: Nested item identity remains stable during client editing
Adding, removing or reordering nested items SHALL NOT cause values or validation messages to migrate to a different logical item because of array-index-only client identity.

#### Scenario: Reorder functions after editing both
- **WHEN** the user edits two functions and then reorders them before saving
- **THEN** each function retains its own edited values and later validation feedback is associated with the intended submitted function

### Requirement: Nested backend errors are presented at the relevant item
The editor SHALL present authoritative validation errors for nested scientific fields at the corresponding function, operation, input or output whenever the backend provides sufficient path information.

#### Scenario: Invalid format on the second output
- **WHEN** the backend rejects a format value within the second output of a submitted function
- **THEN** the editor identifies that output/format control rather than presenting only an unlocated global error

### Requirement: Nested editing preserves unrelated resource metadata
Changes to nested scientific structures SHALL NOT unintentionally clear unrelated resource fields outside the user's changes.

#### Scenario: Edit an operation on a resource with publications and credits
- **WHEN** a user changes an operation and saves without editing publications or credits
- **THEN** the existing publication and credit metadata is preserved

