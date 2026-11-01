# Resource editor schema coverage

Reviewed 2026-09-30 against develop `9faec5b3b660498fdef9736e65e331728b55f99c`.
Authority: the repository's `backend/elixir/biotoolsSchema/biotools_3.3.0-singletool.xsd`,
current serializers under `backend/elixir/serialization/resource_serialization/`,
the generated editor contract and legacy `frontend/partials/tool_edit/` forms.
This is a local schema audit, not a claim about a newer upstream schema release.

## Schema-driven update: 2026-10-21

The same 26 top-level fields remain covered. The implementation now derives
runtime metadata from the pinned XSD, effective DRF JSON contract and explicit
registry policy, instead of manually maintained editor field/choice lists.
`resource_options.py` resolves that selected source for validators too; its former
literal lists are replaced by schema values plus reviewed registry extensions.
The older extraction notes below describe the preceding milestone.

Generic controls render supported advertised additions, including inside function
diagrams and EDAM concept records. Required repeated values initialize without
choosing an enum for the user. Public detail projects approved fields and search
uses only existing query capabilities. Schema revision conflicts, unavailable
metadata and removed enum values preserve drafts instead of silently rewriting
or discarding them. Per-user permission and publication/identifier guards remain.

See [schema-driven evidence and activation runbook](schema-driven-ui.md) for
provenance, discrepancy decisions and current tests. Same-bundle schema
activation/rollback passed through both proxies at desktop/mobile widths,
including a new persistent optional nested field backed by the existing
`Download.cmd` column under test-only settings. EDAM label changes also save
without changing URI identity. Unknown nested function objects remain covered
separately by Vue fixtures; no automatic database migration is claimed.

## Current coverage

All 26 top-level fields are accounted for: 24 have editing controls, `biotoolsID`
is entered on creation and immutable on edit, and `biotoolsCURIE` is derived.
The 19 metadata fields omitted by the basic/nested milestones are implemented
in this follow-up. This is control coverage, not permission to cut over the editor:
known replacement-save restrictions below remain in force.

| Schema fields | Current editor |
| --- | --- |
| `name`, `description`, `homepage`, `toolType` | Editable. |
| `biotoolsID` | Entered on creation; read-only on edit. |
| `biotoolsCURIE` | Server-derived; not user-editable. |
| `function` | Editable operations, inputs/outputs, data/formats, note and cmd. |
| `version`, `otherID` | Repeatable versions and identifiers with value, type and version. |
| `topic` | Repeatable EDAM topic selection. |
| `operatingSystem`, `language`, `license` | Authoritative option controls. |
| `collectionID`, `maturity`, `cost`, `accessibility` | Repeatable collections and scalar options. |
| `elixirPlatform`, `elixirCommunity`, `elixirNode` | Repeatable authoritative options. |
| `link`, `documentation` | URL, repeatable type and optional note. |
| `download` | URL, single type, optional note and version. |
| `relation` | Related bio.tools ID and relation type. |
| `publication` | DOI/PMID/PMCID identifiers, repeatable type, version and note. Existing enrichment is preserved; changing identifiers clears stale draft enrichment. |
| `credit` | Name/email/URL alternatives, ORCID/GRID/ROR/FundRef IDs, entity type, repeatable roles and note. |

The function group is complete with respect to its fields and cardinalities:
zero or more functions; at least one operation per function; zero or more inputs
and outputs; exactly one data concept per input/output; zero or more formats;
optional note/cmd. The revised editor restores the legacy input-to-operation-to-output
diagram as the editable surface, not a second unsynchronized preview.

## Authoritative behavior

The UI and serializers share the existing enumeration lists from
`elixir/resource_options.py`; this extraction changes no accepted choices.
Current serializers accept Android/iOS, additional languages (including Rust),
additional licenses, Preprint publications and an extra accessibility choice
not present in the local XSD. The ELIXIR community serializer's actual
`to_internal_value` accepts 13 choices, despite a separate unused validator
listing 19. The UI exposes the 13 accepted choices, not the unused list.
These are pre-existing differences; this change does not redefine the API schema.

Publication identifiers and credit identity/contact alternatives are validated by
the existing serializers. Link/documentation types are arrays; download type is
a scalar. Repeated records retain stable client-only IDs and keyboard-operable
reordering. Scalar set-like lists use add/remove controls; serializer ordering and
deduplication remain authoritative. Unknown nested keys are rejected rather than
silently discarded. The save guard also compares fields the user left untouched,
even when those fields now have editing controls.

## Remaining cutover gates

The 2026-10-06 cutover prerequisite fixes replacement preservation. Existing
publication metadata and authors are cloned by DOI/PMID/PMCID identity so later
refreshes cannot mutate history. Unchanged publications, including unenriched
ones, do not trigger a replacement-time lookup. Changed identifiers clear stale
draft enrichment and use the existing bounded synchronous lookup; corrected
enrichment persistence is tested with mocked HTTP responses, not a live service.
Badge/homepage status is copied from the authoritative record. Protected
`biotools:` identifiers remain read-only, with server checks preventing additions,
changes or removal and preserving submitted validation-error indices.
Forged enrichment, unsupported fields and unexpected unrelated-data loss still
block saves. Revision, CSRF and permission checks remain in place.

Owner/admin permission editing now supports private/public/group and group users.
The server derives `canManagePermissions` from the existing write-handler policy;
it never trusts that flag from a submitted payload. Group/public editors see
read-only permissions, and forged permission changes receive 403. Native username
suggestions reuse `/api/user-list/`; authoritative validation rejects nonexistent
or malformed usernames. Changing modes retains the selected group until users
explicitly remove members. Permission saves use the same CSRF, revision and
unrelated-data guards as schema edits. This is registry metadata, not an extra
bio.tools schema field, and does not change resource ownership or visibility.

Session-backed ownership/editing requests, browser session interoperability and
canonical editor/request cutover are verified under `cut-over-migrated-routes`.
See the route-ownership record for security/browser evidence and rollback.
Canonical account/provider routes remain legacy-owned; live ORCID verification
and retained workflows still block production approval and legacy removal.

## Verification

The metadata backend tests cover all 19 fields, all shared option values,
creation, rich round trips, optional clearing, malformed shapes, nested errors,
unknown keys and preservation blockers. Frontend tests cover unchanged rich
payloads, dedicated controls, credit-error identity after reorder/removal and
identifier error targets. Browser tests exercise real validation, saves, reloads,
clearing and desktop/mobile layouts. See the metadata OpenSpec completion
evidence for final counts and proxy results.
