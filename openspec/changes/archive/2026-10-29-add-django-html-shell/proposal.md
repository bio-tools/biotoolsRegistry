## Baseline

Target: upstream develop pinned in the [migration baseline](../../../../docs/frontend-migration/baseline.md).
The original completion record applies to the old tree; revalidate this foundation as part of `refresh-develop-migration-baseline`.

## Why

The migration needs a server-rendered page foundation that can coexist with the legacy SPA. Establishing the shell first allows later pages to move individually without coupling route cutover to Vue or search/editor rewrites.

## What Changes

- Add a Django-rendered base layout with navigation/footer placeholders, messages, CSRF support and static assets.
- Expose at least one isolated migration/test route owned by Django.
- Establish complete-page and error-page rendering conventions.
- Keep legacy frontend routes and public REST API routes unchanged.

## Capabilities

### New Capabilities

- `server-rendered-frontend`: Django can serve complete browser pages independently of the legacy AngularJS application.

### Modified Capabilities

None.

## Impact

Django URLs/templates/static assets and local deployment configuration may gain new entries. Existing production route ownership must remain unchanged in this change.
