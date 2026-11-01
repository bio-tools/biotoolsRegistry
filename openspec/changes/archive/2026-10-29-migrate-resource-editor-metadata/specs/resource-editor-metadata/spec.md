## ADDED Requirements

### Requirement: Remaining schema metadata has dedicated editing controls
The migrated editor SHALL support version, otherID, topic, operatingSystem,
language, license, collectionID, maturity, cost, accessibility, elixirPlatform,
elixirCommunity, elixirNode, link, download, documentation, relation, publication
and credit using authoritative nested structures, cardinalities and options.

#### Scenario: Curate a complete resource
- **WHEN** an authorized curator changes the remaining metadata through its dedicated controls and saves a valid resource
- **THEN** reload shows the submitted values in the schema-compatible shape without dropping unrelated data

### Requirement: Repeated metadata retains validation identity
Repeated metadata entries SHALL reuse stable client-only IDs and submitted-snapshot
error mapping, and those IDs SHALL NOT enter the public payload.

#### Scenario: Correct an invalid credit after moving an entry
- **WHEN** a credit is rejected with an indexed validation error and entries are moved
- **THEN** the error remains associated with that credit and can be corrected without losing the draft

### Requirement: Extended editing preserves mutation safeguards
Metadata saves SHALL retain session authentication, CSRF, object permissions,
revision checking, unknown-key rejection and preservation of server-owned data.
Known unsafe replacement cases SHALL remain blocked until persistence is verified.

#### Scenario: Existing publication enrichment cannot be preserved
- **WHEN** a resource contains enriched publication data the save path cannot preserve
- **THEN** saving is blocked without changing the resource and the complete draft remains exportable

### Requirement: Editor cutover requires explicit coverage evidence
Editor route cutover SHALL require review of all 26 top-level schema fields and
separate registry-only workflows; completed basic and function slices alone
SHALL NOT count as full editor parity.

#### Scenario: A metadata section remains unmigrated
- **WHEN** cutover is assessed while required metadata controls or preservation tests remain incomplete
- **THEN** canonical editor routes remain legacy-owned
