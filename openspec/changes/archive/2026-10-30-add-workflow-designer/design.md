## User journey

Start with a data type and/or format using existing EDAM selectors. Search for candidate functions accepting that input or producing a desired output; allow an optional EDAM operation filter and show labels, identifiers, matched input/output and reasons. Add a selected function to a draft; select a specific output to find and connect the next function. User can add independent starting steps, branches, multiple inputs, explanatory notes, delete/reorder steps, and edit/remove connections. Include a simple linear starting path without restricting the data model to a chain.

Represent a design as a graph of uniquely identified step instances and explicit connections between selected IO annotations. Preserve separate instances of the same resource/function and selected data/format values. Keep function references tied to resource revisions and use safe re-resolution; nested function positions alone are not durable identifiers across edits. Preserve unresolved snapshots and require the user to review conflicts; do not silently retarget.

Use the matching service's per-dimension evidence and operation filter. Mark unknown, related or conflicting connections visibly and in text; allow a deliberate manual connection with a reason while never presenting it as verified runnable. Prevent invalid endpoints, unintended self-links and cycles; handle non-linear inputs without assuming all inputs are interchangeable. Clearly show missing required information where it can be inferred and otherwise say it is unknown.

The initial workspace is an in-memory draft. Warn on navigation with unsaved edits, preserve user input through transient errors and offer an explicit draft download/recovery path; persistence and sharing are a later change. Include accessible keyboard/list controls equivalent to pointer interactions, status/error announcements, mobile reflow, and an honest asset-unavailable state. Use the existing design patterns rather than adding a component framework.

## Existing workflows

Keep the current read-only gallery and source links independently reachable. New designs are structured graphs, not images and not automatically published to the existing `/api/w` interface. Document routes, links and rollback. No executable file, engine invocation, command inference or data upload is included.

## Verification

Exercise linear, branching, multi-IO and duplicate-tool designs, operation filters, matching explanations, uncertain/manual edges, cycles, missing annotations, stale selections, failed requests and draft recovery. Verify keyboard, touch, desktop/mobile and failed assets through both proxies.
