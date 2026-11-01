## Context

This is the final destructive cleanup change, followed by final production-readiness verification of the cleaned artifact. It is unsafe to treat lack of obvious navigation links as proof that legacy assets are unused; proxy fallbacks, backend mounts, CI jobs or obscure routes may still depend on them.

The 2026-10-14 [audit](../../../docs/frontend-migration/legacy-removal-audit.md) found active dependencies B01-B12. On 2026-11-01 the user explicitly authorized removal before the remaining production-readiness tests, which will be completed separately against the new implementation. The actual deployment and its provider checks remain outside this cleanup.

## Goals / Non-Goals

**Goals:**
- Remove only demonstrably unused legacy runtime/build infrastructure.
- Simplify local and production startup to the new architecture.
- Keep complete regression coverage passing.

**Non-Goals:**
- New UI features.
- Public API changes.
- Opportunistic unrelated dependency cleanup.

## Decisions

### Dependency report precedes deletion

Create a report covering route ownership, proxy/static references, Compose services/volumes/mounts, CI, docs and backend references. If a live dependency remains, stop cleanup and record it.

### Delete legacy stack as one reviewable cleanup after cutover

Once no dependency remains, remove AngularJS/Bower/Gulp assets and the dedicated legacy frontend runtime/deployment pieces. Do not leave a half-supported build path.

At the cleanup gate every user-facing dependency must have a tested replacement;
only explicitly enumerated legacy build/proxy/service references may remain for
removal in this change. Relocate retained assets before deleting their old paths.
The frontend directory also contains collected Django/admin/DRF assets, logos,
favicon and schema/reference resources: it is not a disposable Angular-only tree.
Remove Rendertron and the retained-page session bridge only after their consumers
are gone. Preserve permanent session/EDAM helpers and public token API behavior.

Adapt legacy-specific test assertions to replacement contracts; do not drop API,
authorization or failure-recovery coverage. Compose cleanup changes configuration,
not database/index/media contents, and must not purge existing volumes.

## Risks / Trade-offs

- **Risk: hidden legacy route breaks** -> Compare route inventory/ownership and run full browser suite before deletion.
- **Risk: production static/proxy reference missed** -> Search all Compose/proxy/CI/docs and run production-like startup.
- **Risk: rollback becomes harder after deletion** -> Rely on version control/tagged release; do not archive this change until new stack is stable.

## Migration Plan

Create dependency report -> complete functional/experience changes -> relocate retained assets -> remove the legacy stack -> rebuild/start the new environment -> complete remaining regression and production-readiness tests separately. Archive only after stable verification. Rollback after deletion restores a tested prior release and compatible configuration; old runtime flags alone are insufficient. Actual production deployment requires explicit operator approval.
