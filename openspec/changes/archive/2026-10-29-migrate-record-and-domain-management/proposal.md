## Baseline

Target: upstream develop pinned at `9faec5b3b660498fdef9736e65e331728b55f99c`, implemented only in `develop-migration/`. Review the current migration work on top of that baseline, not the older outer runtime.
See the [dependency audit](../../../../docs/frontend-migration/legacy-removal-audit.md) and [finishing sequence](../../../README.md#finishing-sequence).

## Why

Record removal/disowning, raw JSON editing and standalone validation, domain management and workflow inspection still rely on AngularJS. Existing migrated schema controls and requests do not cover these remaining workflows.

## What Changes

- Provide native authorized record delete/disown actions and replace legacy Manage record links, reusing migrated permission/request behavior.
- Preserve supported raw JSON editing and standalone validation through the existing editor contract and authoritative validators.
- Implement domain create/edit/delete, membership and editor management with compatible aliases and backend-enforced policy.
- Migrate public workflow browsing/filtering and annotated image inspection; preserve staff/API operations without inventing browser authoring.
- Remove editor failure-state dependence on AngularJS without pretending a rich editor can operate without its assets.

## Dependencies

Depends on `migrate-account-pages`, `complete-search-filter-parity`, completed schema editor/request cutover, and the public domain-directory contract in `migrate-public-information-pages`. Profile owns account data; this change owns its record-action handlers and links.

Requires `add-schema-driven-resource-ui` before JSON/editor extensions. Reuse its
runtime descriptor, version-conflict and deprecated-value handling instead of
adding schema-specific allowlists.

The 2026-10-25 finishing sequence inserts `adopt-upstream-dev-features` before
this change. Use its accepted integration baseline and shared save/schema
contracts. Domain editor selection must incorporate the reviewed dev keyboard,
duplicate-exclusion, stale-response and error behavior; do not copy Angular
controllers or reimplement the record permission/request controls.

## Capabilities

### New Capabilities

- `native-registry-management`: Remaining record/domain operations and workflow inspection have safe native replacements.

### Modified Capabilities

None. Existing completed migration contracts remain in force; this change closes the remaining scope rather than reopening their historical acceptance.

## Impact

Django record/domain/workflow views/forms/templates/URLs, existing write policies and index updates, editor JSON/validation controls, profile/detail links, fixtures, both proxies and mutation/browser tests. Audit B04-B06 and editor fallback in B08.
