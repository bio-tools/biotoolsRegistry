## Context

The repository contains a legacy browser application and a Django/DRF backend. The rewrite will be incremental, so undocumented behavior is a larger risk than framework installation. Repository contents may have changed since this plan was authored; the agent must inspect the checked-out tree rather than assume exact filenames.

## Goals / Non-Goals

**Goals:**
- Produce a route-to-code-to-API map comprehensive enough to review later migrations.
- Record architecture rules for Django, htmx and Vue ownership.
- Identify high-risk editor transformations and validation behavior.

**Non-Goals:**
- No runtime code changes.
- No dependency upgrades.
- No route cutover.

## Decisions

### Record observable behavior, not only files

For every route, document URL/query parameters, deep-link behavior, API calls, authentication requirements, mutations, client-side transformations and validation. File inventories alone are insufficient to preserve behavior.

### Use the final ownership model in the ADR

The ADR must establish:
- Django owns top-level routes and server authority.
- htmx owns simple server-rendered fragments outside Vue roots.
- Vue owns complete state-heavy subtrees.
- Search is one Vue-owned workspace.
- The resource editor is one Vue-owned subtree.
- htmx must not mutate mounted Vue-owned DOM.
- Public REST API behavior remains compatible.
- Django views call shared Python services, not the local REST API over HTTP.

## Risks / Trade-offs

- **Risk: behavior exists only in rarely used directives/services** -> Trace imports and route wiring, not only active templates.
- **Risk: inventory becomes stale** -> Include inspected commit SHA/date in each document.
- **Risk: uncertain behavior is guessed** -> Mark uncertainty explicitly and link to code/test evidence.

## Migration Plan

This change is documentation-only and requires no deployment or rollback.
