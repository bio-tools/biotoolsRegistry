## Context

The Vue island runtime and shared query services should be reused if present. If they are not present, add only the minimum compatible pieces needed by this change rather than a parallel build or search implementation. This change establishes the shared search state model that later advanced filtering will extend.

## Goals / Non-Goals

**Goals:**
- One coherent Vue owner for all result-workspace state.
- Canonical shareable URLs for result-defining state.
- Server-authoritative result counts/facets and bounded result transfer.
- Clear extension points for later post-search filtering, comparison and visualization.

**Non-Goals:**
- No full registry SPA.
- No Vue Router.
- No arbitrary user-defined query language.
- Advanced candidate-only post-filtering is a later change.

## Decisions

### Vue owns the complete search subtree

The root contains query controls, filters, result list, sorting/pagination, selection hooks and future analysis panels. htmx cannot target descendants of this root.

### Django owns the route and server contract

The browser loads a Django-rendered page shell and initial search configuration. Vue calls a frontend-oriented search endpoint that maps typed request inputs to shared Python search services. The existing public REST API remains separate and compatible.

### URL is canonical for result-defining state

Represent text query, primary filters, sorting and page/cursor in the URL using stable parsing/serialization. Browser Back/Forward and refresh must reconstruct the same server search. Ephemeral UI state stays out of the URL.

### Search responses are compact and bounded

Return only fields needed to render/operate the results workspace, facet data, result count and explicit pagination/cursor metadata. Full resource documents are loaded separately when needed. Never send the entire registry merely to enable local filtering.

### Remote state is not copied indiscriminately into global state

Use composables and an appropriate query/cache abstraction if already approved. Add Pinia only if real cross-component state warrants it; route state remains explicitly URL-synchronized.

## Risks / Trade-offs

- **Risk: search endpoint duplicates public API semantics** -> Both call shared services; keep response shaping separate.
- **Risk: URL state and component state diverge** -> Centralize parse/normalize/serialize logic and test round trips.
- **Risk: rapid input floods the backend** -> Debounce text changes and abort/ignore stale requests.
- **Risk: large facets/results inflate response and render cost** -> Paginate results and constrain facet payloads.
- **Risk: Vue search becomes a hidden SPA router** -> No Vue Router; Django still owns top-level navigation.

## Migration Plan

Initially expose the new search workspace under migration routing or a reversible route flag. Compare semantics and browser behavior against the legacy search before canonical cutover.
