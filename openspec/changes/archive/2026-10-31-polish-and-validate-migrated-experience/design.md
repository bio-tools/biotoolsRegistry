## Scope

Review home/discovery, result entries, tool detail, function diagrams, all schema
editor sections, account/recovery, profile/requests, domains and workflows.
Use actual seeded sparse and richly annotated records, long labels/URLs,
multiple functions and validation errors. Preserve the blue develop branding
and existing logo; do not rebrand or replace the architecture.

## Decisions

- Refine current styles/components first. Improve density, hierarchy and scanning
  without hiding supported biotoolsSchema fields or relationships.
- Function presentation retains input -> operation -> output structure, multiple
  data/formats and readable notes/commands. On small screens it may stack while
  preserving semantic order and accessible labels.
- Target WCAG 2.2 AA for changed surfaces, with keyboard/manual review alongside
  automated checks. Record criteria and evidence; an automated pass alone is not
  a claim of complete accessibility conformance.
- Use stable desktop/mobile viewports (including 1440 and 390 CSS pixels),
  320-pixel reflow and 200% zoom. Check long text, focus visibility, target sizes,
  contrast, image rendering and absence of clipped or overlapping controls.
- Keep native fallback contracts from the functional changes. The rich editor's
  honest unavailable-runtime state is not a promise of full native editing.
- Run cross-page journeys, including session expiry and ownership/request changes.
  Preserve drafts and meaningful errors; hide neither permission failures nor
  outstanding functional gaps behind visual polish.

## Evidence and Completion

Create docs/frontend-migration/experience-acceptance.md with routes, fixtures,
viewports, screenshots, keyboard/manual checks, automated results and defects.
Fix blocking defects and rerun affected journeys. User-facing visual review is
recorded separately from automated assertions; do not self-certify user approval.
This change may prepare styling before all pages land, but final acceptance waits
for all four functional changes.

## Non-Goals

No new design system/library, broad backend refactor, unrelated feature expansion
or marketing redesign. Performance/deployment approval belongs to readiness.
