# Resource editor data contract

Completed 2026-09-21 in the isolated develop migration checkout, based on
`9faec5b3b660498fdef9736e65e331728b55f99c`. The develop refresh prerequisite is
complete. This change supplies data conversion and tests, not a visual editor,
new persistence endpoint, schema revision, or route cutover.

## Authoritative develop review

Reviewed `backend/elixir/serialization/resource_serialization/` (resource,
EDAM, publication, credit, link, download, documentation, collection, version,
domain), corresponding models, `elixir/validators.py`, `elixir/view/resource.py`,
`elixir/model/resource_model/editPermission.py`, and publication signals.

The JSON authority is `ResourceSerializer` / `ResourceUpdateSerializer` plus
their validators and the POST/PUT views. The XML parser uses the checked-in
biotoolsSchema 3.3.0 XSD and XSLT. The historical test JSON schema is not substituted
for the current JSON serializers. There is no schema or endpoint behavior change.

Develop has no resource `community` or BioLib field. `elixirCommunity` is a
controlled string list; `collectionID` is a separate list of tags. Domain membership
lives in `DomainResource`, keyed by textual biotoolsID, outside the resource payload.
The rich fixture covers every current top-level serializer field without restoring
removed fields. Its EDAM labels match the isolated test ontology from `test_edam`,
not a claim about the latest external EDAM release.

The AngularJS load path recursively deletes nulls and empty lists. Its controls
append objects/strings, delete the property after the last removal, and remove a
function after its final operation is removed. Develop also has `moveItem` array
reordering. JSON editing replaces the object; validation paths use current indices.
The new contract does not adopt that blanket cleanup or index-based identity.

## Types and state

`backend/elixir/editor_contract.py` introspects the existing DRF fields and produces
`backend/elixir/resource-contract.generated.ts`. The generated artifact is stored
beside its Python source so the backend CI/container can compare it without a second
frontend mount. It describes field shapes, required/read-only/null/empty/blank flags,
and the explicit string representations of scalar-list serializers and permission
authors. Unknown serializer classes or new custom representations require review.

`frontend-modern/src/resource-editor.ts` derives `Resource` and `ResourceEditor`
from that artifact. These are draft types: missing and null values are representable
even when submission validation rejects them. They do not duplicate enums, regexes,
permissions, ontology resolution or uniqueness checks. DRF remains authoritative.

- `resourceToEditor(resource)` creates an independent draft and preserves every JSON
  key, including fields with no UI control. It rejects non-JSON/cyclic data.
- Each array item, including scalar strings, becomes `{id, value}` with a fresh
  client-only UUID. Nested arrays use the same convention. Object fields named `id`
  or `value` are ordinary resource data, not reserved metadata.
- `newEditorItem(value)` creates a new item and nested IDs. Move existing wrappers
  when reordering; do not reload the whole resource or clone a wrapper to add an item.
- `editorToResource(editor)` is the lossless local/export conversion. It preserves
  absent/null/blank/empty values and unknown keys, removing only array wrappers.
- `editorToSubmission(editor)` captures an independent, deeply frozen snapshot with
  `payload`, `paths`, `normalizations`, and `blockers`. It rejects duplicate item IDs
  and undefined values. Delete a property to make it absent; do not assign undefined.

The snapshot payload is a complete replacement representation, not a visible-field
patch. Send only `snapshot.payload`, never the draft or the entire snapshot. Future
editor consumers **must stop submission when `blockers` is nonempty**, display the
limitation, and retain the draft/export. They must also account for the reported
normalizations. This module performs no transport or automatic persistence.

Regenerate after an intentional serializer change, from a configured backend Python
environment in `backend/`:

```sh
python manage.py shell -c "from pathlib import Path; from elixir.editor_contract import render_contract; Path('elixir/resource-contract.generated.ts').write_text(render_contract())"
```

The ordinary backend test suite compares the artifact byte-for-byte with current
serializer introspection. CI also runs frontend type-check and unit tests. The
generation check verifies structure, not every custom validator's behavior; shared
fixtures and backend validation tests cover representative semantics.

## Optional and server-owned values

| Value or field | Local representation / submission / backend behavior |
| --- | --- |
| Missing property | Stays absent. PUT is replacement: most omitted writable metadata is cleared, not merged. |
| Optional null rejected by DRF | Retained locally, omitted from submission with `optional-null-to-absent`. GET emits these for unpopulated model fields such as license. |
| Nullable field | Null is retained, e.g. `additionDate` and EDAM `term`. Backend may resolve a supplied URI to a canonical term. |
| Optional empty list rejected by DRF | Retained locally, omitted with `optional-empty-list-to-absent`. This clears that relation on replacement. |
| Allowed empty list | Preserved, notably `editPermission.authors: []`. |
| Required null or empty list | Not silently removed. Required data / operation errors remain backend errors. |
| Empty string | Preserved, never trimmed or removed by conversion. Publication/link/download/documentation note may accept it; license, function note and credit note reject it. Custom enum validation can reject blank despite `allow_blank`. |
| Required basics | Name, description, homepage and biotoolsID are checked by the backend; an incomplete draft is allowed locally. |
| Owner, CURIE, lastUpdate | Retained for local fidelity; serializer ignores their input. POST sets owner/CURIE/dates; PUT copies owner/CURIE/additionDate/ID and refreshes lastUpdate. |
| biotoolsID | Required and syntax-validated on PUT, but the view retains the original ID. This is not a rename API. |
| additionDate | Serializer accepts missing/null/date, but POST supplies now and PUT copies the previous date. Model signal supplies a date if null remains. |
| validated | Serializer read-only, but PUT explicitly honors 0/1 for superusers; otherwise copies the prior flag. Kept in payload, not blanket-stripped. |
| editPermission | Omission on PUT copies existing permissions. Changes are owner/superuser-only. POST omission defaults to private. Authors are username strings, not user objects. |
| confidence_flag | Preserved; POST/PUT enforce their existing role-dependent restrictions. |
| Unknown fields | Preserved locally and in the diagnostic payload, but flagged `unsupported-field`: DRF otherwise silently ignores them. Includes removed `community` and misplaced domain membership. |

No recursive sorting, value deduplication, label rewriting, or required-field
repair occurs in the frontend contract. Invalid legacy values remain visible for
correction rather than disappearing during an unrelated edit.

## Error identity

`backendErrorsToEditor(errors, snapshot)` accepts DRF nested dictionaries, positional
lists with empty placeholders, numeric-key dictionaries, field message lists,
`general_errors`, `non_field_errors`, and global `detail` messages. An error has
`message`, its submitted `wirePath`, and an `EditorPath` using `{itemId}` segments
instead of array indices. An unresolvable index produces `path: null`, not a guess.

`currentEditorPath(editor, error.path)` resolves that identity against the current
draft. Moved items resolve to their new positions. Removed items return null even
if another item now occupies their old index. Missing field errors can still target
the missing field under an existing parent. Keep removed/unlocated errors visible
in a summary. Use the snapshot belonging to that exact request, never a newer
snapshot. The later editor must manage request ordering and stale field errors.

## Explicit backend limitations

These were characterized by the initial contract. Later facade and cutover fixes
are noted explicitly; the mapper itself is not a persistence layer:

1. PUT hides the previous row and creates another. Omitted writable fields are lost.
   The save path is not an atomic database/Elasticsearch transaction and has no
   optimistic concurrency token. This contract does not prevent another user's
   concurrent replacement or a backend failure after hiding the old version.
2. Fixed in the 2026-10-06 cutover prerequisites: replacement now clones read-only
   publication metadata/authors by identifier tuple, without sharing rows with
   history. Unchanged publications retain their enrichment state without a lookup.
   The incompatible enrichment argument count and missing citation-count handling
   are corrected. The facade rejects forged metadata; changed identifiers clear
   stale draft enrichment before submission.
3. Fixed in the same prerequisite: `homepage_status` and `elixir_badge` are copied
   from the authoritative resource rather than reset. Clients cannot change them.
4. The legacy non-superuser API still rewrites protected identifiers before
   validation. The migrated facade instead verifies their unchanged values and
   multiplicity, then bypasses rewriting to preserve submitted error indices.
   Protected controls are read-only. The API superuser path no longer appends
   duplicate stored identifiers. These known values no longer block submission.
5. `create()` deduplicates several lists via sets (toolType, operatingSystem,
   language, collectionID, operation, format), so duplicates/order cannot be promised
   across persistence. The frontend preserves exact order/content up to submission.
   Functions and input/output entries retain fixture order; there is no general
   cross-database order guarantee without explicit model ordering.
6. EDAM and controlled vocabularies can normalize or reject legacy values. Develop's
   `elixirCommunity` deserializer has a narrower enum than its field validator (for
   example Cancer Data). The contract preserves the value and lets validation report
   it; it does not quietly replace it. URL and string validators may also normalize.
7. Domain membership remains independent and survives replacement by textual ID;
   this does not promise the domain's separately stored display name is refreshed.

The basic/nested editor changes must consume these gates. Do not claim every legacy
record is losslessly editable until the relevant backend limitations are resolved.
No canonical editor cutover is authorized by this change.

## Verification

Completed 2026-09-21:

- Frontend type-check passed; 56 unit tests passed, including 9 editor contract tests.
- Production build passed with unchanged assets: JS 182.36 kB / 55.54 kB gzip;
  CSS 7.70 kB / 1.89 kB gzip. Contract code is not yet imported by a UI entry point.
- 79 migration backend tests passed on Python 3.13 and Apache/Python 3.10, including
  9 new contract tests, serializer generation drift, scoped replacement, permissions,
  independent domains, nested error shapes, and known loss/reindexing cases.
- Tests use the isolated test database and synthetic ontology; publication network
  calls and resource-write Elasticsearch calls are mocked. Existing live search
  regressions use their own test indices. Preview records are unchanged.
- Existing MySQL conditional-constraint, naive-date, and htmx build warnings remain.
- No new browser workflow exists for this data-only change, so browser screenshots
  and the prior 36-case browser suite were not rerun. Existing preview restored and
  checked at `http://localhost:8003/_migration/html/edam/` (HTTP 200).

Focused verification from the develop checkout:

```sh
docker compose -f compose.refresh.json exec -T backend python manage.py test elixirapp.test_resource_editor_contract --noinput --keepdb
```

Run the same command with `apache` to check Python 3.10. In `frontend-modern/`, run
`npm run type-check`, `npm test`, and `npm run build`. The existing API CI discovers
the backend contract tests; the new modern-contract CI job checks TypeScript/tests.
