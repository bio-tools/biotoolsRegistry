# OpenSpec

Current capabilities are summarized in four specifications: [registry](specs/registry/spec.md),
[resource editor](specs/resource-editor/spec.md), [workflow planning](specs/workflow-planning/spec.md)
and [frontend runtime](specs/frontend-runtime/spec.md).

The only open change is [production readiness](changes/verify-production-migration-readiness/tasks.md).
Local checks do not authorize production deployment. See [operations](../docs/operations.md)
for evidence, outstanding risks and the release decision.

Completed migration changes and the previous detailed specifications remain in
Git at commit `cc96a44`; for example, use
`git show cc96a44:openspec/README.md` to inspect the earlier index.
