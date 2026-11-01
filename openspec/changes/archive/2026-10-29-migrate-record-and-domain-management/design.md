## Scope

Cover record Remove and Disown, editable JSON and Validate, /domain-manager,
/subdomain, /edit-domain/:id, /edit-subdomain/:id, and /workflows with image
annotations. The permissions editor and request inbox already migrated and must
be reused. No browser workflow authoring interface was found by the audit;
existing API/staff workflow operations are compatibility boundaries.

## Decisions

- Use native forms for short domain/record commands, with session authentication,
  CSRF and explicit destructive-action confirmation. GET never mutates data.
- Reuse authoritative write services/serializers; characterize current owner,
  editor, staff and protected-domain rules before copying any legacy behavior.
  Recheck permissions against current records at mutation time, including races
  with ownership transfers and request conclusions.
- Preserve database/index consistency and recoverable failure behavior. Do not
  show success after a failed write or index operation; test affected shared API
  handlers when they need a narrowly scoped fix.
- Extend the current editor conversion/validation pipeline for raw JSON edits
  and validation-only requests. Parse into a temporary draft before replacement;
  invalid input must not overwrite the existing draft. Preserve schema fields,
  read-only metadata, stable annotation/error paths and stale-revision checks.
- A failed or disabled editor runtime must render an accessible native explanation,
  link to the record and available read/export actions, with retry when applicable.
  It must not link to Angular or claim a save occurred. Full no-JavaScript rich
  annotation editing is not required by this change.
- Render workflow images from retained media and expose annotation details/links
  by keyboard/touch as well as pointer. Preserve annotation coordinates when
  scaled. Search is text input, not arbitrary regular-expression execution.
- Update profile/detail/domain links and route ownership in the same change;
  temporary legacy aliases survive only until the retirement gate.

## Verification and Rollback

Fixtures cover owner/editor/unrelated/staff users; protected domains; hidden,
removed and transferred records; duplicate submissions; invalid JSON; validation
without persistence; database/index errors; request/ownership races and media.
Run real-index mutation tests where indexing is involved, modern editor tests,
and native/enhanced journeys through both proxies. Compare unaffected schema
metadata before/after writes. Rehearse rollback before deleting legacy services.

## Non-Goals

No new workflow editor, bulk destructive commands, permission model redesign or
unproven historical tool-version creation. Any supported behavior proposed for
retirement requires an explicit decision rather than being silently omitted.
