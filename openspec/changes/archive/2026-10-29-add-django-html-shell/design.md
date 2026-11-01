## Context

The legacy frontend must continue operating while new routes are introduced incrementally. This change establishes only the server-rendered shell; htmx and Vue are separate later changes.

## Goals / Non-Goals

**Goals:**
- Establish a maintainable Django template hierarchy.
- Prove isolated Django page routing alongside the existing frontend and API.
- Establish CSRF and message rendering foundations.

**Non-Goals:**
- No production route cutover.
- No Vue.
- No htmx behavior beyond inert markup compatibility.
- No full visual redesign.

## Decisions

### Use an isolated migration namespace initially

Expose new pages under a clearly isolated development/migration path unless the repository already contains an equivalent route namespace. This prevents accidental shadowing of SPA or API routes.

### Keep server-rendered templates semantically structured

Use a base template with named content blocks and accessible landmarks. Avoid reproducing AngularJS markup mechanically.

### Keep static assets separate from the legacy build

Do not modify Bower/Gulp to serve the new shell. A modern asset path may be introduced by the htmx/Vue changes.

## Risks / Trade-offs

- **Risk: URL precedence shadows API or SPA routes** -> Add route-resolution tests for new and existing paths.
- **Risk: templates depend on SPA globals** -> Keep the shell self-contained.

## Migration Plan

Deploy the isolated route with no public cutover. Rollback is deletion/disablement of the isolated URL include and templates.
