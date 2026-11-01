# EDAM selector

Implemented 2026-09-18 in the isolated `develop-migration/` checkout, on accepted
upstream develop `9faec5b3b660498fdef9736e65e331728b55f99c`. The develop refresh,
Vue runtime, search workspace and advanced filtering changes are complete.

## Try the preview

`http://localhost:8003/_migration/html/edam/`

The annotation form offers topic, operation, data and format selection. Try
`sequence` or `FASTA`, choose terms, then **Apply selection**. **Cancel** discards
the dialog draft. **Validate annotations** resolves selected IDs on the server;
it never creates or changes a registry record. An empty annotation label produces
a validation rerender that preserves the selected terms. Data is single-select;
the other fields allow multiple selections. The native URI form also works
without JavaScript.

The same component is adopted in the actual search workspace:
`http://localhost:8003/_migration/html/search/?q=Workspace+sample`

Open **Advanced filters**, then **Choose edam topics**. Committing a selection
updates the candidate-only filter; **Apply to all matches** performs the existing
server-authoritative refinement. The first lookup does not download the ontology.
The Caddy equivalents use `https://localhost:8443` with a local certificate.

## Develop review

- `frontend/js/controllers.js` loads whole `EDAM_topic/data/format/operation`
  trees through the public `Ontology` endpoint. `UsedTermsList` returns registry
  aggregates, not all valid EDAM concepts; it cannot validate concept identity.
- `EdamModalCtrl` copies the edit value, commits through the modal result and
  dismisses on cancel. Suggestions change the lookup predicate/order without
  committing a term. The new dialog likewise separates draft from committed IDs,
  supports suggested IDs and marks them in results; hint buttons search, not save.
- The legacy modal returns data as `{data: {uri, term}}`, but operation/format
  selections as `{uri, term}`. At the resource boundary, topics/operations/formats
  are arrays; input/output `data` is one object. The new selector keeps identity
  as an ID array, and adapters explicitly retain those different field shapes.
- `OntologyValidator` loads the scoped tree and obsolete tree from `Ontology`,
  accepts known obsolete IDs in the same class, and validates URI/term identity.
  The lookup service reuses these trees and the existing validator, passing only
  the ID and resolving the canonical label. Existing public serializers still
  reject conflicting labels; their behavior is covered by a compatibility test.
- Reusing the validator independently exposed its circular model import through
  `elixir.serializers`. Importing `Ontology` directly from `elixir.models` fixes
  the dependency without changing validation rules.
- `backend/data/edam/current_version.txt` identifies the checked-in source as
  1.25. Runtime reads use the same provisioned database ontology as the public
  validators, not a new external provider or a hard-coded frontend vocabulary.

No ontology import/replacement, database migration, legacy editor rewrite or
canonical route cutover is included. Existing recommendation generation remains
with its editor caller; later editor integration supplies its suggested IDs.

## Lookup and validation contract

`GET /_migration/html/edam/terms/` is a read-only, uncached JSON endpoint.

| Parameter | Meaning |
| --- | --- |
| `scope` | Required: `topic`, `operation`, `data` or `format`. |
| `q` | Optional text, at most 128 characters, no controls. Matches label, canonical URI and exact/narrow synonyms case-insensitively. Query words are ANDed. |
| `branch` | Optional current concept URI in the same scope; restricts lookup and resolution to that concept and its descendants. |
| `suggest` | Repeated optional suggested IDs, at most 20. Validated in the same scope/branch; matching suggestions sort first. |
| `id` | Repeated IDs to resolve, at most 20; cannot be combined with `q` or `suggest`. |

All other or repeated singleton parameters are rejected. IDs must use canonical
`http://edamontology.org/<scope>_NNNN` form. Unknown, malformed or wrong-scope IDs
return HTTP 400 `error.code=invalid_edam`; unavailable ontology data returns HTTP
503 `error.code=edam_unavailable`. Errors provide a retryable/user-facing message
without database details. POST to the lookup route is disallowed.

Responses contain `items`, `more` and `suggestions`. Each term contains only
`uri`, authoritative `term`, `definition` (at most 600 characters), `synonyms`
(at most eight) and `obsolete`. Search choices are capped at 20. Suggestions are
also bounded at 20; `more` signals that a narrower query may reveal other choices.
Duplicates from the ontology hierarchy are collapsed by ID. Exact labels rank
before other text matches after suggested IDs; ties sort by label and URI.

Current terms are offered for new selections. Existing obsolete IDs may be
resolved and retained, marked obsolete, following the public validator's policy.
They are not newly suggested by ordinary text search. A branch restriction does
not infer a place for obsolete terms in the current hierarchy.

`EdamVocabulary(scope, branch).resolve(ids, multiple=...)` supplies the reusable
server check. Form fields declare their scope/branch/multiplicity server-side;
the browser cannot change those constraints. `EdamField` integrates with repeated
native form fields and resolves labels on validation. No client label is trusted.

Advanced-search promotion now additionally checks ontology IDs against the topic
vocabulary before Elasticsearch runs. Unknown well-formed IDs return a typed
`invalid_search` error on `advanced`. A valid ontology refinement reads the two
ontology records once, then makes the existing single Elasticsearch query.
Other workspace queries retain the previous zero-SQL path.

## Vue contract

`frontend-modern/src/EdamSelector.vue` is independent of search/editor stores.

| Prop | Meaning |
| --- | --- |
| `modelValue: string[]` | Committed canonical IDs; an array even for single selection. |
| `scope`, `endpoint`, `label` | Required concept class, internal lookup URL and accessible field label. |
| `multiple` | Defaults to true; false replaces the one selected ID when committed. |
| `maxSelections` | Defaults to 20; cannot exceed 20. Search sets 10 to match its membership-filter bound. |
| `branch` | Optional subtree root ID, enforced by lookup and by the receiving server field. |
| `initialTerms` | Optional server-resolved metadata for initial IDs, avoiding redundant resolution requests. |
| `suggestions` | Optional bounded ID list supplied by the consumer; hints do not change committed values. |
| `name` | Optional ordinary-form field name; emits repeated hidden ID fields. |
| `disabled`, `readonly` | Prevent editing. Disabled hidden controls are omitted from form submission; readonly values remain submitted. |

`update:modelValue` emits a new ID array on **Apply selection** or explicit
removal outside the dialog. A parent Vue consumer uses `v-model`; it should not
read DOM chips or hidden inputs to maintain state. `EdamField.vue` is the small
ordinary-form island wrapper: `initial` initializes its local model, with all
selector props passed through. Form rerenders provide original IDs plus canonical
metadata and do not initialize a second conflicting state model.

```vue
<EdamSelector v-model="topicIds" scope="topic" label="Topics"
  :endpoint="edamEndpoint" multiple :max-selections="10" />
```

`edamPayload(scope, resolvedTerms)` projects only `{uri, term}` values: data
returns `{data: firstTermOrNull}` while topic/operation/format return arrays for
their resource fields. A single legacy modal caller takes the first operation or
format term object; input/output callers keep the `data` wrapper. Persistence
must still use the server resolver, regardless of any frontend projection.

The selector uses the native modal dialog for focus containment and restoration.
Its combobox controls a listbox with unique option IDs and active-descendant
tracking. Arrow keys and Home/End navigate; Enter selects; Tab does not silently
select; Escape closes the choices and then the dialog. Remove buttons are
keyboard-focusable. Opening, cancelling and committing restore the appropriate
focus. The island runtime assigns each Vue app an ID prefix so multiple form
islands cannot generate colliding ARIA IDs.

Lookup waits 300 ms after text input. New input immediately aborts/invalidates
the prior request; sequence checks also ignore late responses from transports
that do not honor cancellation. Closing, disabling, scope changes and unmounting
cancel pending choice lookups. Each request has a 10-second timeout. Selected-ID resolution
has its own cancellation sequence and keeps selections outside the current
choice list. Loading, no-match, selection-limit, invalid-selection and retry
states are explicit. Labels/definitions/synonyms render as text, never HTML.

## Verification and measurements

- Build and TypeScript checks passed; all 47 frontend tests passed.
- All 70 focused backend tests passed on both Python 3.13 and Apache/Python 3.10.
- Full browser suites passed all 36 scenarios on both Apache and Caddy,
  zero skips/retries. Their outputs are in `test-results-edam-apache-full` and
  `test-results-edam-caddy-full` under `tests/browser/` (ignored artifacts).
- Browser checks cover all four scopes, keyboard-only selection/cancel/removal,
  single-data and array payloads, validation rerender preservation, bounded
  requests, stale responses, retry, ID uniqueness and native no-JavaScript forms.
- Desktop 1440px and mobile 390px screenshots were inspected. The blue shell,
  dialog, buttons and selection labels have no horizontal overflow or collisions.
- The initial browser assertions were corrected to account for Django's label
  colon and to scope option lookup to the dialog rather than unrelated selects.
  Assertions were not relaxed or retried automatically.

Read-only local lookup samples over the provisioned ontology, query `sequence`,
three runs per scope (median complete Django request, Python 3.13):

| Scope | Choices | Response bytes | Median ms | SQL reads |
| --- | ---: | ---: | ---: | ---: |
| topic | 9 | 4,008 | 41.38 | 2 |
| operation | 20 | 6,035 | 39.46 | 2 |
| data | 20 | 5,102 | 46.09 | 2 |
| format | 20 | 4,051 | 37.24 | 2 |

This is a local baseline, not production-scale load testing. The existing JSON
trees are read/parsed on the server; no cache or schema/index is introduced.
If lookup throughput becomes a measured bottleneck, cache by an explicit
ontology revision rather than keeping an indefinitely stale process snapshot.

Final modern bundle: JS 182.36 kB / 55.54 kB gzip, CSS 7.70 kB / 1.89 kB gzip.
No package dependency was added. Existing htmx eval-build, MySQL conditional
constraint and naive-datetime test warnings remain unchanged.

## Run and rollback

Use the existing [search preview build/collect/reload commands](search-workspace.md#run-and-verify).
Add `elixirapp.test_edam` to the focused Django regression command. New tests use
isolated database fixtures; no preview ontology data is seeded or overwritten.
Enable `BIOTOOLS_TEST_EDAM=1` alongside the other browser opt-in flags; the five
new browser scenarios require provisioned EDAM records, not a new user account.

Rollback removes the EDAM routes/island import and search-selector adoption,
then rebuilds/collects modern assets. There is no schema or data migration to
reverse. Canonical legacy search/editor routes and public ontology endpoints
remain unchanged. The annotation preview validates only; editor persistence,
resource editing and canonical route cutover remain later OpenSpec changes.
