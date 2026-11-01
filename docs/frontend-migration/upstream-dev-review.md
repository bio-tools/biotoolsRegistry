# Upstream dev review: 2026-10-24

Compared the upstream tree at
[`400bbe32bbdc5396356b35a8f8b4040a731978e5`](https://github.com/bio-tools/biotoolsRegistry/tree/400bbe32bbdc5396356b35a8f8b4040a731978e5)
with the migration baseline `9faec5b3b660498fdef9736e65e331728b55f99c`, then
checked the relevant current migration implementations. `git ls-remote --heads`
and `git fetch --no-tags origin dev` confirmed the remote `dev` head. Its latest
commit is dated 2026-10-08. The remote now has `dev`, `main` and `old_develop`;
there is no current `develop` branch. Fetch did not merge, reset or switch the
dirty implementation checkout.

The remote dev head was reconfirmed unchanged on 2026-10-25.

The repository is shallow. This is an exact tree/content comparison, not a claim
that every commit listed by `HEAD..dev` is new or that history is unrelated.
`git diff --stat 9faec5b3 400bbe32` reports 54 changed paths. Historical migration
evidence remains tied to its original baseline until the new change is accepted.

## Findings and dispositions

| Upstream change and source | Difference from the current migration | Required disposition |
| --- | --- | --- |
| GitHub import/review: `frontend/js/bridge.js`, `toolEditBridgeReview.html`, `toolEditBridgeConfirm.html`, editor/controllers/app/services wiring | No native bridge workflow. This is repository-to-draft metadata import, distinct from the older `biotools_to_github.py` ecosystem/export code. | Add native import, review, keep/replace/selective merge, confirmation and discard using the existing editor. Applying suggestions changes a draft; saving remains a separate authorized action. |
| Bridge infrastructure: `.env.example`, both Compose files and proxies | Upstream adds `anitamnd/bridge:latest`, `GITHUB_TOKEN`, `HUGGINGFACE_TOKEN` and POST `/github-to-biotools`. Current generic detail routing would capture that path. | Verify/pin the service contract and image, keep credentials server-side, reserve the exact route and mediate browser calls through session/CSRF checks. Retain a disabled/unavailable mode. |
| SPDX vocabulary: `backend/elixir/licenses.py`, `update_licenses.py`, selected XSD, serializer, editor options and validation fixtures | Activated migration descriptor accepts 435 licence values; upstream backend and XSD agree on 725, adding 290 and removing none. | Activate the new vocabulary through the shared schema descriptor/validator pipeline. Preserve deprecated/non-SPDX historical values and review updates; do not restore copied frontend enum catalogues. |
| Six ELIXIR communities in `resource.py` and editor options | Cancer Data, Food and Nutrition, Microbiome, Research Data Management, Single-cell Omics and Toxicology are absent from the current descriptor. | Reconcile selected schema and registry policy, regenerate the descriptor and prove editor/search/detail/API consistency. |
| Latest `directives.js` options: Android/iOS, cost, accessibility | Already represented by the activated migration descriptor, including both mobile operating systems and the three cost/accessibility values. | Verify equivalence with fixtures; do not implement them twice or replace nested filters with upstream's flat catalogue. |
| Dashboard search: `toolListDashboard.html`, shared `toolCard.html`, `directives.js`, list/results templates, dashboard/details-bar/footer CSS | Native workspace already has a sidebar, cards/table, nested filters, URL history and facets. Upstream additionally supplies searchable used-term option lists and toggles an active value off on repeat selection. | Map observable behavior into the existing workspace and close actual gaps. Verify domain/query scoping, option filtering, active-value toggling, paging, and any retained display preferences. Check upstream `inputData`/`outputData` against supported canonical query names rather than copying invalid aliases. |
| Unchanged saves: `_payload_fingerprint` in `backend/elixir/view/resource.py`, `version_hash`, controller feedback and PUT tests | Native save path does not expose upstream's `no_changes` result. Upstream hashes normalized data and skips subsequent identical PUTs after the hash is established. | Add consistent unchanged-save behavior to shared write handling and native feedback without skipping authorization, validation, stale-edit checks, or meaningful ordered changes. |
| Record/domain user pickers: `permissionsController.js`, `subdomainController.js`, permission/domain templates and CSS | Native record permission/request workflows already exist; domain management is still planned. Upstream adds keyboard navigation, empty/error states, duplicate exclusion and stale-response protection. | Reconcile existing controls; close remaining domain-picker behavior in management using the established policy. `requestsController.js` changes are formatting/comment-only after whitespace normalization. |
| Publication enrichment: `publication_metadata.py` | Upstream fixes the `save_publication_data` argument mismatch. The migration already has the corrected signature plus bounded HTTP timeouts. | Preserve both; add characterization if shared save changes touch enrichment. Do not replace the safer local code wholesale. |
| New citation: `frontend/components/about/about.html`, commit `76dcbc7` | Adds Mendes et al. (2026), DOI `10.1093/nar/gkag420`. | Adopted during the publication-display correction in this task; verify retention in later reconciliation. Older citations remain. |
| Environment configuration: `settings.py`, `.env.example`, INSTALL/README | Correct boolean parsing replaces `bool('False')`; upstream removes deployment/blacklist module imports and `ADMIN_EMAIL_LIST` configuration. | Adopt explicit environment parsing while auditing actual consumers and providing compatibility/migration guidance for removed settings. Preserve browser-session, cutover, schema and ORCID policies. |
| Packaging/CI: root multi-stage Dockerfile, Dockerfile.dev files, Compose, Gulp/dependency changes and API workflow | Upstream builds a combined production artifact, changes service names, removes production source mounts, changes taskrunner packaging and separates API CI from frontend startup. Migration has its own modern build, static assets and proxy switches. | Reconcile packaging to include both retained legacy and modern assets until retirement; verify Python/mod_wsgi compatibility, API CI, taskrunner and persistent volumes. Preserve modern unit/type/schema checks and test-build isolation. Do not copy Node 11 or volume-deleting cleanup into local/operator commands. |

The licence comparison parsed the fetched Python constants and XSD and compared
them with `resource-ui.generated.json`; it did not execute the upstream updater.
No automatic SPDX or schema download/activation was performed.

## Bridge contract observed in this repository

Upstream posts `{owner, repo, biotoolsID?}` to `/github-to-biotools`. It accepts
an object or a JSON-encoded object response, presents grouped current/suggested
values, preserves review choices while switching tabs, and confirms selected
changes before applying them to the editor. It has loading/error/empty-result
states, raw-result inspection and discard. No save is implied by apply.

The upstream field catalogue covers name, description, homepage, versions,
licence, collections, topics, operating systems, languages, function blocks,
links, downloads, documentation, publications and credits. Its explicit forbidden
list includes identifiers, ownership, dates, validation/status/badge fields and
permissions. The replacement must derive field support/labels from the activated
descriptor plus server policy, not translate that hard-coded JS list verbatim.

Review risks found by reading source, not by running the external service:

- The GitHub regex is not an exact host validator; validate URL structure and
  owner/repository segments before calling the service.
- Function deduplication keys only on operation URIs. Equal operations can have
  different inputs, outputs, formats, notes or commands; merging must preserve
  distinct annotations and all untouched metadata.
- The proposed service image is a mutable `latest` tag. Its implementation,
  request limits, model/provider behavior and precise failure contract are not
  contained here. Pin and verify them before activation; use deterministic
  recorded/stub responses for routine tests, not live tokens.
- A direct proxy exposes a service independently of Django's browser policies.
  The native adapter must enforce authentication, CSRF, permissions, bounded
  requests and protected-field exclusion before suggestions reach a writable
  draft. Unknown/incompatible fields must be visibly rejected, not silently lost.
- Upstream save canonicalization sorts and deduplicates every list. The native
  editor intentionally supports ordered repeated items; blanket normalization
  would hide legitimate changes. Characterize set versus sequence semantics.

## Scope and sequencing

[`adopt-upstream-dev-features`](../../openspec/changes/archive/2026-10-29-adopt-upstream-dev-features/proposal.md)
owns the integration and regression evidence. Run it before
`migrate-record-and-domain-management`, then final polish/readiness/removal.
It reuses completed schema/editor/search/account work; it does not rerun or erase
their historical changes. Native domain CRUD remains management work, with the
upstream picker behavior added to its acceptance input.

Only the publication layout and 2026 citation were implemented in this task.
The bridge, new vocabulary, save handling and packaging are proposed work.
No bridge service was started, no credentials were requested, no repository was
sent to a provider, and no production deployment or upstream merge was performed.

Follow-up on 2026-10-27: the proposed integration now has a separate
[local acceptance record](upstream-dev-integration.md), including native bridge,
vocabulary, save handling and packaged-build evidence. The statements above
describe the original review checkpoint; production deployment remains separate.
