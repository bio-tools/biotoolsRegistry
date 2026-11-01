## 0. Develop baseline

- [x] 0.1 Confirm `refresh-develop-migration-baseline` is complete before implementation.
- [x] 0.2 Review this change against the [develop impact matrix](../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations. See the [2026-10-14 audit](../../../docs/frontend-migration/legacy-removal-audit.md).

## 1. Prove the legacy frontend is unused

- [x] 1.1 Verify the release candidate routes user-facing pages to Django. The actual deployed server remains subject to the separate production-readiness checks.
- [x] 1.2 Search Django/backend code, templates/static includes, reverse-proxy/Caddy config, Compose files, production Compose, CI workflows and documentation for legacy frontend paths/services/assets.
- [x] 1.3 Create `docs/frontend-migration/legacy-removal-audit.md` listing every dependency found and its disposition.
- [x] 1.4 Document the original dependency blocker. Deletion stopped on 2026-10-14; the user's 2026-11-01 instruction superseded that sequencing after local replacements were established.
- [x] 1.5 Complete the functional and experience changes. On 2026-11-01 the user explicitly authorized source removal before the outstanding production-readiness checks; those checks remain open in `verify-production-migration-readiness`.
- [x] 1.6 Refresh the audit against the release candidate and retain schema, image, JSON and static resources in `registry-assets/` with their public URLs.

## 2. Remove legacy source and build dependencies

- [x] 2.1 Remove AngularJS application source; relocate retained content, favicon, static assets and schema/reference resources.
- [x] 2.2 Remove Bower configuration/components and legacy Gulp configuration/dependencies.
- [x] 2.3 Remove obsolete package scripts and build steps for the legacy application.

## 3. Simplify deployment/runtime configuration

- [x] 3.1 Remove the legacy frontend and Rendertron services from local, production and rehearsal Compose without purging persistent volumes.
- [x] 3.2 Remove the SPA/Rendertron fallback and route switches; preserve Django, static, API, admin, media and permanent browser/EDAM helpers.
- [x] 3.3 Update CI, contributor hooks and legacy-specific tests while preserving API and modern regression coverage.

## 4. Update documentation and verify

- [x] 4.1 Update active installation/contribution/deployment documentation for the Django + htmx + Vue/Vite architecture; retain dated historical migration evidence.
- [x] 4.2 Build and start the production-like stack without any legacy frontend service; Apache and Caddy smoke checks passed.
- [x] 4.3 Run backend tests, modern frontend type-check/unit/build, full browser regression suite and route/deep-link checks. The complete backend run and all browser scenarios passed across the main run, corrected-test reruns and required configuration variants; see the [verification record](../../../docs/frontend-migration/production-readiness.md#cleaned-source-verification-2026-11-01).
- [x] 4.4 Confirm no AngularJS/Bower/Gulp runtime dependency remains and summarize deleted dependencies/configuration in the completion report.
