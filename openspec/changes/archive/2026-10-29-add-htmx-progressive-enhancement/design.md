## Context

The Django shell exists or will be added by this change if the minimum shell hooks are absent. Later Vue components should share the same modern asset pipeline rather than create another build system.

## Goals / Non-Goals

**Goals:**
- Reproducibly bundle htmx 2.x for migrated pages.
- Establish one full-page/partial-template pattern.
- Preserve standard links/forms as fallback when practical.
- Define the DOM ownership boundary with future Vue roots.

**Non-Goals:**
- No search workspace implementation.
- No Vue dependency yet.
- No legacy route cutover.

## Decisions

### Create or reuse one modern Vite-based asset package

If no modern asset package exists, add a dedicated package (for example a new migration frontend asset directory) using Vite. Build output must integrate with Django static files via a manifest or equivalent cache-safe mapping. Do not extend Bower/Gulp for new code.

### Bundle htmx locally

Use a pinned stable htmx 2.x dependency in the reproducible build rather than a runtime CDN dependency.

### Full request and htmx request share domain/view logic

A normal request returns a complete page; an htmx request may return only the target fragment. Avoid duplicating business/query logic between those paths.

### DOM ownership rule

htmx may replace server-owned fragments, but it MUST NOT target descendants of a mounted Vue root. If an htmx swap replaces a container that contains complete Vue roots, later lifecycle infrastructure must unmount/remount them cleanly.

## Risks / Trade-offs

- **Risk: htmx-specific endpoints become inaccessible directly** -> Prefer routes that can render a complete response when useful, or return explicit errors for fragment-only endpoints.
- **Risk: two modern build pipelines appear** -> Vue must extend this same Vite package later.
- **Risk: CSRF mistakes on mutations** -> Test session-authenticated POST behavior before production use.

## Migration Plan

Enable htmx only on Django-rendered migration pages. Removal of the new asset include restores the static shell if rollback is needed.
