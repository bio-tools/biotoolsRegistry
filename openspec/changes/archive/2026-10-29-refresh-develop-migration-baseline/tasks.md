## 1. Establish the target

- [x] 1.1 Resolve upstream develop to an exact SHA and document the old baseline, develop/main difference and affected migration areas.
- [x] 1.2 Inventory tracked, untracked and ignored local work; prepare an isolated checkout based on the pinned develop SHA without changing the original worktree.
- [x] 1.3 Run the unmodified develop build/test workflow in disposable services and record pre-existing failures and environment requirements.

## 2. Refresh behavior evidence

- [x] 2.1 Refresh routes, API usage, search behavior, editor behavior and risk register with develop source references and explicit deltas.
- [x] 2.2 Trace dj-rest-auth/allauth, ORCID/account linking, recovery, permissions and active external API credentials; distinguish source facts from configured-provider tests.
- [x] 2.3 Review upstream CI/fixtures and current search/detail/editor/icon/EDAM behavior; update affected acceptance criteria without dropping supported routes.

## 3. Port and verify foundations

- [x] 3.1 Port the existing browser harness and modern asset package; retain upstream legacy build/runtime configuration and test both builds.
- [x] 3.2 Adapt the Django shell for current settings, Caddy/runserver and Apache routing, including bot/Rendertron rules, assets, reverse URLs and error pages.
- [x] 3.3 Revalidate full/fragment responses, history, failure recovery and session/CSRF handling under the pinned develop runtime.
- [x] 3.4 Run focused Django/browser tests and relevant upstream API/permission suites against disposable fixtures; inspect desktop/mobile screenshots and record base SHA, commands, results and limitations.

## 4. Accept the refreshed baseline

- [x] 4.1 Update startup/deployment instructions, fixture/CI prerequisites, route ownership and rollback for the actual develop integration.
- [x] 4.2 Mark the four foundation revalidation tasks complete only after their evidence passes; retain old baseline records and leave unmet gates open.
- [x] 4.3 Validate every OpenSpec change and confirm remaining feature work uses the pinned develop baseline and refreshed inventory.

## Completion evidence

Accepted 2026-09-13 on upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
Implementation is preserved in the separate `develop-migration/` Git checkout;
the original dirty worktree was not switched or reset. See the
[review, results and runbook](../../../../docs/frontend-migration/develop-refresh.md).
Modern and legacy builds pass, as do 24 Django tests per runtime, 16 browser tests
per proxy and 57 API/permission tests. All 17 OpenSpec changes pass strict validation.
Desktop/mobile screenshots and both proxy rollback paths were checked. Provider
ORCID/email and legacy prerender deployment are explicitly not claimed as tested.
