# Legacy resource editor behavior

Develop review (2026-09-12): see [editor and data integrity](develop-refresh.md#editor-and-data-integrity)
for the pinned upstream changes and acceptance limits. That review supersedes
conflicting old-baseline observations below; historical evidence is retained.

Baseline note: this document describes the old `a1fc8b9` worktree.
The [selected upstream develop baseline](baseline.md) has separate completed revalidation;
the source observations and test results below are not develop acceptance evidence.

Inspected commit: `a1fc8b94067f33bc9047efc9c75ebe1579365a07`.
Inspection date: 2026-09-09. Source inspection only; no tool was created, updated or deleted during inventory.

## Load, identity and save

`register` uses `ToolCreateController`; `tool.edit` is a child of `tool`, whose [ToolPageController](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/components/toolPage/toolPageController.js) fetches the resource. Both create/update controllers invoke the shared `ToolEditController` in [controllers.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/controllers.js). Update inherits the parent `software` object rather than making a separate pristine copy.

| Stage | Existing behavior | Preservation concern |
| --- | --- | --- |
| New tool | After 100 ms, initializes owner from `User`, empty name/description/homepage, no other fields. | Optional fields are generally absent; backend determines ownership and defaults private edit permission when none supplied. |
| ID generation | Name edit removes characters outside ASCII letters/digits/underscore/tilde/space/dot/hyphen, replaces space runs with `_`, lowercases. Edit ID/From Name toggles manual entry. | Backend also requires initial alphanumeric, forbids trailing dot and requires uniqueness. Client normalization alone does not establish validity. |
| Existing tool | Parent `cleanNulls` recursively deletes null-valued properties and zero-length arrays before editing. Empty strings/objects are not generally removed. | A load/save already operates on a transformed resource, including fields not shown in the visible form. Keep original data in the future contract. |
| Permissions | Owner can edit data and permissions. Otherwise, `initializePermissions` computes editability through `CheckUserEditingRights` and deletes `software.editPermission` from the payload. Helper also permits superuser/public/group access. | UI gate differs from backend authority; permission omission is intentional for non-owners. Public edit permission still requires authenticated API writes. |
| Validate | POST `/api/t/validate` for create, PUT `/api/t/:id/validate` for update; shared `sendResource` sends `$stateParams` and `software`. | Validated response does not replace `software`; server normalization can differ from displayed state. Validation is not a precondition for Save. |
| Save | Confirm then POST `/api/t/` or PUT `/api/t/:id`; delay 100 ms. Separate saving/validation/deletion flags. Create success goes to `tool.edit`; update success only changes flags. | Save is disabled by its own in-progress flag, not form validity or JSON parse status; 100 ms does not cover the JSON textarea's 1000 ms debounce. |
| Delete | Two confirmations, DELETE `/api/t/:id`; success alert and search navigation. | Backend allows only superuser removal; UI exposes button more broadly. |
| Leave | Update's Go to entry always warns to save first and reloads detail after confirmation. | No general dirty tracking, `beforeunload` or navigation-discard guard found; navbar/Back/reload are not protected by this specific prompt. |

Evidence: [controllers.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/controllers.js) (`ToolEditController`, `ToolCreateController`, `ToolUpdateController`), [services.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/services.js) (`CheckUserEditingRights`, Tool/validators), [toolEdit.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/toolEdit.html).

## Fields and repeated structures

The included editor tabs below all share `software`. View-only expand/filter/selection state is normally stored under separate `meta`; repeated entries use `track by $index` and index-based server error paths. Options come from hard-coded lists in ToolEditController, not a fetched schema.

| Included template under `frontend/partials/tool_edit/` | Editable state |
| --- | --- |
| [toolEditSummary.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditSummary.html) | Name, create-time biotoolsID, description, homepage; repeatable version strings. |
| [toolEditFunction.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditFunction.html) | Repeatable `function`: repeatable EDAM `operation`, repeatable `input`/`output`, each with `data` term and repeatable `format`; function `cmd` and `note`. |
| [toolEditLabel.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditLabel.html) | Tool types, topic terms, operating systems, languages, license, cost, maturity, accessibility, collection tags; COVID-19 shortcut; ELIXIR platform/node/community lists, confidence_flag and repeated otherID `{value,type,version}`. |
| [toolEditLinks.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditLinks.html) | Repeated link `{url,type:[...],note}`. |
| [toolEditDownload.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditDownload.html) | Repeated download `{url,type,version,note}`; type is a scalar. |
| [toolEditDocumentation.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditDocumentation.html) | Repeated documentation `{url,type:[...],note}`. |
| [toolEditPublications.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditPublications.html) | Repeated publication IDs (`doi`, `pmid`, `pmcid`), type list, version, note; backend-enriched metadata may be present in loaded objects. |
| [toolEditCredits.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditCredits.html) | Repeated credit: name, email, URL, orcidid, gridid, rorid, fundrefid, typeEntity, typeRole list, note; name suggestions. |
| [toolEditRelations.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditRelations.html) | Repeated relation `{biotoolsID,type}` with registry ID suggestions; relationship options include version, uses and includes directions. |
| [toolEditCommunity.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditCommunity.html) | Collection shortcuts (`Rare Disease`, `COVID-19`); `community.biolib.app_name`, `author_username`, `author_name`. |
| [toolEditJSON.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditJSON.html) | Entire resource JSON, raw server error JSON, compact/pretty local download. Fields without a dedicated included tab can still travel through this path. |
| [toolEditPermissions.html](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/partials/tool_edit/toolEditPermissions.html) | Private/public/group `editPermission.type`, group author selection/removal through PermissionsController. The tab is shown for owner or superuser, although shared initialization can remove editPermission for a non-owner superuser. |

`toolEditContact.html` exists but is not included by the current editor. Server-enriched publication metadata, protected identifiers and fields without dedicated controls still require preservation. [ResourceSerializer](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/serialization/resource_serialization/resource.py) defines the current API fields; historical partials and `Attribute.description` include older names not equivalent to this schema.

## Transformations and validation

1. `addButtonClick` creates missing arrays and pushes `{}` or `''`, or creates a missing object/scalar. `removeButtonClick` splices the index after confirmation for a truthy item and deletes the entire property when its last item is removed. Thus missing, empty-list and empty-string states are intentionally conflated at some UI points.
2. `addObjectClick` sets the entire parent container to `{}` before adding a child. Adding `community.biolib` can discard other community keys. `removeObjectClick` deletes a child and removes an empty parent. This is a known data-preservation risk, not a target behavior to silently reproduce.
3. `validateEditResourceField` in [directives.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/directives.js) derives an error path from `ng-model`/indices. On editing, it clears the corresponding server error and sets control validity; if the edited value is `''`, it unsets that path on `software`. This also applies to basic required-field controls and can create sparse arrays for indexed scalar fields. It is not a general JSON sanitizer.
4. The directive reads errors from `registrationErrorPayload`, marks controls invalid, and gathers ancestor `general_errors` into form errors. Nested EDAM templates also display array-index errors directly. Paths are constructed at initialization using limited string replacement; removal/reindexing and deeper nested paths need targeted checks. `resetError`/`resetListError` provide additional clearing behavior for legacy controls.
5. The deep `software` watcher serializes the object with `angular.toJson`; the JSON-model watcher parses with `angular.fromJson` and replaces `software` on success. Parse failure retains the previous object and displays a message. The textarea debounces for 1000 ms, whereas Save waits only 100 ms; syntax errors do not disable Save. A syntactically valid non-resource JSON value has no explicit client schema gate here.
6. The download action generates a data-URI attachment from the current object (pretty or compact), named after resource name or `resource.json`. It performs no server write and is not an export of a separately preserved API snapshot.
7. `Covid` and `CommunityCollection` in [services.js](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/frontend/js/services.js) append/remove special collection strings; removal returns `undefined` when no values remain. They act on the same collection list as manual editing and must preserve unrelated tags.

No drag/drop or move-up/down editor operation was found. Array append/remove and raw JSON edits can change ordering, but server relationships do not establish an order guarantee in this inventory. Future nested-editor tests must distinguish meaningful order from unspecified serializer/DB order instead of sorting every list before comparison.

## EDAM selection

The editor fetches four whole ontology trees from `/api/o/EDAM_topic`, `/api/o/EDAM_operation`, `/api/o/EDAM_data`, `/api/o/EDAM_format`. `treecontrol` displays/filter-selects nodes; `ontologyOnSelect` creates an object if needed and assigns both `term = node.text` and `uri = node.data.uri`. The visible selected-term inputs are disabled text controls. Tree expansion/filter/selection metadata lives separately under `meta`.

The I don't know buttons in function input/output/operation/format controls set a root label such as `Operation`, `Data` or `Format` and reset widget selection, but do not consistently clear the previous URI. A previously selected term can therefore become a mismatched URI/label pair.

[EDAM serializers](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/serialization/resource_serialization/edam.py) call [OntologyValidator](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/validators.py) and return canonical URI/term values. The validator checks URI first, rejects mismatched labels and obsolete/unknown terms, and can resolve a label when URI is absent; synonym behavior is also present. Function operation is a required nonempty array; input/output data is required when those objects exist, and optional format arrays cannot be empty. Validate root-term fallback, obsolete terms, synonyms and mismatches against the actual loaded ontology.

## Server authority and data integrity

[ResourceDetail.put](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/view/resource.py) validates a complete new resource, hides the previous DB record, then saves a replacement while retaining biotoolsID, biotoolsCURIE, additionDate, owner and validated-ID flag. It copies existing edit permissions when no change is requested and preserves protected `biotools:` otherIDs for non-superusers. This is not PATCH: omitted unrelated metadata can be lost. Permission changes are restricted to owner/superuser; confidence and validated flags have additional server checks. A partial basic-editor UI must not submit only the fields it displays.

[ResourceSerializer](https://github.com/veitveit/biotoolsRegistry/blob/a1fc8b94067f33bc9047efc9c75ebe1579365a07/backend/elixir/serialization/resource_serialization/resource.py) enforces name/ID syntax, uniqueness, URL rules, required basic fields, nested validation and controlled vocabularies. For example name is 1-100 characters, description 10-1000, homepage 1-300; ID must start alphanumeric and not end in a dot. Server settings use `general_errors` for non-field errors. Preserve errors and entered data on all 400/401/403/404/network responses; current UI does not consistently distinguish them.

Update's validation endpoint omits some save-time permission/otherID preprocessing, and no explicit transaction enclosing replacement plus Elasticsearch write is visible in the handler. Concurrency/failure behavior is an unresolved backend risk. Inventory does not modify it.

## Required later regression evidence

Use a rich existing resource covering every serializer field: edit one basic field, save, reload and compare untouched data. Exercise missing/null/empty string/empty list separately; nested add/remove and JSON reordering; URI/term mismatches and obsolete terms; error paths after index changes; form/JSON synchronization and immediate save; unknown community keys; collection shortcuts; owner/group/public/superuser/anonymous rights; validate versus save; failure preservation, double-submit, stale updates and unsaved navigation. These are planned checks, not test results. The `add-resource-editor-data-contract` change must resolve these before UI migration relies on a replacement payload.
