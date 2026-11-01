## Persistence and visibility

Use a separate versioned structured-design model with owner, title, graph, revision and timestamps. Start with private drafts; enforce authorization on every read/write. Create/update/delete and sharing changes require authenticated POST/appropriate mutation methods, CSRF/session protections, server-side validation and current revision comparison. Duplicate submissions, expired sessions and concurrent edits must not overwrite a newer version or claim success; retain the local draft with an explicit recovery path.

Sharing is opt-in, read-only by default, revocable and clearly distinguishes private from shared. Use an unguessable share link with documented disclosure semantics, no unintended listing/indexing or secret leakage; access stops after revocation and shared users cannot mutate the owner's design. Owners can duplicate a shared design into a separately owned draft. Decide and document exact link lifetime, caching/referrer and failure behavior in implementation, subject to security review.

## Portable design format and evolution

Provide explicit, versioned JSON export/import describing graph structure, source tool IDs, function and IO references, EDAM URIs, explanatory labels/notes and compatibility evidence. It is not an executable workflow, a tool wrapper, a command script or an upload of analysis data. Validate untrusted imports, size, graph shape and schema version before applying; keep the existing draft unchanged on failure. Support safe export even when some references no longer resolve.

Record the resource revision, annotation fingerprint/snapshot, active schema and EDAM revisions needed to re-resolve references. On reload/import, distinguish unchanged, changed, ambiguous, deleted/hidden and unavailable references; show the original choices, do not silently bind by array position, require explicit user confirmation for a replacement, and preserve unresolved information. Retain unknown compatible extension fields when safe; incompatible versions get an actionable error and original export remains available. Permission and current visibility must be checked again at read and share time, with no private metadata leaked.

## Verification and non-goals

Test users and sharing isolation, revoke, guessing, stale writes, cross-tab edits, sessions, input validation, import/export round trips, changed schemas/ontology and deleted/hidden tools. Run migrations and rollback/data-preservation checks on both proxies. No automatic publication, executable export, installation, execution or analysis-data storage.
