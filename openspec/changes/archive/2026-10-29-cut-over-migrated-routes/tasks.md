## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Build the route ownership matrix

- [x] 1.0 Include develop Caddy/runserver, production Apache/WSGI, bot/Rendertron provisioning, Vary/noindex headers, API/schema/account routes and static assets in the acceptance and rollback matrix; test both proxy paths before cutover.

- [x] 1.1 Inspect Django URLs, reverse-proxy/Caddy configuration, SPA fallback handling and production Compose/deployment configuration.
- [x] 1.2 Create/update `docs/frontend-migration/route-ownership.md` listing each user-facing route family, current owner, target owner, readiness evidence and rollback.
- [x] 1.3 Select only route families whose migrated acceptance/browser tests currently pass; leave incomplete routes on the legacy owner.

## 2. Cut over verified read-only routes

- [x] 2.1 Cut over the verified public tool-detail route family without affecting API paths.
- [x] 2.2 Run direct-link, refresh, internal navigation and not-found tests through the production-like proxy stack.
- [x] 2.3 Record/verify the rollback switch for the detail route family.

## 3. Cut over the search workspace when ready

- [x] 3.1 Verify primary and advanced search browser tests, URL deep links, Back/Forward, error states and performance bounds.
- [x] 3.2 Route the canonical search path to the Django page containing the Vue search workspace while preserving API endpoints.
- [x] 3.3 Test canonical/legacy URL variants for redirect loops and verify search deep links through the full proxy stack.
- [x] 3.4 Record/verify the rollback switch for search.

## 4. Cut over authenticated editor/auth routes when ready

- [x] 4.0 Complete `migrate-resource-editor-metadata` and review the full schema coverage plus registry-only permission/ownership workflows; basic/nested editor milestones alone do not establish editor parity.
- [x] 4.1 Verify authentication, CSRF, permission, basic editor and nested editor acceptance suites before changing canonical editor routing.
- [x] 4.1a Fix replacement preservation of publication enrichment, badge/homepage status and protected identifiers; retain forged-value and unrelated-loss guards and test both backend runtimes plus the frontend.
- [x] 4.1b Add owner/admin permission controls with existing username lookup; verify grants, revocations, nonowner denial, validation and both proxy paths.
- [x] 4.1c Add session-backed ownership/editing requests and accept/decline; preserve current ownership across resource replacements and verify both proxy paths.
- [x] 4.1d Connect retained browser workflows to session authentication without changing the token API; verify login/logout, expiry, CSRF, account workflows and transport rollback.
- [x] 4.2 Cut over only the authenticated route families whose feature parity is complete: editor/registration and ownership/editing requests. Retain canonical account/provider routes on their existing handlers.
- [x] 4.3 Verify session expiry, direct refresh and mutation behavior through the proxy stack and record rollback.

## 5. Production observability and documentation

- [x] 5.1 Ensure route-level logs/metrics allow identification of new 4xx/5xx patterns and high-latency search behavior after cutover.
- [x] 5.2 Update route ownership documentation after every successful cutover.
- [x] 5.3 Confirm incomplete legacy routes still work and legacy source/build has not been removed by this change.

## Verification and remaining work

Local rehearsal only, on pinned develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
Normal development/production switches remain off by default. On 2026-10-05:

- 125 migration backend tests pass on Python 3.13 and Apache/Python 3.10,
  including disposable Elasticsearch coverage, without skips.
- 82 frontend unit tests, type-check and production asset build pass.
- Apache and Caddy each pass 57 browser tests with both cutover switches enabled;
  four legacy-only discovery cases are intentionally reserved for full rollback.
  Rich canonical detail also passes desktop/mobile no-JavaScript checks.
- On 2026-10-06, detail-only, search-only and full rollback each pass both
  browser/crawler ownership checks on Apache and Caddy (12 checks total).
  Full rollback also passes nine legacy discovery/authentication/proxy scenarios
  on each proxy. Both switches are restored to enabled. The earlier VPN/Docker
  subnet conflict was resolved by the user disconnecting the VPN.
  After restoring both switches, all nine canonical cutover/detail checks pass
  again on each proxy, including desktop/mobile no-JavaScript detail.
- On 2026-10-06/07, the preservation prerequisite removes enriched-publication,
  badge/homepage-status and protected-identifier save blockers after backend fixes.
  Both runtimes pass 130 migration tests; 83 frontend tests, type-check and build
  pass. Unknown fields, forged values and unrelated-data loss still block saves.
  On 2026-10-07, all 21 focused editor/authentication browser checks pass on each
  proxy, including enriched saves and refreshes at desktop/mobile sizes.
- On 2026-10-08, permission controls pass 136 migration backend tests on both
  runtimes, 87 frontend tests, type-check and build, and all 23 focused editor/auth
  browser checks on each proxy. Desktop/mobile screenshots were inspected. Earlier
  connectivity failures cleared after the user disabled the VPN; no host routes
  or security settings were changed.
- On 2026-10-11/12, ownership/editing requests and the retained-browser session
  bridge pass 147 migration backend tests on both runtimes, 87 frontend tests and
  type-check. All 30 focused browser checks pass on each proxy without skips or
  retries, including desktop/mobile ownership transfers after replacement saves.
  Desktop/mobile request screenshots were inspected. Session-transport rollback
  and restoration each pass two authentication/isolation checks on each proxy.
  The bridge is restored to enabled in the disposable preview; normal defaults
  remain off. Tasks 4.1c/4.1d are complete.
- On 2026-10-12/14, canonical editor/request routing passes 152 migration backend
  tests on both runtimes and all 40 focused browser checks on each proxy, with
  no skips or retries. The retained Angular build and both proxy configuration
  checks pass. Desktop/mobile canonical request screenshots were inspected.
  Editor-only rollback and bridge-disabled fallback each pass four checks on
  each proxy; restoration passes six on each proxy. The preview is restored to
  all cutover switches and the session bridge enabled. Tasks 4.2/4.3 are complete
  for the verified editor/request families; canonical account/provider routes
  remain legacy-owned. Live ORCID exchange remains a production verification gate.

See [route ownership](../../../../docs/frontend-migration/route-ownership.md) for
the route matrix, activation/rollback commands, artifacts and measurements.
The local incremental cutover and rollback scope is complete for detail, search,
editor and requests. This is not production approval or a migration of every
account route. Legacy removal remains blocked by the retained routes and fallbacks.
