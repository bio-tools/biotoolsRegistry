## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

## 1. Inspect legacy behavior and data access

- [x] 1.0 Include develop JSON/XML alternates, publication/modification dates and a documented decision for BIP/Dimensions widgets in detail parity evidence.

- [x] 1.1 Trace the current tool-detail route, displayed sections, links, conditional sections and any client-side data transformation.
- [x] 1.2 Identify or add representative sparse and structurally rich resource fixtures.
- [x] 1.3 Reuse the shared tool-retrieval service if present; otherwise add only the minimum compatible service extraction needed for this page.

## 2. Implement the Django page

- [x] 2.1 Add the Django view and migration-route URL for tool details.
- [x] 2.2 Add semantic templates/components for identity/description, EDAM data, functions, inputs/outputs, publications, links/downloads, credits and relationships as present in the current model.
- [x] 2.3 Add useful page title/metadata and accessible heading/link structure.
- [x] 2.4 Implement not-found, hidden/non-public and malformed identifier behavior consistent with backend policy.

## 3. Test behavior

- [x] 3.1 Add Django tests for rich, sparse, not-found and restricted records.
- [x] 3.2 Add browser tests for direct deep link, refresh and representative outbound/internal links.
- [x] 3.3 Check backend query/Elasticsearch request count for representative rendering and remove avoidable N+1/duplicate access.

## 4. Review parity

- [x] 4.1 Compare legacy and migrated pages against the migration inventory and record deliberate presentation differences.
- [x] 4.2 Verify no production route has been cut over and no public API behavior changed.

## Completion evidence

Completed 2026-09-14 in `develop-migration/`, based on upstream develop
`9faec5b3b660498fdef9736e65e331728b55f99c`.

- Isolated route: `/_migration/html/tool/<identifier>/`; canonical routes and API
  ownership are unchanged. Detail is read-only and needs no JavaScript.
- Reuses shared lookup/visibility through `get_tool_detail`; templates render ORM
  metadata with batch-prefetched relations, not internal HTTP or DRF serialization.
- Rich and sparse fixtures cover identity, nested EDAM, publications, credits,
  documentation/downloads, links, relationships, technical and registry metadata.
- Missing, hidden and malformed identifiers are 404; untrusted text/URLs and
  incomplete nested records are covered. Mutations are rejected.
- JSON/XML/JSON-LD alternates, added/updated dates, canonical metadata and the
  explicit BIP/Dimensions/other remote-widget decision are recorded in the parity note.
- 47 Django tests pass on both Python 3.13 and 3.10.12, Django 5.2.11.
- 19 browser tests pass through both Apache and Caddy with no skips/retries:
  rendered legacy parity, deep links, refresh/history, native keyboard controls,
  JavaScript disabled, links, assets and browser/bot/API routing.
- 1440px desktop and 390px mobile screenshots inspected; blue branding, loaded
  logo and no horizontal overflow. No third-party requests from the migrated page.
- At most 35 SQL queries for rich rendering, one resource lookup and no Elasticsearch
  requests; multiplying nested functions/publications/credits does not grow the count.
- All 17 OpenSpec changes pass strict validation; whitespace checks pass.

[Prototype URLs, parity decisions, commands and rollback](../../../../docs/frontend-migration/public-tool-detail.md).
The seeded rich record is explicitly fictional; original worktree and existing
preview records are preserved.
