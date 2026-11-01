# Nested scientific resource editor

Implemented in `develop-migration/` on pinned develop
`9faec5b3b660498fdef9736e65e331728b55f99c`. The completed develop refresh,
[basic editor](resource-editor-basic.md), [data contract](resource-editor-data-contract.md)
and [EDAM selector](edam-selector.md) are reused. Canonical editor routes remain
AngularJS-owned; this is not production cutover approval.

## Preview

- Existing rich example: http://localhost:8003/_migration/html/editor/tool/editor-demo/
- Create: http://localhost:8003/_migration/html/editor/new/
- Equivalent Caddy origin: https://localhost:8443 (local self-signed certificate).

Sign in with the disposable fixture account. These pages **write to the local
registry**. Functions follow the basic fields. Each function has operation
selectors, separate input/output sections, note and command. Add/remove and
keyboard-operable move controls use the existing blue shell styling.

## Schema and develop review

The authoritative local schema is
`backend/elixir/biotoolsSchema/biotools_3.3.0-singletool.xsd`, function definition
at lines 1034-1203. The implementation follows the develop serializers in
`backend/elixir/serialization/resource_serialization/edam.py` and the resource
serializer's create/read behavior, not an older registry payload shape.

| Field | Shape and cardinality |
| --- | --- |
| `function` | Zero or more objects. |
| `function[].operation` | One or more EDAM operation concept objects. |
| `function[].input`, `function[].output` | Zero or more objects. |
| `input[].data`, `output[].data` | Exactly one EDAM data concept object, never an array. |
| `input[].format`, `output[].format` | Zero or more EDAM format concept objects. |
| `function[].note` | Optional text; authoritative serializer length 10-1000. |
| `function[].cmd` | Optional text; authoritative serializer length 1-1000. |

New selections submit `uri`; the existing serializer validates ontology scope,
identity and label and returns canonical labels. Unchanged concepts, including
term-only legacy values, remain intact in the draft. Changing a selection removes
the previous label to avoid mismatched URI/term pairs. Clearing optional note/cmd
explicitly removes that property. No global cleanup of untouched values is added.

Reviewed legacy `frontend/partials/tool_edit/toolEditFunction.html` and
`frontend/js/controllers.js`: operation/data selection creates function/IO
entries, `moveItem` swaps array entries, and the controller removes empty optional
lists. Unlike the legacy last-operation removal behavior, the migrated editor
does not silently delete a whole function with its inputs/outputs and notes.
An empty operation list remains visible and the backend rejects it until fixed
or the user explicitly removes the function. Populated function/IO removal asks
for confirmation; individual concept removal is direct.

Function and input/output list order round-trips through the existing write/read
path and has explicit tests. Operations and formats are deduplicated sets in the
existing serializer, so they have no order controls or order/duplicate-retention
promise. No schema restriction of 20 annotations is invented: each repeatable
concept row reuses the selector in single-value mode; the existing lookup stays
paged and bounded. No model ordinal columns or cross-database ordering guarantee
have been introduced.

## Integrity and validation

`FunctionEditor`, `FunctionIO` and `EdamConcepts` are typed domain components
inside the existing single Vue editor root. They use contract-generated shapes
and stable client-only item IDs. The established submission conversion strips
those IDs, normalizes only known unsupported optional empty/null forms, and
captures validation paths against the submitted snapshot.

Inline errors and summary anchors track item identity after function/IO moves.
Deleting an errored item leaves its submitted error in the summary, without
attaching it to a different item or leaving a broken link. Existing recovery,
export, dirty/discard, pending-state and navigation-warning behavior applies to
the full nested draft.

The session/CSRF facade allows basic fields plus `function` and calls the same
authoritative API handlers. A nested unknown-key check prevents DRF from silently
discarding unsupported keys or leaked editor IDs. Outside those editable fields,
normalized data must match the stored record; actual replacement output is still
checked before external indexing. Backend round trips include publications,
credits, links, documentation, downloads and other untouched metadata. Browser
round trips use the existing rich fixture without publications; publication
enrichment is mocked only in deterministic backend tests.

The basic editor's permissions, stale-revision checks and unsupported-field
blockers remain. The 2026-10-06 cutover prerequisites fix preservation of publication
enrichment, protected `biotools:` identifiers and badge/homepage status; these no
longer prevent saves. Forged server values and unexpected unrelated-data loss
still block replacement. See the [schema coverage audit](resource-editor-schema-coverage.md).
Legacy replacement may normalize edited function data as described above.
MySQL, Elasticsearch and optional GitHub writes are not one atomic transaction;
ambiguous failures retain the draft and require checking before a manual retry.
Revision locking is not a global concurrency protocol for legacy API writers.
Live ORCID verification remains a separate authentication integration gate.

## Verification

Frontend type-check and production build pass; **76 unit tests** pass, including
six nested editor tests. Production assets are JS 222.34 kB / 63.93 kB gzip and
CSS 10.98 kB / 2.52 kB gzip. No dependency was added. Existing htmx build and
backend baseline warnings remain.

The eight nested backend tests check XSD cardinalities against serializers,
multi-function creation, precise invalid-format paths, required operations and
single-data shape, optional removal, rich metadata retention, unknown-key
rejection, CSRF, permissions and stale revisions. The full migration suite has
112 tests on each of Python 3.13 and Apache/Python 3.10.

Four new opt-in browser scenarios cover desktop/mobile creation with multiple
operations and inputs/outputs, multiple formats, independent note/cmd values,
keyboard moves, populated removal cancellation/confirmation, reload/readback,
absence of client IDs, real nested validation/recovery and rich-record retention.
The invalid-format scenario changes a request once at the transport boundary;
the error response and corrected save come from the real backend. Screenshots at
1440px and 390px were inspected; unique DOM IDs and no horizontal overflow are
asserted. Full proxy-suite results are recorded in the completion evidence below.

## Run

From the develop checkout, with the disposable preview stack running:

```sh
docker compose -f compose.refresh.json exec -T backend python manage.py test elixirapp.test_resource_editor_nested elixirapp.test_resource_editor_basic elixirapp.test_resource_editor_contract --noinput --keepdb
```

Repeat with `apache` for Python 3.10. In `frontend-modern/`, run
`npm run type-check`, `npm test`, and `npm run build`; collect static files and
restart Apache to publish changes.

Use the existing guarded `seed_editor.py` fixture and dedicated test-account
credentials, then from `tests/browser/`:

```sh
BIOTOOLS_BASE_URL=http://localhost:8003 BIOTOOLS_TEST_EDITOR_WRITES=1 npm test -- resource-editor-nested.spec.js
```

Tests create unique `nested-browser-*` records and update/restore `editor-demo`.
Version history and created records remain in the disposable database. Never run
these write tests against production. The fully enabled browser suite has 53
scenarios. Keep traces private: they may contain credentials and full payloads.

## Completion evidence

### Diagram and metadata follow-up

The editable function surface now shows inputs, directional connectors,
operations and outputs in a horizontal desktop flow and vertical mobile flow.
Compact EDAM labels open the existing selector; note/cmd remain below the flow.
There is no second diagram state to synchronize. Browser checks assert geometry,
keyboard selection, unique IDs and absence of overflow at 1440px and 390px.

The user's requested metadata expansion is implemented alongside this correction.
See [all 26 schema fields and remaining cutover gates](resource-editor-schema-coverage.md)
and `migrate-resource-editor-metadata` for current verification evidence. The
original milestone evidence below remains historical, not a full-parity claim.

### Original milestone

Verified 2026-09-23: all 76 frontend unit tests, type-check and production build
pass. All 112 migration backend tests pass on both Python 3.13 and Apache/Python
3.10; the strengthened rich-record operation-edit test was rerun on both.
The four focused browser checks pass, and the full Apache and HTTPS/Caddy runs
each pass **53 tests with no skips or automatic retries**. Ignored artifacts are
in `tests/browser/test-results-nested-apache-full/` and
`tests/browser/test-results-nested-caddy-full/`. All 17 OpenSpec changes pass
strict validation. Changed editor files have no trailing whitespace; repository
`git diff --check` still flags pre-existing CRLF lines in `backend/runtime/apache.conf`,
which this change does not modify.
