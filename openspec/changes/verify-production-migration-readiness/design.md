## Approach

Verify the cleaned artifact using the actual intended origin and configuration.
Separate deterministic local checks from authorized live ORCID and email tests.
Agree performance budgets before measuring representative workloads. Record
schema/vocabulary versions, retained assets, security, indexing, backups,
observability, smoke checks and rollback procedures.

Do not purge persistent data or treat a local rehearsal as proof of production
backup restoration. If a provider, environment or decision is unavailable, leave
its task open and record the limitation. A release decision and deployment are
separate from this change's implementation.
