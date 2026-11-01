## Why

The migration targets the earlier develop snapshot, while upstream now develops
on `dev` and has added a GitHub metadata bridge, vocabulary expansion, dashboard
interaction, unchanged-save handling, permission controls and deployment fixes.
Closing the migration against the old snapshot would omit supported features.
See the [revision-specific review](../../../../docs/frontend-migration/upstream-dev-review.md).

## What Changes

- Reconcile upstream `dev` at `400bbe32bbdc5396356b35a8f8b4040a731978e5` with the
  existing migration, preserving its schema-driven UI and native route owners.
- Add an optional GitHub metadata import/review workflow to the native editor,
  with a protected server adapter, reviewed draft merging and explicit save.
- Activate the expanded licence/community vocabularies through the shared
  descriptor; verify already-equivalent Android/iOS, cost and accessibility values.
- Incorporate unchanged-save semantics, remaining dashboard interaction and user
  picker improvements through existing services and components.
- Reconcile environment parsing, immutable production packaging, taskrunner,
  proxy routing and CI while retaining reversible ownership and persistent data.
- Keep the corrected publication presentation and upstream 2026 citation.

## Baseline and dependencies

Implementation remains in `develop-migration/`, based on the dirty migration atop
`9faec5b3b660498fdef9736e65e331728b55f99c`. Do not blindly merge or reset it.
Historical evidence stays pinned until integration tests establish a new accepted
baseline. Recheck the upstream head at implementation start and document any
additional delta; a moving branch is not an acceptance identifier.

Depends on completed schema-driven UI, search parity, public pages and the editor,
account/session foundations. Implement before record/domain management and final
polish. Coordinate domain-picker acceptance with management without duplicating
domain CRUD. Readiness/removal remain separate gates.

## Capabilities

### New Capabilities

- `github-metadata-import`: authenticated repository metadata suggestions,
  schema-derived review and safe application to an unsaved resource draft.
- `upstream-dev-alignment`: reviewed upstream behavior/vocabulary/configuration
  integration with compatibility, baseline evidence and rollback.

### Modified Capabilities

None. Existing migration contracts continue to apply; this proposal adds the
missing upstream behavior rather than weakening their completed requirements.

## Impact

Shared schema/options and write services, Django browser transport, Vue resource
editor/search/user pickers, both proxies, service configuration, image builds,
CI, tests and migration inventory. No production activation, GitHub write-back,
automatic overwriting of curated metadata, or legacy deletion is included.
