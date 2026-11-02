## 1. Candidate inventory

- [x] 1.1 Inventory the local schema, descriptor, vocabulary, bridge, routes and retained assets; actual deployment configuration remains separate. See [operations](../../../docs/operations.md).
- [x] 1.2 Preserve stable browser and EDAM helpers and remove production dependence on demos.
- [ ] 1.3 Verify actual deployment configuration, static/media destinations and optional bridge provenance, credentials and capacity.

## 2. Configured verification

- [ ] 2.1 Exercise authorized live ORCID login/connect/disconnect and email verification/reset; no configured test environment is currently available.
- [x] 2.2 Check local production-like security, API isolation, crawler, robots, sitemap and canonical routing. Confirm the actual origin and indexing policy separately.
- [ ] 2.3 Agree and measure representative search, editor and management performance/error budgets. Local workflow-search limits were accepted and passed.
- [x] 2.4 Verify domain-name concurrency and database-to-index recovery after ambiguous failures.

## 3. Release evidence

- [x] 3.1 Document local backup/restore evidence, artifact inventory, observability, smoke checks and rollback triggers. Verify actual production backups separately.
- [x] 3.2 Rehearse local route rollback and prior-image restoration using disposable data. Identify and test the real prior deployed artifact separately.
- [ ] 3.3 Record a release go/no-go after the outstanding configuration, provider and performance checks pass.

## 4. Final artifact

- [x] 4.1 Build and start the clean native image; verify retained static, media, admin and API routes through both local proxies.
- [x] 4.2 Run backend, frontend, browser and schema-update checks against the cleaned artifact; document reruns and skips in [operations](../../../docs/operations.md).
- [ ] 4.3 Verify actual origins, indexing/security and representative performance; rehearse restoration of the identified prior release.
- [ ] 4.4 Complete the final handover with artifact IDs, evidence, risks and go/no-go. Production deployment needs separate operator authorization.
