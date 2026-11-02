## Why

The migrated frontend and legacy removal passed local verification, but local
fixtures do not establish that the real production deployment is ready.

## What Changes

Verify production configuration, real ORCID and email flows, indexing,
representative performance, backups and rollback. Record a release decision
and operator handover without automatically deploying.

## Capabilities

### New Capabilities

- `migration-production-readiness`: evidence-backed readiness for the cleaned release.

### Modified Capabilities

None.

## Impact

The release checklist and deployment documentation. Required unavailable checks
remain open; production deployment requires separate operator authorization.
