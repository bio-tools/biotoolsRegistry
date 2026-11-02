# Production readiness

**Status: not ready for production deployment.** The legacy frontend has been
removed and the local checks below passed, but the live deployment has not been
migrated or verified. The remaining tasks are in the [readiness checklist](../openspec/changes/verify-production-migration-readiness/tasks.md).

## Local evidence

- The cleaned backend suite ran 351 tests; ten opt-in Elasticsearch checks passed
  separately. Frontend type checking and 118 unit tests passed. Browser scenarios
  passed across the main run, corrected-test reruns and separate configuration
  runs. The initial main run had two editor test timing failures; both passed
  after the tests were corrected.
- An isolated same-build rehearsal added, removed and restored schema fields and
  vocabulary terms through Apache and Caddy. The same frontend bundle was used
  throughout, and edited values persisted.
- With 34,519 anonymized public records and EDAM 1.25, the cleaned image matched
  the workflow-search oracle. The broad scan had 290 ms p95 page time, 386 ms
  maximum, and four concurrent first-page requests completed within 622 ms.
  These are local in-process results, not production capacity or an SLA.
- A disposable MySQL/media backup and prior-image restore rehearsal passed. It
  did not verify the actual production backup or identify the deployed image.

## Before release

1. Identify the deployed host, current and candidate image IDs, origin, TLS and
   proxy trust, allowed hosts, cookie settings, static/media paths and rollback
   configuration. Commit and build the actual release candidate.
2. Exercise real configured ORCID login/connect/disconnect and email
   verification/reset in an authorized environment. None is currently
   available. Verify optional GitHub bridge provenance, credentials and
   capacity if enabled.
3. Confirm robots, sitemap, canonical URLs and security at the actual origin.
   The image currently denies indexing; production Compose also publishes MySQL
   and Elasticsearch ports with Elasticsearch security disabled, so operators
   must verify network isolation and the intended policy.
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
