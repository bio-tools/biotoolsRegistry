# RSEc service links

Tool pages show links from the [RSEc Atlas](https://github.com/research-software-ecosystem/RSEc-Atlas) when a local index is available. The links are separate from the bio.tools record and its schema.

The `rsec-updater` service in both Compose files builds `backend/data/rsec/links.json` on startup and every 24 hours. The backend and updater share this file through `backend_data`. Set `BIOTOOLS_RSEC_INDEX_PATH` in `.env` only if the chosen path is shared by both containers. To refresh manually:

```sh
docker compose exec rsec-updater python manage.py update_rsec_links
```

The job downloads the Atlas summary, the [Galaxy CoDex tool list](https://github.com/galaxyproject/galaxy_codex/blob/main/communities/all/resources/tools.json), and the RSEc Bioconda and WorkflowHub RDF datasets. It writes a temporary file and replaces the index only after a complete successful import. A failed refresh leaves the previous index in place and the service retries after one hour. The file contains one current snapshot, including its update time; it is not a history of snapshots. Source metadata may be older than the import date.

The updater uses Docker's bridge network by default. If that network cannot resolve external hosts on a Linux deployment, set `BIOTOOLS_RSEC_NETWORK_MODE=host` in `.env` and recreate the updater. The updater does not need database access.

The index contains Atlas associations for Bioconda, BioContainers, Debian and Bioconductor, plus Galaxy CoDex entries and RSEc Bioconda and WorkflowHub associations with explicit bio.tools IDs. Galaxy instance links are shown only when the source lists one tool ID and reports it on that instance; suites with multiple IDs retain their source link without guessing an instance/tool pairing. An absent link means no link was found in the snapshot. It does not establish that the tool is unavailable.

For an offline test, supply `--summary`, `--galaxy`, `--bioconda` and `--workflows` with paths to the downloaded files. RSEc metadata is attributed to the [RSEc content repository](https://github.com/research-software-ecosystem/content), which is published under CC BY 4.0.

## GitHub export tests

The optional bio.tools-to-GitHub export uses a background worker and its own
`ECO_*` settings; the local preview leaves automatic export disabled. Failed
tasks are retried. Interrupted creations and deletions resume only if their
branches are still safe to use; conflicting changes or an advanced base require
manual review. For a temporary GitHub contents-API failure during deletion,
the exporter can use the Git-data API with a non-forced reference update. The
worker's configured retry limit still applies.

`tests/rehearsal/validate_ecosystem_record.py SCHEMA RECORD` checks one exported
record against the supplied official bio.tools JSON Schema, allowing the known
registry metadata extensions. It requires Python's `jsonschema` package. The
official schema currently repeats some enum values; the validator removes
duplicate enum entries before checking it. The RSEc GitHub Actions workflow
does not yet invoke this local test helper.

The RSEc auto-merge workflow deletes its head branch after a successful merge.
Rerunning that completed workflow can fail at checkout because the branch no
longer exists. Use a new pull request to test it again.
