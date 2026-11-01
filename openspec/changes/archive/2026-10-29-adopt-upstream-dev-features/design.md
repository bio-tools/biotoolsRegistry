## Integration boundary

Use the [54-path upstream review](../../../../docs/frontend-migration/upstream-dev-review.md)
as the starting disposition matrix. Classify each behavior as already equivalent,
implemented here, or explicitly assigned to an existing later change. A CSS or
Angular implementation difference alone does not require a second native feature.
Preserve local data-preservation guards, bounded enrichment calls, active schema
policy, native routing and independent rollback switches.

## GitHub import

Use the existing resource editor for create/edit. Accept a public GitHub repository
URL and identify the owner/repository with URL parsing and exact host validation.
Reject credentials, look-alike hosts and invalid segments; define handling of
`.git`, trailing slash and repository subpaths in contract tests.

Provide a same-origin Django POST adapter for the upstream `/github-to-biotools`
contract, reserved ahead of tool IDs/crawler handlers on both proxies. The adapter
checks the browser session, CSRF and permission to create/edit the target record.
Send only owner/repository and the permitted optional tool ID, not the full draft,
private permission data or user credentials. Keep provider tokens in service
configuration. Bound input/output size, timeout and concurrent/rate-limited use;
define disabled, busy, timeout, upstream error and malformed-response states.
Keep the bridge optional so ordinary manual editing works without it. Pin the
verified image revision/digest and document token/provider configuration.

Bridge output is untrusted input. Parse object/JSON-string responses once, then
validate against the active descriptor and authoritative writable-field policy.
Ownership, IDs, permissions, registry state and read-only enrichment cannot be
overwritten, including through nested objects. Unknown or incompatible suggestions
are explained separately and do not silently disappear into a partial save.

Review shows current and suggested values grouped by descriptor labels, including
nested annotations. Existing curated values default to keep. Support replace and
selective list merge, keep-all, discard, pending-change count and escaped raw
output. Reconcile review against the latest local draft when tabs/values change;
stale provider responses cannot replace newer results. If selected values changed
since review, require review of the new comparison before applying.

Apply is an explicit, previewed change to the draft only. Reuse editor conversion,
stable repeated-item identities, dirty state, recovery/export and validation.
Never deduplicate function blocks only by operations or nested records only by a
partial key; preserve distinct IO/format/note/command/type/version data. Cancel,
discard or failure leaves the draft untouched. Persistence uses the normal save
path, including current permissions and optimistic concurrency checks.

## Schema and upstream behavior

Adopt the upstream licence source/XSD through reviewed backend schema activation;
keep old/deprecated and four non-SPDX values. Reconcile the six new communities
with registry policy. Regenerate/check descriptors; verify native controls,
detail and search plus JSON/XML validation without new frontend option lists.
The SPDX updater remains an explicit maintenance action, never page-load fetches.
Replace upstream Angular-array consistency assumptions with descriptor/API/UI
contract tests. Existing mobile OS/cost/accessibility coverage is evidence to
retain, not a second implementation.

Implement unchanged-save detection once in shared write handling, after normal
authorization/validation/concurrency checks. Keep the existing upstream response
meaning (`no_changes`) compatible for public clients and expose clear native
feedback. Do not alter timestamps/history/indexing/notifications for a genuinely
unchanged update. Characterize first-save/null-hash behavior and align subsequent
saves; test meaningful field changes, permission updates and concurrent edits.
Only schema/policy-defined sets may ignore order; ordered repeated annotations
and significant duplicates must not be normalized away by a generic list sort.

Map upstream dashboard behavior to the existing nested filter workspace. Verify
searchable used-term options, active-value clearing and domain/query scoping;
retain browser history, native GET fallback and supported comparison. Document
display-preference compatibility rather than adding a second dashboard runtime.
Reuse record permission/request controls. Carry keyboard/stale-response/duplicate
and failure behavior into domain management's existing user-picker work.

## Runtime and packaging

Adopt explicit true/false environment parsing with regression checks for old and
new supported values. Inventory consumers of removed deployment/blacklist module
imports and ADMIN_EMAIL_LIST before changing configuration behavior; document a
compatible migration path. Preserve configured ORCID/email and browser policies.

Build one reproducible production artifact with modern assets, retained static
content, backend code and any still-required legacy assets. Reconcile service
renames, taskrunner, Python/mod_wsgi ABI and proxy rules; verify builds without
host source mounts. Upstream's Node 11 builder is not a suitable replacement for
the current modern build. Keep existing modern type/unit/schema checks while
decoupling API CI from frontend startup. Scope destructive CI cleanup to disposable
CI projects; never purge local/production data volumes. Legacy deletion remains
owned by retirement after management and readiness complete.

## Verification and rollback

Use deterministic bridge responses for create/edit, invalid URLs, unknown fields,
provider failure, cancellation, repeated requests, protected fields, exact and
near-duplicate nested values, stale drafts and permissions changing during review.
Test apply without persistence, then explicit authorized save and reload through
both proxies. Include keyboard/mobile review, failed assets and disabled bridge.

Run schema activation/rollback, backend/API save and permission tests, modern
tests, search/detail/editor/account journeys and production-like image/proxy smoke
checks. Record exact registry and bridge revisions plus configuration, results
and known limitations. Rehearse disabling the bridge and reverting the integration
without losing saved records or drafts. Live provider activation and production
deployment require their existing readiness/operator process, not this proposal.
