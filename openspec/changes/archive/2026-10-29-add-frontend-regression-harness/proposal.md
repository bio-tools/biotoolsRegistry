## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
The original completion record applies to the old tree; revalidate this foundation as part of `refresh-develop-migration-baseline`.

## Why

The migration needs tests that describe user-visible behavior independently of AngularJS so the same workflows can validate Django/htmx/Vue replacements. Without a behavioral baseline, route-by-route replacement risks silent regressions in search state, deep links, authentication and editing.

## What Changes

- Introduce or extend Playwright-based browser smoke tests with a configurable base URL.
- Cover public search, filtering, navigation, tool details, browser history and representative authentication behavior.
- Add stable selectors only where accessible roles/labels are insufficient.
- Capture trace/screenshot artifacts on failure.
- Do not change production behavior solely to make tests easier.

## Capabilities

### New Capabilities

- `frontend-regression-harness`: Maintainers can execute framework-independent browser regression scenarios against configurable deployments and obtain actionable failure diagnostics.

### Modified Capabilities

None.

## Impact

Developer dependencies, CI and test fixtures may change. Runtime application behavior must not.
