## 1. Release Candidate Inventory

- [x] 1.1 Confirm schema-driven UI, pinned upstream dev integration (including optional bridge), functional finishing changes and experience acceptance; enumerate registry/bridge/schema/descriptor/vocabulary versions, routes, aliases, external callbacks and retained assets against B01-B13. See the [local cleaned-candidate inventory](../../../docs/frontend-migration/production-readiness.md#cleaned-candidate-inventory-2026-11-01); actual deployment settings remain separate.
- [x] 1.2 Specify and implement stable production helper destinations and compatibility redirects where safe; remove production dependence on preview demos without breaking active clients. See [local helper evidence](../../../docs/frontend-migration/production-readiness.md).
- [ ] 1.3 Record exact deployment configuration, static/media destinations and the enumerated legacy cleanup set for Apache/Caddy and development/production Compose; use the upstream integration's tested image/asset inventory and verify live bridge credentials, provenance and deployment-wide capacity limits when enabled.

## 2. Configured Verification

- [ ] 2.1 Verify authorized live configured ORCID login/connect/disconnect/callback failure and test-email verification/reset flows; leave incomplete if external setup is unavailable.
- [x] 2.2 Run security/API-isolation and browser/crawler/robots/sitemap/canonical checks with production-like origins and configuration. Local HTTPS Apache and Caddy rehearsals passed; actual deployment origin and indexing policy remain to be verified separately.
- [ ] 2.3 Agree measurable performance/error/query budgets, run representative-data scenarios and record dataset, concurrency, environment and results.
- [x] 2.4 Verify concurrent creation of identical domain names against the versioned domain model, and rehearse database-to-index reconciliation after ambiguous transport failures; resolve these management limits before production activation. See [concurrency and recovery evidence](../../../docs/frontend-migration/production-readiness.md#domain-concurrency-and-index-recovery).

## 3. Release Evidence

- [x] 3.1 Document backup/restore evidence, artifact/configuration inventory, observability, smoke checks and rollback triggers. See the [isolated backup and prior-image rehearsal](../../../docs/frontend-migration/production-readiness.md#disposable-backup-and-prior-image-rehearsal-2026-10-31); actual production backups and deployment configuration still require verification.
- [x] 3.2 Rehearse selective route rollback through both proxies and compatible schema/descriptor rollback with retained data; specify a tested prior-release restoration procedure for after deletion. Local prior-image restoration was tested against a restored disposable database; the actual deployed release remains unidentified.
- [ ] 3.3 Publish the release go/no-go record and refresh the audit when all section 1-3 requirements pass. Source removal was explicitly authorized earlier by the user; deployment remains a separate decision.

## 4. Final Legacy-Free Gate

- [x] 4.1 After removal implementation, build/start clean legacy-free artifacts without legacy service/assets/volumes; verify retained static, media, admin and API endpoints through both proxies. Local clean-image and proxy rehearsals passed; actual deployment configuration remains to be verified.
- [x] 4.2 Run full backend/public API, modern type/unit/production build and browser/deep-link/native-fallback acceptance; ensure CI exercises the cleaned build and record failures/skips. See the [cleaned-source verification record](../../../docs/frontend-migration/production-readiness.md#cleaned-source-verification-2026-11-01).
- [ ] 4.3 Recheck configured origins, indexing/security and representative performance on the final artifact; rehearse prior-release restoration in the disposable environment.
- [ ] 4.4 Write final release handover with artifact IDs, commands, evidence, remaining risks and go/no-go; explicitly record that production deployment needs operator approval. A [draft no-go handover](../../../docs/frontend-migration/release-handover.md) records local evidence and outstanding release decisions.
