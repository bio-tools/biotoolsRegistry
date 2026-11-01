# Migrated experience review

Status: **in progress**, 2026-10-29. User-facing visual approval and the full
cross-page acceptance have not yet been obtained. This is not a release gate.

The current reference is the develop bio.tools logo and blue shell (`#005472`),
with legible text, visible keyboard focus and the existing schema-driven data
contract. The local changes compact the header, align native forms and search
cards, make record metadata easier to scan, and show each function as connected
input, operation and output cards. The diagram stacks in the same order on a
small screen. The editor retains schema-driven controls and its existing diagram.

Search filter labels now use active schema labels and indexed field paths when
labels repeat; they are not a fixed list of schema fields. All currently active
filter labels were checked for uniqueness. Table column choices, order and widths
are saved locally, and old UI-grid preferences are read without modifying the old
stored value. Older operation/input/output columns restore as independently
selectable columns. Their labels and content come from the active schema's
public function fields; other public function fields can also be selected.

## Evidence so far

- Frontend: 112 unit/component tests, type checking and production asset build pass.
- Backend: 34 schema/search/detail tests ran on Python 3.13 and Apache's Python
  3.10 after adding separate function columns; 31 passed and three integration
  tests were skipped on each runtime.
- Each proxy passed 13 browser checks covering 13 routes at 1440, 390 and 320
  pixels with JavaScript and without it, plus search bookmarks, filters, tables,
  failed assets, and saved-layout restoration. The detail diagram and keyboard
  skip link also passed a 200% zoom check on each proxy.
- Independent function-column migration and enhanced search were rechecked in
  three browser tests on each proxy after the final column changes. The broader
  journey run passed 56 tests on each proxy; three configured-provider tests were
  skipped there and subsequently passed with the deterministic local provider.
- Same-build schema activation, draft preservation and rollback passed on both
  proxies: `tests/browser/test-results-experience-schema`, evidence in
  `/tmp/biotools-schema-z2xXbc/evidence.json`. GitHub suggestion review, apply,
  explicit save and provider failure passed in three additional tests per proxy;
  artifacts are `test-results-experience-github-{apache,caddy}`. The preview was
  restored to its normal provider-disabled configuration afterward.
- A sparse fictional record with a long unbroken description and URL was created
  on each proxy and checked at 320 pixels with JavaScript disabled. The rich
  `editor-demo` record's two separate functions were checked at 390 pixels on
  each proxy; the resulting images were inspected.
- The visible input/select/textarea/button naming check passed on 13 migrated
  routes on both proxies. Keyboard navigation checked visible focus on the first
  eight stops after main content on search, detail, editor, profile, requests,
  domain, workflow and about pages; the skip link and stacked diagram passed at
  200% zoom. The mobile screenshot review included long URLs and two functions.
  The shared link color was darkened after a contrast check: `#286090` has
  contrast 6.63:1 on white, 6.38:1 on `#f8fbfc`, and 5.97:1 on `#edf4f8`.
  These focused checks do not establish full WCAG conformance; screen-reader
  testing and a comprehensive accessibility audit were not performed.
- Screenshots of desktop and mobile detail pages were inspected. Artifacts:
  `tests/browser/test-results-experience-{apache,caddy}` and
  `tests/browser/test-results-experience-zoom-{apache,caddy}`.
- The initial visual audit used an incorrect account route and was rerun against
  `/profile/email/`; those initial failures were test setup errors.

## User acceptance and remaining limitations

On 2026-10-31 the user reviewed the migrated interface and responded
“Yes, accept the interface.” This completes the user-facing visual acceptance
for this change. Full screen-reader testing and a comprehensive accessibility
audit remain release-readiness work; the local checks above do not certify
complete WCAG conformance. Workflow-designer acceptance is a separate change.
