## Baseline

Target: upstream develop pinned at `9faec5b3b660498fdef9736e65e331728b55f99c`, implemented only in `develop-migration/`. Review the current migration work on top of that baseline, not the older outer runtime.
See the [dependency audit](../../../docs/frontend-migration/legacy-removal-audit.md) and [finishing sequence](../../README.md#finishing-sequence).

## Why

Functional migrations need a final coherent user experience. Earlier schema and route milestones do not establish consistent tool presentation, accessibility or complete cross-page journeys.

## What Changes

- Refine the existing blue bio.tools shell, search entries, tool detail and schema-shaped editor without changing domain contracts.
- Review function diagrams, rich metadata, dense/empty records, navigation and all new account/domain/workflow screens on desktop and mobile.
- Verify keyboard access, focus, labels, contrast, status/error announcements and non-destructive session/validation recovery.
- Record cross-page acceptance evidence and resolve discovered blockers before legacy removal.

## Dependencies

Final acceptance depends on the functional finishing changes: `migrate-account-pages`, `complete-search-filter-parity`, `migrate-public-information-pages`, `adopt-upstream-dev-features` and `migrate-record-and-domain-management`. Include the native bridge review/apply states in cross-page acceptance. Earlier completed editor/schema/cutover contracts remain authoritative.

Also requires `add-schema-driven-resource-ui`. Visual acceptance includes generic
new fields and changed vocabulary labels with the same frontend build; preserve
the function diagram without restoring hard-coded exhaustive field lists.

## Capabilities

### New Capabilities

- `migration-experience-acceptance`: Migrated registry journeys meet documented visual, responsive and accessibility acceptance criteria.

### Modified Capabilities

None. Existing completed migration contracts remain in force; this change closes the remaining scope rather than reopening their historical acceptance.

## Impact

Existing Django templates/static styles and Vue components, shared navigation, focused accessibility/visual tests, browser fixtures and an experience acceptance record. No new component framework.
