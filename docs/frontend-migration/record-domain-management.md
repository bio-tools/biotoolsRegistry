# Native record and domain management

Local acceptance: 2026-10-28, in `develop-migration/` on the preserved
`9faec5b3b660498fdef9736e65e331728b55f99c` checkout, with the accepted
[`400bbe32` upstream integration](upstream-dev-integration.md). This is not
production activation or permission to delete
legacy code.

## Reviewed contracts and replacements

| Existing interaction | Native replacement and policy |
| --- | --- |
| Profile Disown / detail Manage record | `/<id>/manage`, authenticated native confirmation form. Only the current owner or a superuser can disown; ownership transfers to the existing `admin` account. Missing admin configuration fails without changing the record. |
| Editor Remove | Same confirmation page, superuser only. Removal hides the current database version and deletes its search documents. Ordinary owners retain disown/request flows. |
| Raw JSON and Validate | Existing editor now exports, edits, validates and explicitly applies JSON to the draft. `register/validate/` and `/<id>/edit/validate/` use the save facade's schema revision, current record revision, authorization and protected metadata checks. Validation never calls save or indexing. |
| `/domain-manager`, `/subdomain` | Native owner/editor domain list; superusers can manage all current domains. |
| `/edit-domain[/<id>]`, `/edit-subdomain[/<id>]` | Native create/edit forms with title/subtitle/description, existing private flag, tags, collections, resource membership and editors. Both slash variants and aliases remain. |
| Domain editor picker | Extracted the existing permission picker's username lookup into `UserPicker.vue`; both callers retain debounce, cancellation, stale-response guard, Enter selection, duplicate exclusion and empty/error states. Native textarea remains when assets fail. |
| `/workflows` | Public server-rendered list and literal text filtering over workflow IDs/descriptions and annotation titles/descriptions/EDAM terms. No browser authoring was added. |
| Annotated workflow image | Proportional focusable regions target full annotation details, usable with keyboard/touch and without JavaScript. Invalid coordinates omit the region but retain details. Unsafe stored external links render as text. Missing media/data and image transport failures have explicit recovery states. |
| Editor without JavaScript/assets | Honest unavailable message, retry, record navigation and stored JSON export. No automatic Angular fallback. |

The review found that `IsOwnerOrReadOnly` allowed any editor of a public record to
disown it, although disowning was presented as an owner's action. The shared
permission now requires actual ownership or superuser rights. Public/group
metadata editing still uses `HasEditPermissionToEditResourceOrReadOnly` and is
unchanged. The same owner check also covers the retained edit-permissions API.

Domain editor/delete restrictions previously existed mainly in Angular controls.
The shared API now enforces owner/superuser-only editor changes and deletion;
assigned editors can still edit domain metadata and membership. `all` and
`covid-19` cannot be deleted, including through direct API calls. The existing
`all` name reservation remains. Updates must target the URL's domain, preserve
ownership and retain editors when omitted. Unknown/hidden member IDs and unknown
editors produce validation errors instead of silently disappearing.

The historical `is_private` flag is preserved; it is **not** a privacy boundary:
the existing domain directory/API expose domain metadata. The form says so.
Workflow API authentication/authoring policy and staff admin interfaces remain;
the existing workflow API's missing response imports and missing-object handling
were repaired. Historical resource version browsing/creation was not established
as a supported browser workflow and has not been invented here.

Empty domain-create aliases are reserved before tool-ID matching, including when
management is rolled back. New resource registration now checks the existing
reserved-keyword policy; update requests retain their existing identifiers.

## Mutation and recovery boundary

Native destructive actions require POST, a valid browser session, CSRF and an
explicit checked confirmation. Native record/domain updates compare the rendered
revision with current serialized state under a row lock. Ownership/editor changes,
replaced versions, hidden records and duplicate submissions cannot reuse an old
confirmation. Shared write handlers repeat their current-object authorization.
Domain creation rejects existing names, including case-normalized duplicates.

Domain writes and record disown/removal wrap database changes and synchronous
index requests in a transaction. Index failure rolls database changes back and
returns an error, with the submitted form/draft retained. Successful index
changes request `refresh=wait_for`; deletion tolerates an already absent document.
Record removal notifications are scheduled after database commit.

Shared record creation and updates also wait for search refresh before reporting
success. The final Caddy checks exposed a race where immediate disown/removal
could not see a just-created document, leaving a duplicate or stale result. The
fix is in the shared save handlers, with immediate create/disown and create/remove
browser checks through both proxies. Five affected disposable test fixtures were
reconciled from their current database state; no registry records were changed.

MySQL and Elasticsearch do not share a transaction. A timeout can occur after an
index write was applied, or a database commit can fail after indexing. These cases
are reported as unconfirmed rather than successful. Recovery is to inspect the
visible database version, then reindex that version (or remove the document if
the database record is hidden), verify detail/search/domain membership and only
then retry. Do not restore data by submitting the stale form blindly. The original
versioned domain model has no database uniqueness constraint for active names.
A later readiness change serializes application domain creation by normalized
name; see [concurrency and recovery evidence](production-readiness.md#domain-concurrency-and-index-recovery).

JSON edits are parsed into a temporary candidate and checked authoritatively
before application. Invalid text remains exportable; the form cannot save over
unapplied text. A form edit after loading JSON forces renewed comparison.
Unchanged repeated annotations retain their client identities through the existing
draft merge helper. Applying JSON or GitHub suggestions still does not save.

## Routing, media and rollback

`BIOTOOLS_CUTOVER_MANAGEMENT=1` enables native management routing before crawler
handlers on Apache and Caddy. Normal development/production defaults remain `0`;
the disposable refresh preview defaults to `1`. Disable this switch in both
backend and proxy environments to restore the retained domain/workflow owner.
The explicit `_legacy=1` escape hatch is retained. Existing editor/account/search
switches remain independent. The new record `/manage` path has no historical
equivalent; links revert to legacy detail/profile when management is disabled.

The editor's validation-only endpoints follow the existing editor switch and
preview aliases. API paths retain their existing authentication and routing.
API-side permission corrections stay effective even when browser routing is
rolled back.

Workflow media uses persistent `media_data` at `/elixir/application/media_cdn`.
The development/refresh backend and proxies share this volume; Caddy mounts it
read-only and serves `/media/*` without directory listing. Production Apache and
taskrunner already use the same persistent-media layout. The disposable preview
had zero media entries before mounting its new volume. For an existing deployment,
copy and verify existing media before replacing a container-local directory with
a volume; never purge persistent volumes for this change.

## Local verification

- 110 frontend unit/component checks, type checking and Vite build passed.
- 73 backend management/editor/route/account/request checks passed on development
  Python 3.13 and Apache Python 3.10. After the search-refresh fix, the 40 affected
  management/editor checks passed again on both runtimes.
- 13 new desktop/mobile browser journeys passed on each proxy, including real-index
  domain search, native forms, JSON validation/apply/save, disown, superuser removal,
  image scaling, keyboard navigation and failed assets/media.
- Mobile domain and workflow screenshots were inspected; content fits the narrow
  viewport and annotations remain aligned and independently readable.
- Adjacent account, permissions, enriched editor, stale/session recovery, search,
  public navigation and failed-runtime checks passed. Apache covered 54 unique
  checks across the main run and two corrected navigation checks; Caddy covered
  47 across its main run and corrected native navigation checks. Initial failures
  were outdated tests assuming workflows still belonged to Angular, followed by
  an unsuitable explicit-rollback starting page. Updated navigation checks use
  the configured route owner and passed on both proxies.
- The final restored-preview checks passed: five on Caddy and three on Apache,
  including exact search counts and ownership immediately after disown/removal.
  These close the three Caddy failures that revealed the search-refresh race.
- Management disabled/restored through real Compose configuration on both proxies.
  Domain list/create aliases and workflows returned retained Angular when disabled;
  native routes returned after restoration. Public/API ownership, image bytes and
  denied directory listing remained correct. Counts stayed at 1,083 resource
  versions (381 visible), 25 domain versions (one visible) and one workflow during
  this read-only rehearsal. Evidence: `/tmp/biotools-management-rollback.json`.
- Apache and Caddy configuration checks, whitespace checks and strict validation
  of all 26 OpenSpec changes passed.

Backend logs: `/tmp/biotools-management-tests.log` and
`/tmp/biotools-management-apache-tests.log`; final affected-test reruns are in
`/tmp/biotools-management-refresh-tests.log` and
`/tmp/biotools-management-refresh-apache-tests.log`. Browser artifacts:
`tests/browser/test-results-management-apache` and
`test-results-management-final-{apache,caddy}`, supplemented by
`test-results-management-navigation-{apache,caddy}` and
`test-results-management-restored-{apache,caddy}`. Fixtures require the existing disposable
seed opt-in; `seed_management.py` adds only a named fictional workflow and isolated
test administrator, preserving existing records. Tests create unique records and
domains rather than deleting registry data.

No production rollout, live provider/email calls, load test or legacy deletion was
performed. Cross-page visual polish and release hardening remain separate changes.
