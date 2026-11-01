## Acceptance

Define representative annotated and sparsely annotated resources, multi-function and multi-IO tools, unknown formats, differing EDAM relationships, changed and removed resources, and linear/branching designs. Include examples where operation-filtered results share a resource but not a function. Compare ranked/paginated matches and uncertainty labels against a documented independent oracle. Measure realistic coverage of missing data/format/operation annotations and communicate the dataset and interpretation rather than claiming universal coverage.

Assess the complete journey from EDAM data/format and operation selection to graph editing, save, reload, share/revoke, export/import and recovery. Test narrow viewports and 200% zoom, keyboard focus and list/diagram equivalence, labels, contrast, status and errors; include screen-reader review where available and document limitations. Test unavailable ontology/index/assets, stale references, authorization and conflicting saves. Inspect actual images and ensure long values, multiple functions, branches and unknown compatibility remain readable.

Use agreed measurable budgets and representative dataset/concurrency before judging latency; verify complete pagination and describe indexing/revision lag. Fix blockers, rerun affected tests on both proxies, and record version/configuration, fixtures, screenshots, results and unresolved issues in `docs/frontend-migration/workflow-design-acceptance.md`. Obtain user-facing visual and workflow acceptance before declaring the change complete. Full production/security readiness and deployment remain separate gates.

No executable export, code generation, execution, silent conversion of existing images or automatic publication is in scope.
