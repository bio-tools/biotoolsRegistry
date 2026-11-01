## Current Evidence

Paths below are relative to the implementation checkout.

- `backend/elixir/editor_contract.py` generates field shapes and basic flags from
  DRF serializers; `resource-contract.generated.ts` is a build-time snapshot.
- `backend/elixir/resource_options.py` and `serialization/resource_serialization/toolType.py`
  hold Python choice lists. Sharing them with the editor reduces duplication but
  does not automatically follow schema updates.
- `backend/elixirapp/resource_editor.py` maintains BASIC_FIELDS/METADATA_FIELDS.
  `frontend-modern/src/MetadataEditor.vue` and `nested-editor.ts` hard-code
  field names, labels and sections. Detail templates and search filters also
  enumerate fields.
- The bundled `biotools_3.3.0-singletool.xsd` describes XML, not the complete
  registry JSON write contract. Its operating-system list lacks Android/iOS,
  and toolType lacks Mobile application present in backend choices.
  These discrepancies require explicit reconciliation, not silent narrowing.
- EDAM comes from the existing Ontology/validator/lookup service. A schema release,
  an EDAM release and registry permission policy are distinct inputs.

## Meaning of Automatic

One selected, versioned schema artifact is ingested and checked on the backend.
Once a compatible revision is activated, supported field metadata and choices
propagate to new page loads without editing frontend code, rebuilding its bundle,
or manually copying option lists. Backend deployment/reload may be required by
the existing runtime; no new live-update service is required.

Upstream publication does not immediately mutate production. The update command
or existing CI workflow must automate ingestion, generation and compatibility
checks for a selected version. Unattended fetching/scheduling and automatic
approval of arbitrary upstream changes are not part of this change. The browser
does not fetch an unpinned external schema on every page load.

## Source and Compatibility Contract

1. Inventory the selected upstream schema artifact's format, version and checksum,
   current serializers/validators, and external vocabulary sources. Use structured
   parsing with an existing parser or standard library, not regex extraction.
2. Generate schema-derived labels/documentation, primitive/structured types,
   choices and supported constraints. Map XML/JSON representation differences
   explicitly; do not assume an XSD can replace DRF validation.
3. Reconcile backend schema-owned enum validation to the same generated source.
   Registry extensions and server-owned policies remain explicit, separately
   identified metadata. Any disagreement is reported and tested, not resolved by
   silently dropping existing accepted values.
4. Produce an effective descriptor only for fields the backend can serialize,
   validate and persist (or explicitly exposes read-only). New persistent fields
   may require model/serializer/index migrations; schema metadata alone cannot
   create storage or search support.
5. Include schema version/digest, descriptor protocol version, vocabulary revisions,
   stable field paths, required/read-only/null/empty rules, supported constraints,
   choices as values plus labels, and server-advertised read/write/search capability.
   Permissions stay enforced by the server and are never inferred from the schema.

Use existing JSON configuration delivery where sufficient. Keep static metadata
separate from per-user capabilities if caching; otherwise use private/no-store.
Do not introduce a separate metadata service or generic schema framework.

## Rendering and Interaction

Reuse EditorField, EditorStrings, EditorRecords and the lossless draft/error-path
mapping. A generic traversal handles supported strings, booleans, numbers,
objects and arrays, including previously unseen optional fields at nested paths.
Metadata chooses labels/options/required markers and applicable familiar controls.
The unsupported-schema-construct path is explicit, not an accidental text input.

Keep the input -> operation -> output diagram, EDAM picker, publication rendering
and protected identifiers as bounded presentation/policy overrides. New fields
inside a specialized section must still appear through the generic fallback;
overrides may not hide additions or freeze enum values. Layout hints are optional:
an unlisted supported field renders without a new frontend mapping entry.

Public detail renders only server-approved public fields, with generic display
for supported additions. Search consumes the same field labels/choices for
server-advertised searchable/filterable fields. A schema field is not automatically
indexed or searchable; unavailable capabilities are not offered. Existing query
semantics and explicit advanced-filter scope remain intact.

No schema-provided executable expressions, HTML injection or arbitrary component
loading. Render labels/help as safe content and constrain links/renderer choices.
Do not expose private owner/account metadata merely because it exists in a serializer.

## Version Changes and Existing Data

| Change | Behavior |
| --- | --- |
| Label/help change with stable field/value ID | Automatic display update after activation; stored IDs unchanged. |
| Allowed value added | Automatic control update and matching server validation from the same source. |
| Value removed/deprecated | Stop offering it for new selection; retain existing value visibly and apply an explicit server preservation/correction policy. Never erase or select a substitute automatically. |
| EDAM label/synonym/obsolescence update | Existing lookup returns the activated vocabulary; retain URI identity and surface obsolescence/replacement suggestions without silently rewriting annotations. |
| Optional supported field added with backend support | Generic editor/detail representation appears without component/template edits. Search appears only with backend capability. |
| Field/value wire ID renamed, type/cardinality changed, or required field added | Compatibility report requires explicit migration/default/alias policy and backend tests before activation. A label rename is not a wire-ID migration. |
| Unsupported construct or missing backend persistence | Reject activation or explicitly quarantine the unsupported field read-only with diagnostic/export support; never claim it was saved. |

Stamp loaded drafts/submissions with the effective descriptor revision separately
from record revision. At save, a changed descriptor must trigger a server
compatibility/revalidation decision or a recoverable conflict, not silent
coercion. Preserve raw draft data and export on conflict, invalid values or
unavailable metadata. Cache invalidation must prevent a mixed set of schema,
choices and permissions from being presented as one version.

Types generated from a schema snapshot remain useful for tests and specialized
renderers, but cannot be the sole runtime allowlist. Unknown fields remain
losslessly preserved locally; server write capabilities still constrain saving.

## Acceptance and Rollout

Create docs/frontend-migration/schema-driven-ui.md with the source manifest,
baseline discrepancy decisions, supported constructs/overrides, refresh command,
version behavior and rollback. Switch one section at a time using existing
components and tests; do not rewrite the editor wholesale.

Tests must swap backend schema/vocabulary fixtures while using the identical
frontend build. Demonstrate label and enum updates, a new optional nested field,
deprecated stored values, EDAM label changes, permissions and non-searchable
fields. Exercise reload/cache and an in-flight old draft. Run round-trip,
serializer/API, type/unit/build and desktop/mobile browser tests through both
proxies; retain function-diagram/schema coverage.

Rollback reactivates a prior compatible descriptor/schema and records what happens
to data written under the newer version. No destructive reverse migration or
blind reactivation of an incompatible older contract.

## Non-Goals

No automatic database evolution, new public API format, arbitrary upstream
auto-deployment, automatic semantic renames, browser-side authority over validation
or replacement of the function diagram with an undifferentiated form.
