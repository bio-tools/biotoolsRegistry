## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
Implementation requires completion of `refresh-develop-migration-baseline`.

## Why

EDAM term selection is a repeated state-heavy interaction across bio.tools search and resource editing. A single typed accessible Vue component avoids duplicating autocomplete, keyboard, stale-request and serialization behavior in multiple features.

## What Changes

- Add a reusable Vue selector configurable for EDAM concept class/branch and single or multiple selection.
- Add or reuse a narrow backend term-search service/endpoint with debouncing and stale-request handling.
- Submit stable EDAM identifiers rather than trusting client-provided labels.
- Support keyboard-only interaction, loading/empty/error states and re-render after server validation errors.

## Capabilities

### New Capabilities

- `edam-selector`: Migrated interfaces can search, select and submit valid EDAM concepts through a reusable accessible component.

### Modified Capabilities

None.

## Impact

Adds a reusable Vue component and possibly a frontend-oriented EDAM lookup endpoint while preserving existing public ontology/API behavior.
