## Baseline

Implement on `develop-migration/` using the accepted blue shell, current schema-driven resource views and `add-workflow-tool-matching` contract. The existing annotated-image workflow gallery is not an editable workflow graph.

## Why

People need to choose relevant tools and tailor a sequence of analysis steps, instead of viewing only a pre-existing static diagram.

## What Changes

- Provide a workflow design workspace for choosing input/output data and format, optionally filtering candidate functions by EDAM operation, and adding selected functions as steps.
- Allow users to connect specific outputs to inputs, create branches, rearrange and remove steps, annotate choices and see matching evidence and unknowns.
- Provide equivalent keyboard-operable list and diagram views, recoverable draft/error states, and navigation to underlying bio.tools records.
- Keep the existing workflow gallery reachable; do not silently convert its image annotations or remove its API.

## Dependencies

Requires `add-workflow-tool-matching`, the EDAM selector, schema-driven UI and accepted migration shell. `add-workflow-drafts-and-sharing` adds persistence and sharing after the in-memory designer is usable.

## Capabilities

### New Capabilities

- `workflow-designer`: User-authored, non-executable workflow designs assembled from annotated tool functions.

### Modified Capabilities

None.

## Impact

New designer route and Vue interaction using existing native shell and shared matching endpoint. Existing gallery and public resource APIs remain supported. No executable workflow generation or execution.
