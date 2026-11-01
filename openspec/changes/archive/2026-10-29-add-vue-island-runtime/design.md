## Context

The modern asset package established for htmx should be extended rather than duplicated. Django owns top-level routes. Vue owns only descendants of explicit mount roots. htmx must not target descendants of a mounted Vue root.

## Goals / Non-Goals

**Goals:**
- Typed Vue 3 components embedded in Django pages.
- Safe initial prop transfer.
- Deterministic mount/unmount across htmx swaps.
- Testable generic lifecycle infrastructure.

**Non-Goals:**
- No Vue Router.
- No site-wide SPA bootstrapping.
- No Pinia unless existing merged code has already justified it.
- No search/editor feature implementation yet.

## Decisions

### Use one component registry and explicit root attributes

Mount only elements declaring a known Vue component/application name. Keep a registry from root element to Vue application instance so duplicate mounting is prevented and unmount is possible.

### Transfer initial props through escaped JSON script data

Prefer Django's safe JSON-script mechanism or an equivalent non-executable JSON container. Do not place arbitrary serialized JSON directly into HTML attributes.

### Bridge htmx lifecycle generically

Listen to documented htmx lifecycle events to unmount Vue applications before their roots are removed and mount newly inserted roots after swaps. The bridge contains no search/editor-specific logic.

### Build through the existing modern Vite package

Add Vue support to the same Vite build that supplies htmx/static assets. Django resolves hashed production assets through the existing manifest mechanism.

## Risks / Trade-offs

- **Risk: duplicate mounts after swaps** -> Root-instance registry plus idempotent mount scan tests.
- **Risk: memory/event listener leaks** -> Explicit unmount on removal and repeated-swap browser tests.
- **Risk: unsafe JSON injection** -> Escaping-safe script serialization.
- **Risk: Vue scope expands accidentally** -> No client-side router; every root is explicitly declared by Django HTML.

## Migration Plan

Ship the runtime with a demonstration component only. Existing pages remain unchanged until they opt into a Vue root. Rollback removes the demo/root includes while leaving the modern asset package intact.
