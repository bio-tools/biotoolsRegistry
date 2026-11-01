# Upstream dev integration

Local acceptance record: 2026-10-27. This document does not authorize production
activation or legacy deletion.
The packaging and deployment instructions below describe that dated baseline;
the current production-image change and outstanding gates are recorded in
[production readiness](production-readiness.md).

## Reviewed baseline and implementation

Upstream `dev` was reconfirmed at `400bbe32bbdc5396356b35a8f8b4040a731978e5`.
The implementation remains in the dirty migration checkout based on
`9faec5b3b660498fdef9736e65e331728b55f99c`; there was no merge/reset. The
[54-path review](upstream-dev-review.md) remains the source disposition inventory.

| Area | Integration disposition |
| --- | --- |
| GitHub metadata import | Native Django adapter and Vue editor review; descriptor-derived writable fields; keep/replace/selective merge, keep-all, discard, raw output and explicit draft confirmation. |
| Licence vocabulary | Upstream's 725 XSD values replace the 435-value effective catalogue, retaining historical and four non-SPDX values. The XSD remains the runtime source; no duplicate frontend or Python enum catalogue was introduced. |
| ELIXIR communities | Six upstream additions plus the two existing policy extensions now reside in the selected XSD, so XML and JSON share all 19 community values. |
| Mobile OS, cost, accessibility | Existing descriptor coverage retained; no second option implementation. |
| Unchanged saves | Shared `ResourceDetail.put` fingerprint after validation and authorization; native feedback and retained Angular feedback. Ordered annotations and duplicates remain significant. |
| Dashboard | Existing nested filters gain local used-value searching and repeat-selection clearing, preserving query/domain scope and URL state. Saved display preferences remain assigned to final polish. |
| Record user picker | Existing native datalist, Enter-to-add, cancellation/stale-response guard, duplicate exclusion and error states retained; permission tests pass. Domain picker acceptance belongs to management. |
| Publications | Corrected enrichment signature, bounded calls, readable citations and the 2026 reference retained. |
| Environment | Explicit boolean parsing fixes false-string truthiness. Deployment/blacklist overrides and admin email remain compatible because active consumers still exist. |
| Packaging | Root Dockerfile builds modern and retained assets into the Apache image. Production backend/taskrunner share that image without checkout mounts; database/index/data volumes are retained and media has a persistent volume. |
| CI | API startup excludes the legacy frontend; modern type/unit/build and descriptor checks remain. Deterministic bridge browser checks use a separate disposable provider, never live credentials. |

## Verified bridge contract and provenance

The upstream image name is `anitamnd/bridge`. Its Docker Hub manifest was pinned
to `sha256:d9dc5a5484247b9eedc9e204aea999bcd82fce79e5fea8bdfe4681b50203ec61`;
the amd64 manifest is
`sha256:8d7f5e254ed408bd8c84f03520757324c82faebde7c06a7db2ff413d60446326`.
The image's source layer
`sha256:045f7b1580b4272b84012f796772d5b0641db9a850cc60978aa0ef739520629f`
was downloaded, digest-checked and inspected without executing the service.
This pins the inspected artifact; it is not a claim of signed publisher provenance.

The inspected FastAPI router takes `{owner, repo, biotools_id?}` and returns
HTTP 201 with JSON-encoded metadata. Its handler can retrieve an existing public
bio.tools record and clones the repository before running extraction. Notably,
the service expects `biotools_id`, unlike upstream Angular's `biotoolsID`.
The adapter translates the permitted existing identifier to the verified name.
Provider configuration uses `GITHUB_TOKEN` and `HUGGINGFACE_TOKEN`; no user
tokens or draft content are sent by the adapter.

The browser supplies an exact `https://github.com/owner/repository` URL, an
optional authorized existing ID, and its schema revision. A trailing slash or
`.git` suffix is supported; credentials, ports, query strings, fragments, encoded
segments and repository subpaths are rejected. The internal URL comes only from
server configuration, redirects are disabled, and provider failures are sanitized.

Requests are limited to 2 KiB and responses to 512 KiB. Connect/read timeouts are
5/45 seconds with elapsed-time checks between response chunks. Each worker has
two provider slots and a one-minute per-user attempt limit through Django's
cache. With the default local-memory cache these limits are per worker, not a
deployment-wide quota; size worker counts and provider quotas during readiness.
The optional service also has CPU, memory and PID limits and no published port.

Suggestions are checked recursively against the descriptor and serializers.
Unknown/protected values, nested enrichment, registry identifiers and incompatible
values are visibly rejected. Current values default to keep. List merge compares
complete structured values and preserves existing duplicates and repeated-item
identities. Changed selected draft values require a fresh comparison. Apply has
no persistence endpoint; the ordinary save retains CSRF, permissions, revision,
schema and preservation checks.

## Configuration and rollout

`BIOTOOLS_GITHUB_BRIDGE_URL` defaults to empty. In that state the adapter returns
503 and manual editing remains available. To configure the optional service,
combine the deployment Compose file with `compose.bridge.yml`, explicitly enable
the `github-import` profile, provide provider tokens through the deployment's
secret mechanism, and set the backend URL to
`http://bridge:8000/github-to-biotools`. Do not publish the service port.
The existing GitHub ecosystem export switch is unrelated and remains separate.

Ordinary Django boolean environment settings accept `1/true/yes/on` and
`0/false/no/off/empty`, ignoring case and surrounding whitespace. Invalid values
fail configuration. Route cutover flags retain their documented `0/1` format to
match both proxy implementations. Existing deployment-settings and blacklist
modules are still supported in development. They are excluded from production
build context; migrate values to environment/secret configuration before rollout.
`ADMIN_EMAIL_LIST` remains used by background notifications and
`BLACKLISTED_DOMAINS_LIST` by URL validation, so neither was silently removed.

Build the production artifact with `docker build --target prod -t IMAGE .`.
The image uses distribution Python 3.10 and its matching mod_wsgi module, rather
than copying Python 3.13 packages into Apache. Modern assets use Node 22. The
production service names remain `backend`/`taskrunner` for operator compatibility;
the production frontend build container is replaced by image build stages.
As of 2026-10-31 the production image no longer includes legacy runtime assets;
legacy development/rehearsal services remain until retirement.
Persist `backend_data` and `media_data`, and back up existing media before moving
from a previous container layout. Do not use volume-purging cleanup commands.
Tag/promote the tested image digest; OS and npm repositories remain external
build inputs. The production build no longer invokes Bower or Gulp.

SPDX/schema updates remain explicit maintenance work: compare the chosen upstream
licence source/XSD, retain historical values, review the selected XSD/policy,
generate the descriptor with `manage.py resource_schema --write`, then run drift,
JSON/XML and activation/rollback checks. No page-load or automatic remote
vocabulary activation was added.

## Local verification

- 106 modern unit/component tests, type checking and Vite build passed.
- 49 focused backend tests passed on both development Python 3.13 and packaged
  Apache Python 3.10, including XML round-trip and public API unchanged-save checks.
- 91 broader backend checks passed, with seven live search checks initially
  skipped. A subsequent enabled Elasticsearch run passed all 16 search tests.
- Desktop/mobile/keyboard import review, stale comparison, draft-only apply,
  protected values, explicit save/reload and provider failure recovery passed
  through Apache and Caddy: three journeys each.
- All 33 affected account, editor, permission, enriched-publication, search and
  disabled-import browser checks passed on each proxy. These include narrow
  viewports, expired sessions, stale writes and native/failed-asset recovery.
- Eight public/detail journeys passed in the packaged image without source mounts,
  including mobile, no JavaScript and failed modern assets. Its descriptor check
  and isolated empty-queue taskrunner startup passed.
- The same-build schema activation/persistence/rollback rehearsal passed through
  both proxies, including newly advertised nested metadata. The base schema was
  restored after the rehearsal.
- Final packaged smoke checks passed for public HTML, REST JSON, modern and
  retained assets, media files and denied media directory listing (403).
  The media check corrected an Apache location override that enabled listing.

The accepted artifact is `biotools-refresh/upstream:review`, image ID
`sha256:e9be6fb9fad2b1db7a4c166b93c9e08616c4232088373723ff55389caea2e99f`.
Its descriptor revision is
`41c6bde30ed530b2de333f02fc848b54da4951624662807703e68c47d451277a`.
The unchanged JavaScript bundle `main-DFPAKDPU.js` has SHA256
`09c43f7fdc652b6795d4b2c99fe6fd5f817eb73bf4af00008066726712baf92f`.
The production-like image has no source mounts. Both asset families remain
required: modern manifest/assets, collected Django/admin/public static, retained
Angular `dist`, templates/components, fonts and vendor assets. Their presence is
packaging evidence, not permission to remove them.

Local reports are in `tests/browser/test-results-github-final-{apache,caddy}`,
`test-results-upstream-final-{apache,caddy}`, `test-results-upstream-packaged`
and `test-results-upstream-schema-retry`.
Schema transition evidence is `/tmp/biotools-schema-636Rsm/evidence.json`;
backend logs are `/tmp/biotools-upstream-final-backend-tests.log` and
`/tmp/biotools-upstream-final-packaged-tests.log`. These local generated reports
are not committed release artifacts. The normal previews on ports 8003/8443 have
the provider URL empty and the deterministic bridge service stopped.

CI configuration was updated and its component checks exercised locally; no
hosted GitHub Actions run is claimed. A sandbox denied the initial final Caddy
test launch; its accepted run uses local network/browser permissions and the
explicit local self-signed TLS option. An earlier schema browser run encountered
`ERR_NETWORK_IO_SUSPENDED`; the complete retry passed without an application fix.

Live model/provider calls, configured production credentials, ORCID/email delivery,
production promotion and removal of legacy dependencies are not part of local
acceptance. The deterministic provider is only a test fixture and must not remain
configured as the normal preview's bridge after the rehearsal.
