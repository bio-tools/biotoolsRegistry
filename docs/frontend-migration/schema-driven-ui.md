# Schema-driven resource UI

Status: local acceptance complete, 2026-10-21. This is not production approval.
Implementation checkout: `develop-migration`, pinned develop
`9faec5b3b660498fdef9736e65e331728b55f99c`. Paths below are relative to it.

## Authority and source manifest

The effective contract combines three local, reviewed inputs:

| Input | Authority |
| --- | --- |
| `backend/elixir/biotoolsSchema/biotools_3.3.0-singletool.xsd` | Selected schema 3.3.0; labels, documentation, enum wire values and source constraints. SHA-256 `c5e5fde7980b3e0fdaf45ff069fecbb618421fd8c8f87f66d5093815e08282a5`. |
| `ResourceSerializer` / `ResourceUpdateSerializer` and their validators | Actual JSON shapes, required/null/empty rules, validation and persistence. XSD XML constraints do not replace these. |
| `backend/elixir/biotoolsSchema/registry-ui-policy.json` | Explicit registry extensions, public/write/search capabilities and bounded layout hints. |

`resource-ui.generated.json` is the approved effective descriptor, not a second
hand-maintained field list. Its protocol is 1; its revision hashes the schema
provenance, policy digest and effective contract. The 2026-10-21 acceptance revision was
`1463298031bf613ea7b161fd027a6da87a6faa6ac5a608fdc5a0fd399b60d10a`.

The subsequent [search parity change](search-filter-parity.md) expands declared
aliases for existing backend search fields. Its approved revision is
`6ab2490fa587b187de771a4c4cdc89da6407c83b5c31413de6de967b58b1a535`;
the activation/rollback results below remain evidence for the earlier revision.

EDAM remains separately authoritative in the registry `Ontology` table.
Lookup responses identify EDAM, scope and source and include a SHA-256 revision
of the current and obsolete trees. This is a content revision, not an invented
upstream release number. URI identity is independent of labels and revisions.

## Source audit and discrepancies

The former choice literals in `resource_options.py`, `toolType.py` and the
separate ELIXIR-community validator now resolve through `SchemaChoices`.
The registry policy preserves the previously accepted JSON vocabulary:

- Android and iOS; Mobile application; Preprint; Open access (with restrictions).
- Twelve extra languages, including Rust, Go, TypeScript and Kotlin.
- The existing additional license values and Biodiversity/Systems biology
  communities, with exact case-sensitive wire values recorded in the policy.
- Icarus remains excluded because the existing JSON validator did not accept it.

The policy is an explicit compatibility decision, not a claim that these values
are in the bundled XSD. Choice labels are presentation only; submitted values
remain stable identifiers. Changing a label must not rename a stored value.

Registry-only paths classify owner, dates, status/badges, edit permissions and
publication enrichment. Existing public owner username/dates/badges and public
publication metadata remain public; permission authors are not public. Owner
permission editing still uses its separate per-user server policy. A serializer
field alone is not permission to expose or edit it.

The runtime editor no longer uses the old metadata-field allowlist or dedicated
metadata controls. Generic traversal handles strings, numbers, booleans, objects
and arrays of primitives/objects. Function diagrams, EDAM selection, basic identity,
publication enrichment and protected identifiers retain bounded behavior.
Generic fallback inside functions, IO and concepts handles additional advertised
fields. Static generated TypeScript shapes remain useful for those specialized
components and tests, but are not the generic submission allowlist.

Public detail recursively projects only approved fields. Search consumes metadata
only for its existing 12 supported simple query aliases. Schema additions do not
create an index or new filter semantics; broader parity belongs to the next change.

## Protocol and safety

The parser uses defused XML parsing and local lxml schema compilation. Supported
constructs include named/ref elements and types, primitive restrictions, repeated
elements, sequences and the existing choice groups. Unknown XSD constructs,
unsupported element attributes, group cardinality and unresolved/recursive types
are rejected. Nested annotation text cannot overwrite a parent field's help.
DRF custom representations and array item types require explicit support.
The browser rejects unknown protocol/kind combinations and nested arrays.

The descriptor separates effective JSON constraints from `schema*` source
constraints. New schema paths must have backend serializer support, and write
and public exposure require explicit policy. No automatic model/index migration
is attempted. New persistence needs its own backend implementation and tests.

The editor receives `schemaRevision` separately from the record `revision` and
submits both. A changed descriptor produces a recoverable 409 before mutation;
missing/unverified metadata produces 503. Drafts remain exportable. Missing or
unsupported frontend metadata disables editing and saving rather than guessing.
Removed enum values remain visible and retained in drafts, but require correction
before saving; the authoritative validators reject them too. No replacement is
selected automatically. Non-writable nested data is compared on the server,
allowing reorder but not replacement or removal. CSRF, identity, record revision,
permission and publication-preservation checks remain independent.

Editor/detail/search metadata pages and EDAM lookups are not cacheable. Parsed
sources and the approved descriptor are process-cached; source activation requires
reloading all backend workers. Mixed sources fail provenance/equality checks.
An EDAM response with a new revision invalidates selector caches and re-resolves
selected URIs without silently changing their identity.
Submission sends a recognized EDAM concept's stable URI without its cached label,
so the backend resolves the current label. Drafts and local exports retain the
original label losslessly; term-only and malformed values still reach validation.
The public API's strict URI/term consistency validation is unchanged.

## Generate, activate and roll back

Run these commands from `backend/` in the configured backend environment. The
disposable stack equivalent prefixes them with
`docker compose -f compose.refresh.json exec -T backend` from the checkout root.

```sh
python manage.py resource_schema --check
python manage.py resource_schema --schema /review/candidate.xsd --schema-version candidate --policy /review/policy.json --output /review/descriptor.json --against /release/descriptor.json --write
```

Use an operator-writable output path. `--write` atomically replaces only the
descriptor after generation and compatibility checks succeed. It does not fetch
upstream files, activate a release or change storage. `--check` detects drift;
CI runs it alongside backend tests. Review the schema, policy and generated diff
together and run serializer/round-trip tests before deployment.

Stage immutable files together and select them using Django deployment settings:

```python
RESOURCE_SCHEMA_PATH = '/release/candidate.xsd'
RESOURCE_SCHEMA_VERSION = 'candidate'
RESOURCE_UI_POLICY_PATH = '/release/policy.json'
RESOURCE_UI_DESCRIPTOR_PATH = '/release/descriptor.json'
```

These are Django settings, not automatically imported shell environment variables.
The existing `elixirapp.deployment_settings` hook can supply them. Reload all API
and HTML workers, including the Apache and Caddy-backed applications; check the
new page configuration and a validation/save round trip. Do not rebuild the
frontend merely for compatible metadata/choice updates. Old tabs must retain their
draft and receive the schema-revision conflict rather than saving under mixed rules.

Compatibility rejects field removal/rename, newly required fields, type or
cardinality/constraint changes, changed public/write permissions and simultaneous
enum removal/addition that might be a wire-ID rename. A migration needs explicit
backend review; deleting the previous snapshot is not a safe bypass.

For rollback, run the previous sources as the candidate with `--against` pointing
at the currently active descriptor, using a separate output path. Inspect records
written since activation. Removing a newly added enum uses the same correction-
required policy: retain its stored value visibly and require a deliberate correction
on subsequent save. Do not erase it in a reverse migration. Field removal or
incompatible storage rollback is blocked. After approval, select the previous
compatible source set and reload all workers. The isolated two-proxy rehearsal
below verifies compatible rollback and blocks removal of a newly stored field.

### Repeat the isolated rehearsal

With the disposable `compose.refresh.json` preview running and modern assets
already built and collected, run from `tests/browser`:

```sh
BIOTOOLS_SCHEMA_REHEARSAL=biotools-refresh PLAYWRIGHT_BROWSERS_PATH=/tmp/biotools-playwright npm test -- schema-update.spec.js --output=test-results-schema-transition
```

Do not run builds, other browser suites or backend restarts concurrently. This
temporarily replaces the local preview with isolated fixture data, checks the
served JavaScript hash across both proxies and restores normal settings afterward.
The test-only Django settings reject databases outside `test_schema_ui_<random>`;
the search index uses that same isolated name. Normal preview data is not replaced.
The fixture exposes the existing `Download.cmd` column through a test-only
serializer and explicit schema/policy addition, proving real storage without
claiming automatic model migrations. Final storage assertions select current
records (`visibility=1`); historical versions intentionally retain old values.

Generated source snapshots, override configuration and evidence remain in the
logged `/tmp/biotools-schema-*` directory. Its database/index remain for inspection;
remove only those exact disposable names when no longer needed. After a forced
interruption, restore normal settings from the checkout root with
`docker compose -f compose.refresh.json up -d --no-deps backend apache`.
See [browser rehearsal instructions](../../tests/browser/README.md#same-build-schema-activation-rehearsal).

## Verification evidence

On 2026-10-19, after the required-label, required-repeatable and annotation fixes:

- 185 backend tests passed on both the Python 3.13 backend and Python 3.10 Apache
  image, including live query tests, schema ingestion/compatibility, editor
  preservation, permissions and request saves.
- 94 modern unit tests passed; type-check and production build passed.
- Apache: 30 desktop/mobile browser tests passed (1440px and 390px), covering
  detail/native fallback, EDAM, metadata, function diagrams, basic editor and search.
- Caddy HTTPS: the same 30 desktop/mobile browser tests passed, using the same
  built frontend assets. Both proxy runs used a single worker and no retries.
- Strict OpenSpec validation passed.
- Inspected mobile function/detail and desktop credit screenshots; browser checks
  also cover overflow, duplicate IDs, errors, reload and persistence.

Bundle: `main-CFUwi-Ne.js`, SHA-256
`95ae91e1948c0c74775a4eab1a41647b4e3a39b6d04d3499b62dafd4249e6090`.
The existing htmx eval build warning, MySQL conditional-constraint warnings and
fixture naive-date warnings remain. These runs are not a dependency/security audit.

Backend fixtures cover label/help and enum activation, removed-value validation,
unapproved sources, required/cardinality/type/ID changes, missing backend support,
unknown constructs and compatible label rollback. Vue fixtures cover a previously
unknown nested object inside a function diagram, primitive arrays, stable choice
values, removed choices and unavailable metadata. EDAM backend/Vue fixtures cover
revision and label changes without URI substitution.

### Same-build activation and rollback: 2026-10-21

`schema-update.spec.js` passed through Apache HTTP and Caddy HTTPS at 1440px and
390px, without retries or a frontend rebuild between source activations. Every
page's served JavaScript matched `assets/main-BahO6ryL.js`, SHA-256
`9bf7042718a46734ccbbd165c1f79509b2ef7e27dad370ebf7d32a5331008d8e`.

- Added label/help and the `Preview` enum choice appeared and saved.
- Newly advertised `download.cmd` rendered, persisted, reloaded and appeared in
  public detail. Search consumed updated supported labels without inventing a
  filter for the new field.
- Function diagrams retained their generic annotation field with its new label;
  Vue fixtures separately verify a previously unknown nested function object.
- Old tabs received 409 and retained/exported their unsaved drafts. EDAM lookup
  caches refreshed labels while preserving URI identity; subsequent saves resolved
  current labels on the backend instead of submitting stale cached terms.
- Removed `Mature` remained visible, disabled saving until corrected, and was
  rejected with 400 when injected into a fresh submission. No silent replacement.
- Compatible rollback restored labels and the `Mature` option while retaining all
  four current records' `Preview` values, new column data and stable EDAM URIs.
  The generator also rejected rollback that would remove `download.cmd`.

Activated descriptor revisions:

| Phase | Revision |
| --- | --- |
| Added | `0b276773c1d1ca440bbdb21cbc1ac7451b877a65f8c04d4d4293086f18fc6080` |
| Removed | `fd08b5fb40c9c3f7ebb5886cab0f305ab2056aba776f0abcca566fc05e030b35` |
| Compatible rollback | Same as Added |

Passing evidence: `/tmp/biotools-schema-QZVecR/evidence.json`, isolated database
and index `test_schema_ui_c283a9a7`, and
`tests/browser/test-results-schema-transition/`. Desktop/mobile new-field
screenshots were inspected; layout and horizontal-overflow checks passed.
Normal preview settings were restored automatically.

The updated EDAM submission logic passed 96 modern unit tests, type-check and
production build. After the rehearsal, 186 backend tests passed in each runtime
(Python 3.13 backend and Python 3.10 Apache), including the new real-storage EDAM
label-update regression. The normal descriptor drift check passed with the
unchanged approved revision recorded above. Existing htmx/MySQL/fixture-date
warnings remain; they are not new failures or a security-audit result.

On the restored normal preview, all 30 desktop/mobile browser regressions passed
through Apache and the same 30 passed through Caddy HTTPS, with one worker and
no retries. These cover native/read-only fallback, permissions, enriched data,
function diagrams, validation, sessions, conflicts, EDAM and search. Results are
in `tests/browser/test-results-schema-apache/` and
`tests/browser/test-results-schema-caddy/`. Together with the same-build rehearsal,
this closes tasks 4.1 and 4.4; CI retains the schema drift check.

Production deployment, live ORCID, real email, arbitrary database migrations and
legacy deletion remain outside this change's local verification.
