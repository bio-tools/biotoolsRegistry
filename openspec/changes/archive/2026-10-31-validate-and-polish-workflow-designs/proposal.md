## Baseline

Assess the implemented matching, designer and draft/sharing changes on `develop-migration/` against representative bio.tools data and the current blue registry experience.

## Why

Workflow composition is only useful if matching explanations are trustworthy, annotation gaps are visible, and people can successfully create and revisit meaningful designs.

## What Changes

- Evaluate matching and EDAM operation filtering against independently checked representative examples and real annotation coverage.
- Review linear and branching workflows, long/sparse metadata, changed tools and uncertain connections on desktop, mobile and keyboard.
- Correct usability, accessibility, performance and recovery blockers and record the evidence and remaining limitations.
- Obtain user-facing visual and workflow acceptance; keep existing image gallery access until an explicit separate retirement decision.

## Dependencies

Requires `add-workflow-tool-matching`, `add-workflow-designer`, `add-workflow-drafts-and-sharing`, and the existing migration experience acceptance. Coordinate production readiness if these changes are included in a release; their proposal does not authorize deployment.

## Capabilities

### New Capabilities

- `workflow-design-acceptance`: Evidence-backed functional, usability, accessibility and data-quality acceptance of workflow design.

### Modified Capabilities

None.

## Impact

Fixtures, focused tests, UI/service corrections and acceptance evidence. No workflow execution, executable export or automatic publication.
