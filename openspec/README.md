# Frontend migration changes

On 2026-10-29, 23 completed changes were archived under
[`changes/archive/`](changes/archive/) and their capability requirements were
consolidated under [`specs/`](specs/). On 2026-10-30 the workflow designer and
draft/sharing changes were also archived after their local verification. The
experience-acceptance, workflow-matching and workflow-acceptance changes were
archived on 2026-10-31 after user review and real-data verification. Legacy
removal was archived on 2026-11-01 after local verification. Production readiness
is the remaining open change; deployment still requires its separate checks.

## Finishing Sequence

Status on 2026-10-15: the 17 earlier changes through
`cut-over-migrated-routes` are complete for their recorded incremental scope.
That is not all-route parity or production approval. The
[legacy-removal audit](../docs/frontend-migration/legacy-removal-audit.md)
found active dependencies B01-B12 and stopped deletion at that time.

The first finishing change, `migrate-account-pages`, is complete for its local
scope; see [account-page evidence](../docs/frontend-migration/account-pages.md).
The second finishing change, `add-schema-driven-resource-ui`, is also complete
for local acceptance. The third, `complete-search-filter-parity`, is complete
for its local functional scope. The fourth, `migrate-public-information-pages`,
is complete for local acceptance. The upstream integration,
`adopt-upstream-dev-features`, and record/domain management are also complete for
local acceptance. Experience acceptance and legacy removal are complete locally;
release readiness remains open:

2026-10-21 update: schema-driven runtime controls, shared choices, public
projection and compatibility checks passed local acceptance.
The [schema evidence](../docs/frontend-migration/schema-driven-ui.md) records
passing regressions and the completed same-build activation/rollback rehearsal
through both proxies, including persistence of a newly advertised nested field.
Production readiness and legacy deletion remain separate gates.

2026-10-22 update: all 61 supported search filters, domain membership, native GET
results and comparison passed local acceptance. See the
[search compatibility matrix and evidence](../docs/frontend-migration/search-filter-parity.md).
The explicit rollback remains; saved legacy grid layout preferences are tracked
for polish/retirement review, not silently declared removed.

| Order | Change | Exit condition |
| --- | --- | --- |
| 1 (complete) | [migrate-account-pages](changes/archive/2026-10-29-migrate-account-pages/proposal.md) | Native account pages and permanent session helpers verified locally; configured live provider/email remain readiness gates. |
| 2 (complete) | [add-schema-driven-resource-ui](changes/archive/2026-10-29-add-schema-driven-resource-ui/proposal.md) | Compatible activated schema/vocabulary changes reach editor/detail/search metadata without frontend edits or rebuilds; incompatible changes are gated. |
| 3 (complete) | [complete-search-filter-parity](changes/archive/2026-10-29-complete-search-filter-parity/proposal.md) | Supported bookmarked filters, domains and native GET search work without legacy fallback. |
| 4 (complete) | [migrate-public-information-pages](changes/archive/2026-10-29-migrate-public-information-pages/proposal.md) | Native public pages, domain directory, statistics, redirects and errors verified through both proxies with independent rollback; external destination failures recorded. |
| 4a (complete) | [adopt-upstream-dev-features](changes/archive/2026-10-29-adopt-upstream-dev-features/proposal.md) | Pinned dev features, native GitHub bridge, vocabulary/save/runtime compatibility and rollback verified locally; live provider activation remains optional and untested. |
| 5 (complete) | [migrate-record-and-domain-management](changes/archive/2026-10-29-migrate-record-and-domain-management/proposal.md) | Native record/domain commands, JSON validation, user picker, workflow/media inspection and independent rollback verified locally. |
| 6 (complete) | [polish-and-validate-migrated-experience](changes/archive/2026-10-31-polish-and-validate-migrated-experience/proposal.md) | Cross-page visual/accessibility acceptance, responsive tool entries and function diagrams are verified. |
| 7a | [verify-production-migration-readiness](changes/verify-production-migration-readiness/proposal.md), task sections 1-3 | Configured provider/email, security/indexing, performance and rollback checks pass before release. |
| 8 (complete) | [remove-legacy-angularjs-frontend](changes/archive/2026-11-01-remove-legacy-angularjs-frontend/proposal.md) | Legacy source and services were removed; local clean-stack regression checks passed. |
| 7b | [verify-production-migration-readiness](changes/verify-production-migration-readiness/proposal.md), task section 4 | Actual cleaned artifact passes final verification and has an operator handover. |

## Workflow Design Sequence

The 2026-10-29 workflow-design proposals add a separate product capability. At
the user's request, implementation proceeded while the current frontend
experience review remains open. They do not change the historical scope
of the completed workflow-image migration, authorize deployment or require legacy
removal to happen first. If included in a release, production readiness must also
cover the completed designer and its data/security contracts. Existing image
workflows remain available until an explicit separate retirement decision.

| Order | Change | Exit condition |
| --- | --- | --- |
| 1 (complete) | [add-workflow-tool-matching](changes/archive/2026-10-31-add-workflow-tool-matching/proposal.md) | Matching passed a real-corpus oracle, agreed local performance budgets and user acceptance of live-scan behavior. |
| 2 (complete) | [add-workflow-designer](changes/archive/2026-10-30-add-workflow-designer/proposal.md) | Editable step graph and existing gallery verified locally; broader visual and accessibility acceptance remains separate. |
| 3 (complete) | [add-workflow-drafts-and-sharing](changes/archive/2026-10-30-add-workflow-drafts-and-sharing/proposal.md) | Private revision-protected designs, deliberate revocable sharing and non-executable import/export verified locally. |
| 4 (complete) | [validate-and-polish-workflow-designs](changes/archive/2026-10-31-validate-and-polish-workflow-designs/proposal.md) | Representative matching, usability, recovery, accessibility and user-facing acceptance evidence; screen-reader and independent security review remain release limitations. |

Workflow designs are planning artifacts. Executable workflow generation, export
and execution are explicitly out of scope, not deferred implementation tasks.

2026-10-24 update: public-page migration passed local acceptance, including
no-JavaScript/mobile journeys, retained content images, explicit redirects,
statistics failure states and public-only rollback. See the
[public-page inventory and evidence](../docs/frontend-migration/public-information-pages.md).
Existing external shortcut failures need content-owner review before production
readiness; original targets and explicit rollback remain available.

2026-10-25 update: upstream now uses `dev`; its confirmed head is
`400bbe32bbdc5396356b35a8f8b4040a731978e5`. The
[upstream review](../docs/frontend-migration/upstream-dev-review.md) identifies
the GitHub metadata bridge, vocabulary expansion, unchanged-save handling,
dashboard/picker changes and deployment/CI updates. The new integration proposal
is open; fetching/reviewing it did not merge or replace the migration baseline.
Publication presentation and the 2026 bio.tools citation are corrected already.

2026-10-27 update: upstream integration passed local acceptance. The
[integration record](../docs/frontend-migration/upstream-dev-integration.md)
records the pinned provider contract, expanded shared vocabulary, unchanged saves,
search interaction, source-free packaged build and same-build schema rollback.
Both proxies passed 33 affected browser checks and three import journeys each;
106 modern tests and 49 focused backend tests on each runtime passed. The preview
has been restored to provider-disabled manual editing. This accepts the reviewed
dev behavior without merging the upstream branch or authorizing deployment.

2026-10-28 update: management passed local acceptance. The
[2026-10-28 management evidence](../docs/frontend-migration/record-domain-management.md)
records current-owner authorization, native forms, JSON draft preservation,
real-index/browser checks and configuration rollback. Concurrent domain creation
and ambiguous database/index outcomes remain explicit production-readiness inputs.

2026-10-29 readiness progress: permanent EDAM lookup and production demo
isolation passed local checks. Concurrent domain creation is serialized by an
additive migration, and ambiguous index outcomes were rehearsed and documented.
See [readiness evidence](../docs/frontend-migration/production-readiness.md).
The user accepted the interface on 2026-10-31. Outstanding release and final
checks remain open after the authorized source removal.

The user authorized source removal before the remaining checks on 2026-11-01.
Final readiness verifies the cleaned artifact. Production deployment is a
separate operator action; creating these proposals does not authorize it.

The migrated checkout was moved to the repository root on 2026-11-01. Historical
records mentioning `develop-migration/` refer to its former location.
Schema-driven UI work is independent of account pages, but must precede the new
search/management work and final polish. Automatic propagation means updates to
the activated backend contract, not unreviewed upstream production changes.
Reuse existing session, query, schema editor, EDAM, permission and request
contracts. Do not rerun completed changes just to close scope they did not claim.
The removal audit, source cleanup and local regression checks are recorded;
production readiness remains incomplete.

## Earlier Milestones

The notes below describe the historical scope at each milestone. Where they say
canonical cutover is still pending, the later
[route ownership evidence](../docs/frontend-migration/route-ownership.md)
supersedes that statement for detail, supported search, editor, requests and accounts.
The remaining route families are owned by the finishing sequence above.

All changes target upstream `bio-tools/biotoolsRegistry` **develop**, pinned at
`9faec5b3b660498fdef9736e65e331728b55f99c`. See the
[baseline and impact matrix](../docs/frontend-migration/baseline.md).

**refresh-develop-migration-baseline is complete** in the separate
`develop-migration/` checkout. The inventory, browser harness, Django shell and
htmx foundations were revalidated on develop; see the
[evidence and preview runbook](../docs/frontend-migration/develop-refresh.md).
Continue the original feature dependencies there; route cutover and legacy
removal remain separate final gates.

`extract-shared-query-services` is also complete on this baseline. See the
[shared service contracts and verification](../docs/frontend-migration/shared-query-services.md).

`migrate-public-tool-detail` adds the isolated, server-rendered
[tool detail prototype](../docs/frontend-migration/public-tool-detail.md).
Canonical route cutover remains a later change.

`add-vue-island-runtime` adds typed, explicitly mounted Vue components with
safe JSON props and htmx teardown/insertion support. See the
[runtime convention and demo](../docs/frontend-migration/vue-island-runtime.md).
That runtime change includes no search/editor functionality or visual redesign.

`add-vue-search-workspace` is complete under the isolated HTML mount. See the
[search prototype, contract and verification](../docs/frontend-migration/search-workspace.md).
Its search checks pass through both proxies; a remaining legacy Caddy login-page
timeout is documented. Canonical `/t` remains legacy-owned.

`add-advanced-search-filtering` is complete with bounded candidate-local filters and explicit
full-set promotion with reproducible server URLs. See the
[advanced filter contract, score fixtures and verification](../docs/frontend-migration/advanced-search-filtering.md).
No production scoring model or canonical route cutover is included.
Its final browser runs passed all 31 tests on both Apache and Caddy; the earlier
intermittent legacy login timeout did not recur in these runs.

`add-edam-selector` is complete with a reusable scoped, keyboard-accessible EDAM selector,
adopted by advanced topic filtering and an ordinary annotation preview form.
See the [component contract and preview](../docs/frontend-migration/edam-selector.md).
Selections submit validated IDs; the preview does not write registry records.

`add-resource-editor-data-contract` is complete with serializer-derived draft types,
lossless local conversion, explicit submission normalization, stable repeated-item
IDs and snapshot-based validation paths. See the
[data contract and known backend limitations](../docs/frontend-migration/resource-editor-data-contract.md).
This is data-only; the visual editor remains a subsequent change.

`migrate-browser-authentication` is complete with session-backed login/logout,
server-protected account pages and shared CSRF/session recovery for native forms,
htmx and Vue. Existing token API and legacy account routes are retained. See the
[authentication contract and verification](../docs/frontend-migration/browser-authentication.md).
Configured ORCID integration remains explicitly pending; deterministic recovery
token and social-account permission tests pass.

`migrate-resource-editor-basic` adds session-protected creation and basic editing,
authoritative validation, stale-version checks, draft recovery/export and
transactional checks for preservation of hidden metadata. See the
[basic editor preview and limits](../docs/frontend-migration/resource-editor-basic.md).
Known unsafe replacement cases remain blocked; nested editing and canonical
route cutover are separate changes.

`migrate-resource-editor-nested` is complete with schema-shaped function,
operation, input/output, data/format, note and command controls. Stable local IDs
keep values and errors attached during keyboard reorder; rich round trips retain
unrelated metadata. See the [nested editor preview and schema review](../docs/frontend-migration/resource-editor-nested.md).
Existing replacement limitations remain guarded; canonical cutover is still separate.

`migrate-resource-editor-metadata` completes the remaining controls before
authenticated editor cutover. The [schema coverage audit](../docs/frontend-migration/resource-editor-schema-coverage.md)
accounts for all 26 top-level fields, including the 19 newly implemented metadata
fields. Known preservation blockers and registry-only workflow review still gate
editor cutover; control coverage is not full production workflow parity.

The original worktree and its `a1fc8b9` evidence remain intact. Do not implement
subsequent features against that older application tree.
