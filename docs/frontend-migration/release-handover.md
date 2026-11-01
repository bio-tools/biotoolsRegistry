# Draft production handover

Status: **no-go for production**. This is a local rehearsal record, not approval
or evidence that the live deployment has changed. The user confirmed that no
configured ORCID/email test environment is currently available. Complete the
remaining `verify-production-migration-readiness` tasks before release.

## Candidate and local evidence

The candidate is the uncommitted `trial_rewrite_codex` working tree. Its code was
built from develop baseline `9faec5b3b660498fdef9736e65e331728b55f99c`; the
branch itself retains its earlier commit. The locally built image is
`sha256:ef56bed6bbc432d50426422f3d1f65b4579860f67e24f3865819e481151f4d87`.
A commit and reproducible release artifact still need to be identified before
an operator can deploy. Schema, descriptor, vocabulary, bridge, routes and
asset identities are in the [candidate inventory](production-readiness.md#cleaned-candidate-inventory-2026-11-01).

The isolated backend, frontend, browser and schema-transition checks are in the
[verification record](production-readiness.md#cleaned-source-verification-2026-11-01).
These do not establish live ORCID, SMTP, production network policy or production
load capacity. The optional GitHub bridge requires its own live provenance,
credentials and capacity checks if enabled.

## Before a release decision

- Identify the deployed host, current and candidate image IDs, canonical origin,
  TLS/proxy trust, allowed hosts, secure cookies and callback URLs. Configure and
  exercise authorized ORCID and email verification/reset flows.
- Confirm the intended robots/indexing policy and sitemap at the real origin.
  The candidate image currently serves deny-all robots, and the sample production
  Compose exposes database and Elasticsearch ports with Elasticsearch security
  disabled; operators must verify network isolation and adapt configuration.
- Set and verify agreed search, editing and management performance/error budgets
  with representative production-like data and concurrency. The separately
  accepted local workflow-search measurements are not a production SLA.
- Take and verify restorable backups of the actual database and media; identify
  index backup or rebuild procedures, migration compatibility, monitoring,
  smoke checks, rollback thresholds and the exact prior deployed artifact and
  configuration. A disposable local backup/restore rehearsal is recorded in
  [production readiness](production-readiness.md#disposable-backup-and-prior-image-rehearsal-2026-10-31);
  it does not validate actual production backups or the prior deployed image.
- Obtain an independent sharing/security review and an available screen-reader
  review, as recorded in [workflow acceptance](workflow-design-acceptance.md).

## Operator steps after approval

Build the identified source with `docker build --target prod -t IMAGE .` and
validate the deployment Compose using the operator's secret mechanism and the
existing credentials. The required variables and development setup are listed
in [INSTALL.md](../../INSTALL.md). Confirm backup restoration and compatible
migrations before activation. After activation, smoke-test home, search, detail,
login, editor, workflows, public API, admin, static files and media from the
actual public origin; monitor route errors, authentication, writes and index
health. If rollback triggers occur, pause writes and restore the verified prior
artifact and compatible configuration according to the operator's tested plan.
Production deployment requires separate explicit operator authorization.
