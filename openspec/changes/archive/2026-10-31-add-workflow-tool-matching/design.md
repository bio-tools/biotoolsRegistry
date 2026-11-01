## Matching contract

A request identifies direction, an EDAM data type and/or format, an optional operation, relation mode and pagination. Validate scope and values against the active vocabulary. Return a resource identifier, a function reference, the specific input or output and its data/format annotations, operation annotations, revision information and per-dimension match evidence. Distinguish exact, ontology-related, unknown and incompatible dimensions; never call any result guaranteed runnable.

Use the index only to retrieve candidates when its mapping preserves or safely over-approximates relationships. Verify each returned result against the current structured resource: input data and format must be on the same IO item, and the operation must belong to the same function. A coarse index query must not silently exclude eligible results, combine functions, or turn a truncated candidate set into complete results. Define stable order, pagination, dataset/index revision and truthful completeness. Resolve the race between index candidates and changed, hidden or removed database versions; don't expose hidden records.

For matching a produced output to a required input, support exact URI equality first. For ontology relations, state direction: a more specific produced concept may be relevant to a more general accepted concept, while the reverse requires user review. EDAM hierarchy relationships are not proof of interchangeability or an automatic conversion. Treat data and format separately; lack of an annotation is unknown. Keep obsolete, unresolved, term-only and unrecognized values visible with provenance, never silently substitute concepts. Operation filters apply to the same function and distinguish no annotation from non-matching annotations.

Use the active schema descriptor and vocabulary revision rather than copied term or enum lists. If required relationship semantics cannot be interpreted under a future schema, return an actionable unavailable/incompatible state instead of guessing. Keep query scope, traversal, cost and result size bounded; test representative coverage before selecting an indexing strategy.

## Verification

Use fixtures with multiple functions, multiple inputs and outputs, alternative formats, absent/obsolete terms and cross-function false positives. Compare paginated results with a structured-data oracle, including sparse and large candidate sets and operation filters. Verify exact and directional related matches, changing index/database revisions, failures and privacy on both proxy paths. Record corpus coverage and latency to inform later acceptance.

## Non-goals

No runnable workflow, command synthesis, data transfer, execution or executable workflow export.
