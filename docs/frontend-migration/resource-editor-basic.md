# Basic resource editor

This records the basic-editor milestone. The subsequent
[nested editor](resource-editor-nested.md) adds function editing and extends the
facade's editable-field allowlist; the earlier limits and counts below describe
the basic-only implementation.

Implemented in `develop-migration/` on pinned develop
`9faec5b3b660498fdef9736e65e331728b55f99c`. The develop refresh, Vue runtime,
[data contract](resource-editor-data-contract.md) and
[browser authentication](browser-authentication.md) prerequisites are complete.
Canonical registration/edit routes remain AngularJS-owned.

## Preview

- Create: http://localhost:8003/_migration/html/editor/new/
- Disposable rich example: http://localhost:8003/_migration/html/editor/tool/editor-demo/
- Equivalent Caddy origin: https://localhost:8443 (local self-signed certificate).

Sign in with the disposable fixture account. These pages **really save to the
local registry**, unlike the earlier annotation and session demonstrations.
Account links to registration; authorized users also see Edit basic information
on migrated tool detail pages. Without JavaScript, the page retains a link to
the existing editor, which may require its separate legacy token login.

One Vue root owns the complete form under `hx-disable`. Controls cover name,
explicit bio.tools ID on creation (read-only when editing), homepage, description
and tool types. Tool-type choices come from the same constant used by the existing
serializer. Required/length checks are native usability checks; homepage stays a
text field because the backend also supports FTP and its own URL normalization.
No nested metadata controls or schema-generated forms were added.

The form reports dirty/saving/saved state, disables controls during saves,
warns before leaving or signing out with changes, supports explicit discard and
exports the complete draft as JSON. It stores no draft or credentials in browser
storage. Backend field errors appear beside controls and in a focused summary;
hidden-field/global errors remain visible there. Failed requests retain all input.
Session expiry uses the existing second-tab sign-in and explicit reconnection
flow, without automatic resubmission. A successful create changes the browser URL
to the edit page and subsequent saves use the returned update endpoint/revision.

## Authoritative path

Reviewed develop's `ResourceList.post`, `ResourceDetail.put`, resource and
tool-type serializers, `HasEditPermissionToEditResourceOrReadOnly`, edit-permission
models, publication signals, AngularJS controller submission/permissions logic,
and the refreshed baseline impact matrix.

- Any authenticated user can create. Edit permissions retain the existing
  owner, superuser, public-edit and named group-author rules. Private edit rights
  do not make public registry reads private.
- Django protects both editor pages and JSON POST save endpoints with sessions
  and CSRF. A page-access check uses the existing mutation permission predicate,
  not its read-only GET allowance. The write handler checks permissions again.
- The facade passes the contract snapshot to the existing create/update methods;
  it does not create an API token, change API authentication or copy the resource
  serializer's validation rules. The browser helper now retains error response
  bodies for snapshot-based field mapping.
- Edit saves compare a SHA-256 revision of the loaded row ID and complete resource
  representation with current data under a row lock. Stale drafts receive 409,
  not a silent overwrite. The token is a comparison value, not authorization.
- Creation now accepts the migrated schema fields plus editing permissions.
  Editing requires normalized out-of-scope values to match the stored record,
  including ID and owner. Only owners and superusers may change permissions;
  group/public editors must retain them. Unknown fields, renames and unexpected
  unrelated changes are rejected.
- The existing backend still creates a replacement row and hides the prior row.
  The facade wraps this in a database transaction. A small no-op hook on the API
  handler lets the facade compare actual saved output before Elasticsearch/GitHub
  writes. Unexpected unrelated changes raise 409 and roll back the replacement.
  The ordinary token API retains its existing behavior.
- Preservation comparisons ignore only the editable fields and `lastUpdate`.
  Existing serializer set-valued relations (language, operating system, collection,
  operation and format) may reorder but may not lose values or multiplicity.
  Other nested values are compared directly. Domain membership remains separate.

## Deliberate limits

The 2026-10-06 cutover prerequisites remove the enrichment, badge/homepage-status
and protected-identifier save blockers after fixing persistence. See the
[schema coverage audit](resource-editor-schema-coverage.md#remaining-cutover-gates).
Unsupported fields, forged server values and unexpected unrelated-data loss
still block saves; those drafts remain editable/exportable.

Only new or changed publication identities trigger enrichment during saves;
deterministic backend tests mock HTTP responses. The original browser fixture
omits publications; a separate enriched fixture checks preservation without
network access. EDAM labels resolve from the installed ontology.

Database rollback covers validation/preservation failures and exceptions during
indexing. It cannot make MySQL, Elasticsearch and optional GitHub writes one atomic
operation. An external write may have succeeded before a later failure; network
timeouts therefore say save could not be confirmed and retain the draft. There is
no automatic retry. Inspect the record before retrying an ambiguous failure.
The existing API's missing/duplicate search-document behavior is unchanged.

Revision checks protect edits through this facade, not all concurrent legacy API
writers. They do not add a global database uniqueness constraint or cross-client
locking protocol to the legacy replacement path. These remain cutover concerns.
This change is not production/editor cutover approval, and live ORCID verification
remains the separate pending integration documented by the authentication change.

## Verification

Verified 2026-09-22: **70 frontend unit tests** and **104 migration backend tests
on each of Python 3.13 and Apache/Python 3.10** passed, including 12 new backend
editor tests. The focused Apache browser run passed all seven editor scenarios;
the complete Apache and Caddy suites each passed all 49 tests with no skips or
automatic retries. Results are in the ignored `tests/browser/test-results-editor-apache-full/`
and `tests/browser/test-results-editor-caddy-full/` directories. OpenSpec completion
was recorded on 2026-09-23.

Frontend type-check, unit tests and production build pass. The seven new component
tests cover full snapshots, precise errors, recovery, dirty/discard behavior,
save blockers, duplicate-submit prevention, abort cleanup and create semantics.
Production assets: JS 208.63 kB / 61.23 kB gzip; CSS 9.61 kB / 2.26 kB gzip.
No dependency was added. Existing htmx build and backend baseline warnings remain.

The new backend suite covers rich round trips (including publications, credits,
links, downloads, documentation, functions, relationships and domain membership),
owner/group/public/superuser access, anonymous/private rejection, CSRF/origin
checks, authoritative field errors, creation/uniqueness, hidden-field tampering,
stale versions, preservation blockers, rollback before indexing, index failure,
safe props and write-handler permission rechecks.

Seven opt-in browser scenarios cover desktop/mobile create, invalid backend
values, correction and save, direct reload/edit links, navigation warnings,
rich hidden-metadata preservation, expiry/reconnection, stale tabs, failed saves,
draft download, anonymous access and the native legacy fallback. Screenshots at
1440px and 390px were inspected and horizontal overflow checks pass.

## Run

From the develop checkout, with the disposable preview stack running:

```sh
docker compose -f compose.refresh.json exec -T backend python manage.py test elixirapp.test_resource_editor_basic --noinput --keepdb
```

Repeat with `apache` for Python 3.10. In `frontend-modern/`, run
`npm run type-check`, `npm test`, and `npm run build`; collect static files and
restart Apache to publish changes.

Provision the rich browser fixture once, after the existing fixture account and
ontology have been seeded. The script refuses to overwrite an existing record:

```sh
docker compose -f compose.refresh.json exec -T -e BIOTOOLS_ALLOW_TEST_SEED=biotools-refresh backend python manage.py shell < tests/browser/seed_editor.py
```

In `tests/browser/`, set the dedicated username/password environment variables:

```sh
BIOTOOLS_BASE_URL=http://localhost:8003 BIOTOOLS_TEST_EDITOR_WRITES=1 npm test -- resource-editor.spec.js
```

This extra flag authorizes real disposable writes: tests create uniquely named
`editor-browser-*` records and update/restore `editor-demo`. Records/version history
remain in the disposable database; there is no cleanup against arbitrary targets.
Never enable this flag against production. Full browser coverage also enables the
existing shell/detail/islands/search/EDAM/auth flags. Keep traces private because
they can contain account credentials and complete resource payloads.
