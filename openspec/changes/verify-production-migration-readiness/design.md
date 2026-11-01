## Two Gates, No Circular Dependency

The user authorized legacy source removal on 2026-11-01 before the remaining
checks; tasks in sections 1-3 remain release requirements. Functional route parity and experience
acceptance must be complete, and every retained asset/helper must have a recorded
destination. Remaining legacy build/proxy/service references are an enumerated
cleanup set, not undiscovered functional dependencies.

The existing remove-legacy-angularjs-frontend change then implements cleanup and
its clean-stack tests. Final readiness = section 4, repeated against that actual
legacy-free artifact. Neither a proposal nor a pre-removal pass certifies the
cleaned release. Final readiness completion produces a go/no-go recommendation;
production deployment still requires explicit operator approval.

## Configuration and Providers

Inventory production-like Caddy/runserver and Apache settings, canonical origin,
TLS/forwarded-host trust, allowed hosts, debug flags, session/CSRF cookie settings,
trusted origins, secrets, static/media serving and security headers. Reuse existing
platform configuration rather than inventing a secret-management system.
Move production-used session/EDAM/search/editor helper URLs away from prototype
naming, preserve required compatibility, and disable/exclude demo pages from the
production route surface. No production journey may depend on a demonstration
counter or preview landing page.

Use authorized test accounts and a configured ORCID environment to exercise real
login/connect/disconnect/cancel/error paths with correct callback origins. Exercise
real test-mail verification/reset links on the intended public origin. Missing
credentials/provider access remain an explicit incomplete gate; fixtures do not
satisfy it. Do not log tokens, credentials or private account data.

## Security, Indexing and Performance

Check authentication/authorization boundaries, CSRF, safe redirects, content
escaping, private cache headers and unchanged external token API use. Verify
robots, sitemap, canonical URLs, redirect aliases and crawler responses through
both proxies. Preview stays noindex; the production indexing policy is explicitly
recorded, never copied from the deny-all preview by accident.

Agree concrete latency/error/query-count budgets before measurement and record
dataset size, concurrency, hardware, build and cache state. Use representative
registry-shaped data and expensive search/domain/detail/editor paths. Small seed
fixture timings are not full-registry load evidence. Do not invent pass thresholds
after observing results.

## Release and Rollback

Document build/collectstatic/start commands, required environment and artifact
identifiers, migrations if any, database/index/media backup and restore checks,
route/error/session/write observability, smoke tests and rollback triggers.
Selective route rollback through both proxies was rehearsed before deletion.
After deletion rehearse restoration of the prior deployable release and its compatible
configuration; a removed Angular container cannot be enabled by a flag.
Do not destroy existing data volumes or imply an untested backup can be restored.

Final gate builds from the proposed cleaned source without legacy service/assets
or warm legacy volumes. CI must execute the modern production build and relevant
backend/public API/browser contracts. Compare backend, modern unit/type/build,
full browser/deep-link/native fallback and static/media/admin results. Update
the audit and handover with failures, exclusions and approval status.

## Non-Goals

No automatic production deployment, real-user credential use, destructive
production test, blanket infrastructure replacement or fabricated provider/load
verification. Required unavailable checks remain unchecked.
