## Baseline

Target: the current migration implementation in `develop-migration/`, based on
upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`. The inspected bundled
XML schema is biotoolsSchema 3.3.0, not a claim about the latest upstream release.

## Why

The frontend should be mostly agnostic of individual biotoolsSchema fields and
controlled values. Updating the active schema or vocabulary should update supported
controls and presentation automatically, without manually editing Vue components,
Django templates or duplicated enum lists.

The existing serializer-generated contract covers shapes, not a complete dynamic
UI. Metadata labels, sections and editable field sets are hard-coded, and backend
option lists are maintained separately from the bundled schema.

## What Changes

- Introduce a versioned backend resource UI descriptor derived from the selected
  biotoolsSchema artifact, effective JSON serializer contract and explicit registry
  policy, with provenance for schema and external vocabularies.
- Generate supported fields, labels/help, choices, constraints and cardinality;
  expose them to editor, detail and applicable search controls at runtime.
- Reuse generic field/repeated-record components, adding generic rendering for
  supported types and fallback fields while retaining specialized function/EDAM
  presentation as small overrides, not exhaustive field lists.
- Make compatible active-schema/value updates flow through without frontend source
  edits or a frontend rebuild; automate descriptor/validator generation and drift checks.
- Preserve existing values, drafts, permissions and server metadata across version
  changes; gate incompatible structural changes rather than guessing migrations.

## Dependencies

Build on completed resource-editor-data-contract, schema editor, EDAM, shared-query
and detail changes. Implement before `complete-search-filter-parity`,
`migrate-record-and-domain-management` and final experience acceptance.
Account-page work is independent and may remain first in the finishing sequence.

## Capabilities

### New Capabilities

- `schema-driven-resource-ui`: Supported resource fields and controlled vocabulary
  changes flow from an activated backend contract into the frontend automatically,
  with explicit compatibility and data-preservation guarantees.

### Modified Capabilities

None. Earlier data-integrity, permission, validation and schema-coverage
requirements remain mandatory. This change replaces their duplicated presentation
metadata rather than weakening their safeguards.

## Impact

Backend schema/serializer metadata and enum validation, runtime descriptor/config
delivery, generated TypeScript artifacts, editor conversion and rendering,
server-rendered detail, search metadata/capabilities, EDAM version/cache handling,
CI fixtures and schema-update runbook. No automatic production schema migration.
