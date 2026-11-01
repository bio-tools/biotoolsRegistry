# Workflow design acceptance

The workflow prototype is available at `http://localhost:8003/workflows/design/`; `/workflows` remains the existing image gallery. On 2026-10-31 the user reviewed it and responded “Yes, accept the workflow designer” for its appearance and workflow-building experience. This is user-facing acceptance; it does not imply production release or completion of the remaining technical checks.

## Evidence so far

- Deterministic tests independently construct several functions and input/output records, including different functions and different IOs on one resource, and check that matches do not combine them. Tests cover current, related, obsolete, unknown and conflicting EDAM terms, operation filters, hidden records, cursor bounds and changed vocabularies.
- Graph tests cover branches, cycles, duplicate instances, missing endpoints, uncertain connections, portable extensions and invalid imports. Draft tests cover ownership, CSRF, concurrent and stale revisions, retrying creation, hidden or deleted records, share revocation and preservation of original hidden snapshots. Coordinated database tests also check that shared reads are ordered with concurrent hiding and revocation.
- Apache and Caddy browser journeys exercise data and operation selection, duplicate steps, a branch, cycle prevention, editing and removing connections, desktop and mobile reflow, 200% zoom, keyboard focus, draft download/restore, changed snapshots, matching failure and unavailable assets. Signed-in browser journeys save and share a connected design, copy it, revoke access and recover after session expiry. The reviewed local captures are [desktop](evidence/workflow-branch-desktop.png), [mobile](evidence/workflow-branch-mobile.png) and [200% zoom](evidence/workflow-zoom-200.png); `tests/browser/workflow-designer.spec.js` regenerates them in the test-results directory.
- The fixture-heavy local database has 421 visible resources, of which 106 have functions. A separate, anonymized 500-record public API sample was compared with an independent structured-data oracle, including missing annotations. Its five clustered pages are not a random or production-sized corpus; coverage, method and live-scan limits are in [workflow matching](workflow-tool-matching.md).
- An opt-in isolated rehearsal repeated that sample to 35,000 resources and measured strict, uncertainty-inclusive and four concurrent first-page requests. It found and helped remove a severe pagination bottleneck; results and limitations are documented in [workflow matching](workflow-tool-matching.md).
- A later 34,519-record anonymized public crawl was compared with a structured
  oracle using the preview's real EDAM 1.25 vocabulary on both Python runtimes.
  Input, output, operation-filtered and sparse uncertainty scans passed the
  user-accepted local budgets. The crawl is live rather than a snapshot, and
  its vocabulary is not asserted to match the live deployment.
- Forty-five matching and draft tests passed on each Python runtime, including
  owner isolation, CSRF, revision conflicts, hidden resources, share revocation
  and coordinated shared-read races. A code review checked the read-only share
  endpoint, token hashing, graph validation, redaction and locking. This local
  review is not an independent external security assessment.
- Twelve browser checks passed through the packaged Apache image behind HTTPS,
  and eleven passed through the native Caddy/Django rehearsal. They covered
  matching, desktop/mobile branching, 200% zoom, keyboard control, failed assets,
  changed snapshots and draft save/copy/share/revoke and session recovery.
  The current desktop and mobile branch screenshots were inspected; the user
  accepted the designer's appearance and workflow-building experience.

## Acceptance criteria

- Matching must preserve the identity of each function and input/output, apply
  operation filters to the same function, distinguish unknown and conflicting
  annotations, and agree with an independent structured-data oracle. Report live
  pagination and permit the user to restart when the registry changes.
- On desktop and mobile, a keyboard user must be able to select terms, add and
  connect functions, inspect the same connections in the diagram and list, and
  recover a draft. At 200% zoom, controls and status messages remain available;
  long annotations and intentional diagram scrolling must not hide controls.
- Saving and sharing require the appropriate owner/session and CSRF protections;
  stale revisions, revoked links and hidden or removed resources must not expose
  private data or silently discard the draft. Failed assets, expired sessions and
  unavailable matching/ontology data must have recoverable, explicit states.
- The user-accepted local page, concurrency and oracle budgets are recorded in
  [workflow matching](workflow-tool-matching.md#full-corpus-rehearsal-2026-10-31).
  Screen-reader review is performed when the necessary environment is available;
  keyboard checks are not described as a substitute for it.

## Remaining release limitations

The user's visual and workflow acceptance and the local functional checks are
complete. Orca is installed locally, but no isolated virtual display was
available for a screen-reader session, so the keyboard tests are not a substitute
for screen-reader review or comprehensive WCAG conformance. An independent
sharing security review, real deployment performance and configured production
checks remain release-readiness work. Executable workflow export and execution
are outside the requested scope.
