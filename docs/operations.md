# Production readiness

**Status: not ready for production deployment.** The legacy frontend has been
removed and the local checks below passed, but the live deployment has not been
migrated or verified. The remaining tasks are in the [readiness checklist](../openspec/changes/verify-production-migration-readiness/tasks.md).

## Local evidence

- The isolated backend suite passed 433 tests, including live Elasticsearch
  checks. Frontend type checking, the production build and 146 unit tests passed.
  All 120 enabled browser scenarios passed across the main run and corrected
  reruns; 47 environment-specific scenarios were skipped. Public-page keyboard,
  label and viewport checks also passed.
- An isolated same-build rehearsal added, removed and restored schema fields and
  vocabulary terms through Apache and Caddy. The same frontend bundle was used
  throughout, and edited values persisted.
- With 34,519 anonymized public records and EDAM 1.25, the cleaned image matched
  the workflow-search oracle. The broad scan had 290 ms p95 page time, 386 ms
  maximum, and four concurrent first-page requests completed within 622 ms.
  These are local in-process results, not production capacity or an SLA.
- A disposable MySQL/media backup and prior-image restore rehearsal passed. It
  did not verify the actual production backup or identify the deployed image.
- A separate database restore retained active, deleted and physically purged ID
  reservations and rejected reuse. All 30,790 distinct IDs in the local 2024
  SQL snapshot are reserved in the preview. The newer RSEc snapshot refers to
  1,313 additional IDs absent from that preview; reconcile these against an
  authoritative registry history before relying on the preview's reservations.
- A synthetic record was registered in the isolated editor, queued, retried after
  a GitHub server error and exported to a test-only pull request on the fork.
  The prepared schema-validating workflow is not installed there.
- A 20-sample read-only local preview baseline found p95 response times of 25–54
  ms for home and search, 731 ms for tool detail and 2.54 s for statistics.
  These measurements were taken during browser testing, not under a defined
  production workload.

## Before release

1. Identify the deployed host, current and candidate image IDs, origin, TLS and
   proxy trust, allowed hosts, cookie settings, static/media paths and rollback
   configuration. Commit and build the actual release candidate.
2. Exercise real configured ORCID login/connect/disconnect and email
   verification/reset in an authorized environment. None is currently
   available. Verify optional GitHub bridge provenance, credentials and
   capacity if enabled.
   Django 6.1's database checks also report that MySQL cannot enforce allauth's
   conditional uniqueness constraints for primary and verified email addresses.
   Audit existing account data and decide how to enforce those invariants before
   production cutover; this limitation also applied to the previous MySQL setup.
3. Confirm robots, sitemap, canonical URLs and security at the actual origin.
   The image currently denies indexing. Production Compose keeps MySQL and
   Elasticsearch on the internal Docker network, but Elasticsearch security is
   disabled; operators must verify actual network isolation and indexing policy.
4. Agree and measure representative search, editor and management performance
   and error budgets. The accepted workflow measurements above do not cover them.
5. Verify restorable production database and media backups, index recovery,
   compatible migrations, monitoring, smoke checks, rollback triggers and the
   prior deployed artifact. Arrange the outstanding independent sharing/security
   and screen-reader reviews.

After these checks, document a go/no-go decision and obtain separate operator
authorization before deploying. See [installation](../INSTALL.md) for the image
and configuration; do not purge persistent volumes or run destructive fixtures
against production.

## Historical records

The detailed migration reports and completed OpenSpec changes were consolidated
here. Their committed versions remain in Git at `cc96a44`; for example,
`git show cc96a44:docs/frontend-migration/production-readiness.md` retrieves the
full earlier evidence. The retained screenshots are in `docs/evidence/`.
