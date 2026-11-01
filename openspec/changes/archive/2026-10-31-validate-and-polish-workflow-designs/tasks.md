## 1. Review and fixtures

- [x] 1.1 Define representative real-data and deterministic fixtures with matching oracle, EDAM operation filters, annotation coverage and revisions. See the [full-corpus evidence](../../../docs/frontend-migration/workflow-tool-matching.md#full-public-corpus-results) and documented live-crawl and vocabulary limits.
- [x] 1.2 Define user-journey, visual, accessibility, privacy, performance and recovery acceptance criteria and measurable budgets. See the [acceptance criteria](../../../docs/frontend-migration/workflow-design-acceptance.md#acceptance-criteria) and user-accepted local performance budgets.

## 2. Corrections

- [x] 2.1 Review and fix matching, graph editing, branching, sharing, import/export and stale/missing/unknown states without hiding uncertainty or dropping schema data.
- [x] 2.2 Review and fix desktop/mobile, keyboard, diagram/list, focus, labels, contrast, long values and error recovery; preserve existing image gallery. Screen-reader review remains explicitly recorded as a release limitation because no isolated display was available.

## 3. Acceptance

- [x] 3.1 Run oracle, coverage, security, performance and regression checks with documented fixtures and representative dataset; report skips and limitations. The [acceptance record](../../../docs/frontend-migration/workflow-design-acceptance.md) retains the independent security and deployed-performance limitations.
- [x] 3.2 Run both-proxy desktop/mobile/keyboard, asset/session/index failure, save/reopen/share/revoke and changed-reference journeys; inspect screenshots and fix blockers. Matching uses the database, not Elasticsearch; matching-unavailable recovery was exercised explicitly.
- [x] 3.3 Record findings and evidence, obtain user-facing visual and workflow acceptance, and keep production readiness and deployment as separate gates. The user accepted the designer's appearance and workflow-building experience on 2026-10-31.

Progress and remaining checks are recorded in `docs/frontend-migration/workflow-design-acceptance.md`; the current fixture-heavy preview is not a representative registry corpus.
