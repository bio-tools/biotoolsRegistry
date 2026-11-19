# Searching and drafts

The Tools page offers grouped, schema-derived filters. EDAM selectors search
labels and synonyms from the active vocabulary. Within each EDAM category,
choose whether all or any selected terms must match. “Include narrower terms”
also matches descendants in the current EDAM hierarchy; different categories
are combined. These are registry-level filters and do not require the matches
to belong to the same function.

Select **Boolean search** to use uppercase `AND`, `OR`, and `NOT`, parentheses,
quoted phrases and search fields, for example
`function:alignment AND output:sequence` or `topic:"genomics" OR name:FastQC`.
`NOT` applies first, then `AND`, then `OR`; use parentheses to change grouping.
Fields use the same names as the public search API. These are record-level
matches and do not require annotations to occur in the same function. Ordinary
searches retain their existing behavior. API clients can add `qmode=boolean`.

The public API accepts `updatedAfter` as a timezone-aware ISO 8601 timestamp,
for example `/api/t?updatedAfter=2026-01-01T00%3A00%3A00Z`. It returns records
whose indexed `lastUpdate` is strictly later than that instant, including newly
registered records. Follow the returned pagination links; results use the live
index, so concurrent changes can affect pagination. This is not a deletion feed
or a guaranteed complete synchronization protocol.

The registration editor can save incomplete work as a **private draft**. Drafts
are stored separately from public resources, visible only to their owner, and
can be reopened or deleted. “Publish tool” validates and creates the public
record; saving a private draft never publishes it. Drafts of existing records
retain their original record revision, so publishing cannot silently overwrite
a newer edit. The JSON export remains available as an independent backup.

## Permanent tool identifiers

A published bio.tools ID is permanently reserved, case-insensitively, including
after its record is deleted. Edits keep the original ID. Deletion hides the
record and removes its search entry; its historical database rows remain.
Private drafts do not reserve an ID until publication.

The reservation table is independent of resource rows and must be included in
backups. When restoring an older backup, reconcile identifiers assigned since
that backup before accepting new registrations. The migration reserves IDs in
all resource rows present at migration time; IDs physically removed before that
point need to be recovered from historical records separately.
