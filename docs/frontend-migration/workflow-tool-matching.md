# Workflow tool matching

`GET /_workflow/matches/` finds public, recorded functions by the data type and/or format of one input or output. An optional EDAM operation must belong to that same function. This supplies evidence for a human designing a workflow; it does not establish that a tool can run or that two tools are compatible in practice.

Parameters: `direction=input|output`; `data` and/or `format` are active EDAM URIs; `operation` is an optional active operation URI. `mode=exact` is the default; `mode=related` also reports ancestor/descendant relationships. `include=matches` is the default; `unknown` includes missing or uninterpretable evidence and `all` also includes conflicts. `limit` defaults to 20 and is at most 50. Examples of related evidence say which of the requested or annotated terms is more specific and retain the input/output direction; they are not guarantees of substitutability. Obsolete terms are never silently mapped. Missing, term-only, unrecognized and obsolete annotations remain visible, with reasons when they affect the query.

Each candidate identifies its visible resource, function and particular input/output, with its data, formats, operations, evidence, keyed identifiers and a signed function reference. References and fingerprints are scoped to the current record and annotation: an edit or replacement can invalidate a selection. The designer preserves the snapshot and asks the user to review changed or missing selections; it does not rebind by position. Only fields permitted by the active public schema are returned. If the shape is incompatible, a record is ambiguous, related annotations exceed the safe bound, or metadata is unavailable, the endpoint returns a recoverable 503.

`POST /_workflow/compare/` compares a selected output's data and formats with an input's annotations using the current EDAM hierarchy. It reports exact, related, unknown or conflicting evidence separately for data and format, together with schema and vocabulary revisions. For a hierarchy relationship, “requested” is the output and “annotated” is the input. Even exact annotation equality does not guarantee that a connection is usable. Obsolete or unrecognized values remain uncertain; the comparison requires CSRF protection and does not mutate registry data.

The database is authoritative: Elasticsearch's flattened function fields cannot safely preserve function and IO correlation. Correlated database filters eliminate known conflicts before the application inspects candidates. For searches including uncertain annotations, bounded prefilters identify possible data and operation records using exact-byte URI hashes, so case-insensitive database collations do not discard unrecognized values. If a prefilter exceeds 5,000 IDs, that filter is skipped and the application continues with the full scan; formats and all returned evidence are checked against the actual IO/function records. Each request inspects at most 100 returned candidate IO records, or functions without an IO record when unknown results are requested; the database may need to examine many more rows to find those candidates. There can be an empty page with a `next` cursor. Repeat the original parameters with that cursor, which expires after 15 minutes and is bound to the query, schema and vocabulary revisions. A changed query or revision requires restarting. No total is claimed. `complete` means only that the current live scan reached its end; it is not a consistent snapshot. Records can change between pages, the source has no reliable global revision, and the client should restart for a fresh scan. Resources without a recorded function are outside the candidate set and cannot be inferred.

On 2026-10-31 the user explicitly accepted live results with the visible warning
and restart option for workflow planning. A database test exercises a hidden
record and a newly added record between cursor pages. This decision accepts the
documented live-scan behavior; it does not turn a scan into a snapshot.

## Local evidence, 2026-10-29

The fixture-heavy preview has 421 visible resources, 106 with functions, and 176 functions. Of those functions, 105 have no input and 70 have no output. There are 139 input and 143 output records; zero inputs and 37 outputs lack format annotations. This is not a representative registry sample and cannot establish production coverage or a performance budget.

## Public registry sample, 2026-10-30

The public `https://bio.tools/api/t?format=json&page=N&per_page=100` endpoint reported 34,513 records. Pages 1, 87, 173, 259 and 345 each returned 100 records, with 500 distinct identifiers. These are five contiguous blocks at evenly spaced positions in the API's ordering, not a random sample; the index can also change while pages are retrieved. They therefore show annotation patterns but do not establish statistically representative population estimates.

Of the 500 sampled records, 450 had at least one function and 25 had more than one. Their 508 functions included 406 without an input and 412 without an output; 14 had multiple inputs and 22 had multiple outputs. All 508 had an operation URI. Of 121 input records, 22 had no format URI; of 123 output records, 43 had no format URI. All sampled input/output records had a data URI. Absence of an annotation does not establish that a tool has no input, output or format.

The anonymized `backend/elixirapp/tests/data/WorkflowPublicSample.json` retains only function operation, input/output, data and format URIs; it excludes tool identifiers, names, notes, commands and other metadata. Its SHA-256 is `6638a610d1c301388eb12abce0d9d4d4fd13eae039e526b4a1cb27154ab299be`. `elixirapp.test_workflow_public_sample` loads it only into an isolated test database and compares paginated exact and unknown results in both directions with a separately calculated structured-data oracle, including the operation constraint and missing IO/format annotations. Both Python runtimes passed. Its vocabulary is a synthetic flat tree of the sampled URIs, so this check does not validate real ontology relationships or obsolete status. Across 25 local in-process requests in each runtime, individual page times were roughly 25–111 ms; this small sequential test is not a concurrency or production-scale benchmark.

## Synthetic scale rehearsal, 2026-10-30

The opt-in `BIOTOOLS_WORKFLOW_SCALE=1 python manage.py test elixirapp.tests.workflow_scale --noinput --keepdb` repeats the anonymized sample 70 times in the isolated test database: 35,000 synthetic resources, 35,560 functions and 17,080 IO records. For the sample's most frequent input data/format/operation combination, the independently calculated oracle expected 630 strict matches and 840 matches including uncertainty; both complete scans returned those counts on both Python runtimes. Strict matching took 13 pages, with median page times of 199 ms (development runtime) and 193 ms (Apache runtime); their slowest pages took 241 and 306 ms respectively. Four concurrent first-page requests took 373–441 ms and 475–533 ms respectively. The uncertainty-inclusive scan took 18 pages and 9.0 / 10.1 seconds in total, with median pages of 512 / 575 ms and slowest pages of 669 / 719 ms respectively. Before the bounded uncertainty prefilter, the same scan took 370 pages and 47.1 seconds on the development runtime; an attempted correlated hash prefilter was discarded after individual database queries exceeded the browser's ten-second timeout.

These figures are a local rehearsal, not a release budget: repeated records are not independent, the test vocabulary is synthetic and smaller than active EDAM, the test client avoids proxy/network overhead, and the fallback path can still scan many pages. Production-sized real-data measurements, agreed latency budgets and concurrent-edit consistency remain open.

Backend tests cover correlated functions and IO, both directions, hidden records, a visibility change during scanning, exact/related/unknown/obsolete/conflicting evidence, cursors and empty pages, changed vocabularies, unavailable metadata and private schema fields. The matching, EDAM and cutover suites passed on the backend runtime; the matching suite passed on the Apache runtime. Browser checks found the expected seeded function and exercised pagination through both Apache and Caddy, for browser and crawler user agents. One initial local request took about 1.6 seconds on a cold Apache process; a warm Caddy request took about 0.2 seconds. These isolated observations are not a load test.

The real-data and concurrent-query results below complete this local change.
Production-origin performance, deployed vocabulary and operational budgets remain
separate readiness checks.

## Full-corpus rehearsal, 2026-10-31

Before measuring the full public corpus, the local interactive-page budgets were:
95% of sequential matching pages within 2 seconds, every page within 5 seconds,
and four simultaneous first-page requests each within 5 seconds, with no failed
requests and exact agreement with the structured-data oracle. These are provisional
engineering budgets for the recorded test machine, not a production service-level
agreement. On 2026-10-31 the user accepted these local limits. Full-scan time and
page count are also reported. A sanitized live
page-by-page crawl can contain duplicates or omissions if the registry changes;
it is not a point-in-time database snapshot. The collector retains only EDAM
annotation URIs and counts, with no identifiers or personal metadata.

### Full public corpus results

Between 15:28:49 and 15:31:33 UTC on 2026-10-31, the collector read 346 public
API pages at a limited rate. It obtained 34,519 distinct visible records with no
duplicate identifiers; the advertised count was 34,519 at both ends. Concurrent
edits can still cause omissions, so this is a live crawl, not a snapshot. The
anonymized file's SHA-256 is
`9226ebb5a2c0def3a7e544d5b4263a815d1b35d078cbbcdd3d1e2ee9909be7ad`.
The generated corpus is ignored by Git and Docker; the opt-in collector is
`backend/elixirapp/tests/collect_workflow_corpus.py`.

Of the 34,519 resources, 31,489 had recorded functions and 1,315 had more than
one. The 33,748 functions included 28,978 without an input and 29,706 without
an output; 1,283 had multiple inputs and 975 had multiple outputs. All had an
operation URI. Of 7,001 input records, 2,277 lacked a format URI; of 5,705 output
records, 1,684 lacked one. Absence of an annotation does not establish that a
tool has no input, output or format.

An isolated MySQL test database loaded the anonymous records once, preserving
function/IO/format relationships. A separately constructed structured-data oracle
checked strict input and output matches, uncertainty-inclusive matching with an
operation filter, and a sparse input scan without an operation filter. The test
used the preview's EDAM 1.25 tree (949 current data, 612 format and 534 operation
terms, plus obsolete terms), not a synthetic flat vocabulary. Its snapshot hash
was `ac35ce0193af4cae38fc4ff392a9cd58a705589732a352d5d71c732bb2a9d284`;
it is local test data and is not claimed to match the live deployment's vocabulary.

On an i7-11800H local machine using MySQL 8.0.43, Python 3.13 and Python 3.10
both matched the oracle: 31 strict input results, 75 strict output results, 1,165
uncertain input results with operation filtering, and 29,298 sparse input results.
The sparse scan took 587 pages: 48.0/51.7 seconds total, p95 page times 97.8/203.2
ms and maximum page times 304.1/273.9 ms respectively. Four concurrent sparse
first-page requests took at most 459.4/272.9 ms. Operation-filtered unknown pages
had p95 times of 527.0/613.9 ms. All met the provisional local budgets. These
in-process test-client timings exclude proxy/network overhead and are not an
agreement about production performance or provider capacity.

On 2026-11-01, both runtimes passed the full corpus again after the strict-input
and operation-filtered scans were strengthened to compare each returned resource,
operation, data and format combination with the independent oracle. The broad
587-page scan took 77.9/78.4 seconds, with p95 pages of 174.3/282.3 ms and
maximum pages of 406.0/358.1 ms on Python 3.13/3.10 respectively. All scenarios
still met the accepted local limits.

On the cleaned production image, a further isolated run used the same 34,519
records and EDAM 1.25 snapshot with MySQL 8.0.43 and Python 3.10. It matched the
structured-data oracle in every scenario. The broad input scan returned 29,298
matches over 587 pages in 80.4 seconds, with p95 page time 289.6 ms and slowest
page 385.8 ms; four simultaneous first-page requests took at most 621.5 ms.
Operation-filtered uncertain results had p95 874.3 ms and maximum 904.4 ms.
These in-process measurements met the user's accepted local limits; they exclude
proxy/network overhead and do not establish a production capacity or SLA.
