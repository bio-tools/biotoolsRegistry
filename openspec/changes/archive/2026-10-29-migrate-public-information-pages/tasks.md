## 1. Inventory

- [x] 1.1 Review B03/B07/B10 and inventory all public routes, redirects, source content, domain links, statistics datasets and referenced assets.
- [x] 1.2 Confirm redirect destinations and metadata/indexing intent; specify handling for unavailable external targets and tool-ID route collisions.

## 2. Implementation

- [x] 2.1 Implement native home/about/community/domain directory and statistics pages using existing data services and shell.
- [x] 2.2 Replace SPA/meta-refresh redirects and error pages with explicit server responses, preserving aliases and deep links.
- [x] 2.3 Move required content assets into retained static serving and update navigation/link producers and both proxy ownership rules.

## 3. Verification

- [x] 3.1 Add backend tests for route precedence, status/redirects, data rendering, statistics empty/failure states and preserved API boundaries.
- [x] 3.2 Run desktop/mobile and no-JavaScript public journeys plus crawler/asset checks through both proxies.
- [x] 3.3 Update route ownership, asset dispositions and the audit with revision-specific evidence and external-link limitations.

Local acceptance completed 2026-10-24. See
[route/content inventory, asset dispositions and verification](../../../../docs/frontend-migration/public-information-pages.md).
Production activation, external destination replacement and legacy deletion remain
separate readiness/retirement work.
