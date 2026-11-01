## Baseline

The migration was built from upstream develop at `9faec5b3b660498fdef9736e65e331728b55f99c` and moved to the repository root on 2026-11-01. At the user's request, the unchanged working files are now uncommitted on `trial_rewrite_codex`; its historical commit differs from the develop baseline.
See the [dependency audit](../../../docs/frontend-migration/legacy-removal-audit.md) and [finishing sequence](../../README.md#finishing-sequence).

## Why

Preview cutover and deterministic tests are not production approval. Configured account providers, deployment assets, security, indexing, performance and rollback need explicit evidence on the cleaned release.

## What Changes

- Establish a release-candidate gate covering all native routes, shared assets, permanent helper URLs and deployment configuration.
- Verify configured ORCID/email journeys, browser/API security isolation, crawler/indexing behavior and representative performance.
- Rehearse route rollback while legacy exists and document a separate whole-release rollback after deletion.
- Run clean legacy-free verification after the existing removal change and produce an operator handover with explicit deployment approval still required.

## Dependencies

Sections 1-3 require the functional finishing changes and `polish-and-validate-migrated-experience`. On 2026-11-01 the user authorized legacy source removal before the outstanding checks; all readiness checks remain required for release. Final verification (section 4) runs on the cleaned artifact.

Release readiness also requires `add-schema-driven-resource-ui`; the release
inventory includes schema/descriptor/vocabulary versions and compatibility
evidence for updating or rolling them back.

## Capabilities

### New Capabilities

- `migration-production-readiness`: Configured checks and cleaned-artifact verification establish evidence-backed release readiness.

### Modified Capabilities

None. Existing completed migration contracts remain in force; this change closes the remaining scope rather than reopening their historical acceptance.

## Impact

Deployment/runbook evidence, permanent browser helper routing, asset destination inventory, environment/security checks, CI/build/browser acceptance and release/rollback documentation. No production mutation is authorized by this proposal.
