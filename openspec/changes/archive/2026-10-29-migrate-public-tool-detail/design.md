## Context

Shared query services should be reused if already present. If not, extract only the minimum retrieval logic required here and keep public API serialization unchanged. This page should not need Vue and should use htmx only for clearly bounded optional interactions.

## Goals / Non-Goals

**Goals:**
- Direct server rendering of a rich and sparse resource.
- Accessible semantic layout and stable deep-link behavior.
- Preserve links and identifiers relied on by users.

**Non-Goals:**
- Editing.
- Search results.
- Client-side routing.

## Decisions

### Render authoritative page content on the server

The page must be useful on direct request/refresh without first booting a JavaScript application.

### Treat optional data defensively

Templates should use explicit sections/components for nested structures and avoid assumptions that optional lists or fields are present.

### Keep route cutover separate

Implement under the migration routing mechanism first. Production ownership changes only after behavior review and browser tests pass.

## Risks / Trade-offs

- **Risk: legacy page includes undocumented formatting/links** -> Compare against inventory and representative records.
- **Risk: template loops cause N+1 queries** -> Use service-layer prefetch/query shaping and assert query behavior where applicable.
- **Risk: metadata omitted from sparse/rich edge cases** -> Use fixture matrix covering both.

## Migration Plan

Deploy the new page at its migration route. Later `cut-over-migrated-routes` switches the canonical URL after parity review; rollback preserves legacy ownership.
