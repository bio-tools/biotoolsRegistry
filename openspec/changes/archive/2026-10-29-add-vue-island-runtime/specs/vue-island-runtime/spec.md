## Purpose

Provide isolated, typed Vue applications for state-heavy interface regions while Django retains page routing and server authority across the registry.

## ADDED Requirements

### Requirement: Vue mounts only on explicitly declared interface roots
The system SHALL instantiate Vue applications only for DOM roots explicitly declared for a registered Vue component or application.

#### Scenario: Page without a Vue root
- **WHEN** a Django-rendered page contains no declared Vue root
- **THEN** loading the Vue runtime does not take ownership of unrelated page DOM

#### Scenario: Multiple declared roots
- **WHEN** a page contains multiple valid Vue roots
- **THEN** each root is mounted once with its own declared initial data

### Requirement: Server-provided Vue input is transferred safely
Initial data provided by Django to a Vue root SHALL be serialized using an escaping-safe non-executable JSON mechanism and parsed as data by the client runtime.

#### Scenario: Initial data contains markup-like characters
- **WHEN** server-provided text contains characters that could otherwise terminate or alter HTML/script markup
- **THEN** the text is delivered as data without executing unintended script or changing surrounding markup

### Requirement: Vue lifecycle remains correct across server fragment replacement
When an htmx operation inserts or removes complete Vue roots, the system SHALL mount newly inserted roots and unmount removed roots without duplicate Vue applications.

#### Scenario: Fragment inserts a Vue root
- **WHEN** an htmx fragment inserts a registered Vue root into the page
- **THEN** the Vue root becomes interactive once without requiring a full page reload

#### Scenario: Fragment replaces a mounted Vue root
- **WHEN** an htmx operation removes or replaces the element that is the root of a mounted Vue application
- **THEN** the previous Vue application is unmounted before the old root is discarded and any new declared root is mounted once
