# ADR 001: Frontend ownership during incremental migration

Develop review (2026-09-12): see [routes and deployment](develop-refresh.md#routes-and-deployment)
for the pinned upstream changes and acceptance limits. That review supersedes
conflicting old-baseline observations below; historical evidence is retained.

Baseline note: this document describes the old `a1fc8b9` worktree.
The [selected upstream develop baseline](baseline.md) has separate completed revalidation;
the source observations and test results below are not develop acceptance evidence.

Inspected commit: `a1fc8b94067f33bc9047efc9c75ebe1579365a07`.
Inspection date: 2026-09-09.
Status: migration decision recorded by `inventory-frontend-migration`; implementation and production cutover remain pending.

## Context

The [route inventory](routes.md) identifies a single AngularJS application served by Apache, a Django/DRF API and shared client state spanning navbar, search results and editor tabs. Search is coupled through URL/query/list/sort/page services. The editor sends a complete resource replacement and can change data in hidden tabs. Replacing individual DOM controls without assigning ownership would split these state models and increase data-loss and history risks.

## Decision

1. **Django owns top-level browser routes and server authority.** It renders full pages, enforces authentication/permissions, validates all mutations, and defines error/redirect behavior. Browser visibility and client validation cannot grant permission or override server validation.
2. **htmx enhances simple server-rendered fragments outside Vue roots.** Ordinary GET links and form submissions remain functional fallbacks. A fragment has an explicit server endpoint and replacement target; history/redirect/error behavior must also make sense for full-page requests.
3. **Vue owns complete state-heavy subtrees.** Django emits initial props through safe JSON serialization. Each mounted root owns its descendants and client state. htmx must not mutate DOM inside a mounted Vue subtree; replacing a containing region requires unmounting that Vue application before removal and mounting any replacement root once. Neither AngularJS nor third-party widgets may co-own the migrated root.
4. **Search is one Vue-owned workspace.** Query, filters, suggestions, sorting, pagination, result layout, selection and future comparison/analysis features share one state model. Django owns the search page and authoritative query execution. Result-determining state is represented in the URL or an explicit saved-search reference; browser Back/Forward and reload restore it. A navbar/home search entry may navigate to the workspace but must not maintain a competing result set.
5. **The resource editor is one Vue-owned subtree.** Basic fields, nested functions, EDAM selection, permissions, JSON/state conversion and error mapping remain coherent inside it. Shared typed EDAM controls can be reused within search/editor. Django owns the page, permission checks, CSRF and persistence. A staged basic editor must preserve untouched nested fields through the tested data contract.
6. **The public REST API stays compatible.** Preserve supported paths/aliases, methods, authentication for external clients, payload/response fields, pagination/error semantics and content negotiation, including JSON/XML/YAML and detail JSON-LD. Browser-oriented endpoints may be added separately; they cannot silently repurpose the public API for a Vue-specific shape.
7. **Server views call shared Python services directly.** Reuse/extract retrieval and query logic currently in `elixir/view/resource.py`, `elixir/search.py` and related modules. Django-rendered views must not call the application's own REST API over HTTP. Shared services retain authoritative access and query semantics while serializers/presenters handle their own output formats.
8. **Migration and cutover are separate decisions.** Keep legacy routes/build working while replacements run under isolated migration routes or a reversible ownership mechanism. Switch each canonical route only after implementation, behavioral tests and parity review, recording the routing rule and rollback. Audit all route, proxy, static, build, CI and deployment dependencies before removing AngularJS/Bower/Gulp.

The existing browser uses localStorage tokens; session/CSRF behavior for migrated pages must be established by `migrate-browser-authentication`. Installed middleware and JWT packages are not evidence of a usable browser session strategy. Preserve external token clients while introducing the chosen browser flow.

## Interaction classification

All target classifications imply Django route/server ownership. They are not authorization to cut over an incomplete feature.

| Interaction | Target | Rationale / gate |
| --- | --- | --- |
| Page shell, navigation, footer, about/community content, 404 | Plain Django | Primarily links/content; native anchor and redirect behavior; no shared mutable client model needed. |
| External aliases and schema redirect | Plain Django | Server redirects with explicitly reviewed destination and URL precedence. |
| Home/navbar search entry | Vue control or ordinary GET form feeding search | Preserve typed tag entry where retained; submit canonical state to the same search workspace. No independent results model. |
| Search query, suggestions, filters, sorting, pagination, cards/grid | Vue workspace | These controls change the same result identity and URL state. No htmx result swaps within it. |
| Domain banner inside search | Vue-rendered data within workspace | Domain scope affects search; Django/service supplies authoritative metadata and membership. |
| Tool detail and metadata | Plain Django | Read-oriented content, stable links, server-emitted metadata/JSON-LD; native disclosure where adequate. |
| Request editing/ownership from detail | htmx form/fragment | Small server-authorized command and success/error state outside Vue. Full-form fallback required. |
| Login, registration, recovery, profile | Plain Django; htmx for small form/list updates | Server-owned auth flow and validation; retain deep links, destination return and error states. Modal presentation is optional, not an authentication boundary. |
| Requests list/filter/accept/decline, profile disown | htmx | Server-filtered fragments and discrete commands; preserve transfer effects, confirmations and counts. |
| Resource form, raw JSON, nested structures, EDAM, permissions | One Vue editor | Full payload and validation state cannot be split between fragment replacement and client state. |
| Domain directory local search | Vue subtree | Current weighted multi-field filtering and domain/resource counts share a local state model; bound data before scaling. |
| Stats charts | Vue chart subtree within Django page | Chart interactions/data transforms share state; server remains source of totals. |
| Domain administration/editing | Legacy until later | Current plans do not fully specify its private flag, memberships, bulk selection, aliases or replacement updates. Requires explicit migration coverage; cannot be dropped for legacy retirement. |
| Workflow image/annotation browser | Legacy until later | Routed but not in main navigation; legacy modal and regex behavior unverified. Decide supported behavior and tests before migrating or retiring. |
| Old affiliation/version templates and unresolved calls | Legacy/unresolved evidence | No active route chain demonstrated; audit usage and explicitly retire or support before deleting dependencies. |

## Consequences and acceptance gates

This keeps public rendering straightforward while allowing coherent client state for search and editing. It requires explicit Vue mount/unmount handling, shared backend query contracts, browser tests and a loss-resistant editor mapping. It does not require a site-wide SPA, parallel routers for migrated pages, or duplicate search engines.

For each route family, record: current and proposed owner, canonical paths/aliases, backend/public API impact, tested authentication/error/history behavior, routing mechanism and rollback. Existing legacy routes remain owned by AngularJS until these gates pass. Home/about/community/stats/domain-directory/profile/requests/workflows/domain-management and redirects need implementation coverage in addition to the named search/detail/editor changes. The 16 proposal names alone do not establish complete route parity.

This ADR and its companion inventory are documentation only. No runtime configuration, assets, dependencies or route ownership were changed. See [risk register](risk-register.md) for evidence needed before implementation/cutover.
