## Purpose

Preserve and deliberately share non-executable workflow designs without losing private or unresolved user work.

## ADDED Requirements

### Requirement: Designs are private and revision protected
The system SHALL save structured workflow drafts under an owner and enforce current authorization and revision checks for mutations.

#### Scenario: Concurrent edits
- **WHEN** a user saves a draft after a newer version has been saved
- **THEN** the system rejects the stale save and preserves the user's unsaved changes for recovery

#### Scenario: Unauthorized access
- **WHEN** another user requests or changes an unshared draft
- **THEN** the system denies access without disclosing its contents

### Requirement: Sharing is explicit and revocable
The system SHALL make sharing an owner-controlled action and give recipients read-only access until sharing is revoked.

#### Scenario: Revoking a shared design
- **WHEN** the owner revokes a sharing link
- **THEN** subsequent link requests cannot read the draft and the owner's private copy is retained

### Requirement: Portable descriptions preserve designs safely
The system SHALL support validated, versioned import and export of non-executable designs while retaining unresolved user choices.

#### Scenario: Tool annotations changed
- **WHEN** an imported or reopened design references a changed, hidden, missing or ambiguous function
- **THEN** the system preserves the original reference and notes, explains the problem and requires explicit review before reconnecting

#### Scenario: Invalid import
- **WHEN** an imported description is malformed, unsupported or exceeds declared limits
- **THEN** it is rejected without replacing the current draft

### Requirement: Failed saves do not lose work
The system SHALL retain unsaved edits and provide recovery when authentication expires or persistence fails.

#### Scenario: Session expires during save
- **WHEN** the session expires before a save completes
- **THEN** the user can recover the unchanged draft and sign in again without a false success indication
