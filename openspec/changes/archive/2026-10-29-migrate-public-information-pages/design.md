## Scope

Own /, /about, /community, /communities, /domains, /stats and /404.
Preserve /schema as a server redirect to its approved schema destination.
Migrate fixed redirects /governance, /events, /mail, /faq, /apidoc, /changelog,
/helpdesk, /projects and /roadmap. Check their actual destinations during
implementation; a historical external URL is not evidence of current availability.

## Decisions

- Use server-rendered pages and existing read services, with small htmx/Vue
  enhancements only where data interaction requires them.
- Preserve useful home search and domain-directory search/filter behavior.
  Home remains an entry to the registry, not a new marketing landing page.
- Port statistics from the existing total entries, users, annotation count and
  aggregate data sources. Keep comparable visual summaries plus accessible values;
  unavailable data is not zero. Do not add a new analytics backend.
- Move required logos/content images into the retained static pipeline, maintaining
  attribution and intentional compatible URLs. Schema/reference files and API
  assets need classification, not wholesale deletion.
- Reserve literal public and redirect routes ahead of tool identifiers; preserve
  both community aliases. Unknown routes and missing resources receive genuine
  error responses without an Angular bootstrap.
- Define page-specific canonical/indexing metadata. Preview remains noindex;
  production indexing decisions are verified by the readiness change.

## Verification and Rollback

Check native GET, refreshed deep links, mobile/desktop navigation, asset failures,
domain links and statistics success/empty/failure states. Verify status, Location,
metadata and rendered content for ordinary browsers and crawler user agents on
Apache and Caddy. Keep reversible ownership until retirement and record any
destination changes; do not silently retire public links.

## Non-Goals

No editorial rewrite, new content management system, new statistics metrics or
domain administration. Domain writes and workflow browsing belong to management.
