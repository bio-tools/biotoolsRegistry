## 0. Develop baseline

- [x] 0.1 Revalidate this change on pinned upstream develop as part of `refresh-develop-migration-baseline`; preserve the completed items below as old-baseline evidence.
- [x] 0.2 Review this change against the [develop impact matrix](../../../../docs/frontend-migration/baseline.md#change-specific-review) and record revision-specific evidence and remaining limitations.

Develop evidence (2026-09-13): upstream `9faec5b3b660498fdef9736e65e331728b55f99c`,
preserved in `develop-migration/`. The [refresh record](../../../../docs/frontend-migration/develop-refresh.md)
covers the 41-state inventory, current authentication/editor/search deltas, both
asset builds, 24 Django tests on each runtime, 16 browser tests on each proxy,
57 API/permission tests, screenshots and exercised rollback. No browser skips or
retries. Real ORCID/email and legacy Rendertron remain later deployment gates.

## 1. Inspect routing and templates

- [x] 1.1 Identify Django project URL configuration, current template settings, static-file settings, authentication context processors and reverse-proxy route ownership.
- [x] 1.2 Confirm an isolated route prefix that does not conflict with the public API or legacy SPA.
- [x] 1.3 Revalidate the shell through develop's Caddy/runserver and production Apache/WSGI paths, including browser/bot routing, Vary headers, assets, account/API isolation and blue upstream branding; record deployment evidence separately from the temporary dispatcher preview.

## 2. Implement the shell

- [x] 2.1 Add or reuse a narrowly scoped Django app/module for browser page views.
- [x] 2.2 Add a base template with semantic page landmarks, navigation/footer placeholders, Django messages and CSRF-ready form support.
- [x] 2.3 Add an isolated test/landing page rendered by Django.
- [x] 2.4 Define the strategy/templates for 404 and 500 responses without changing unrelated production behavior.

## 3. Verify route isolation

- [x] 3.1 Add Django tests for URL resolution, status code, template selection and basic context.
- [x] 3.2 Add regression assertions that representative existing API URLs and legacy frontend URLs still resolve to their previous owners.
- [x] 3.3 Verify the page renders useful structure without browser JavaScript.

## 4. Document developer workflow

- [x] 4.1 Document how to start the existing development stack and reach the Django-rendered test page.
- [x] 4.2 Run the relevant backend tests and record any environment-limited checks.

## Completion evidence

- Isolated `/_migration/html/` WSGI mount and request URLconf; existing API URLconf and SPA fallback retained.
- Templates and separate static assets under `backend/templates/html/` and `backend/elixir/static/html/`.
- `python manage.py test elixirapp.test_html`: 13 passed with Python 3.8.20 / Django 3.1.2; no database required.
- `BIOTOOLS_TEST_HTML_SHELL=1 npm test -- shell.spec.js`: 2 passed with JavaScript disabled, desktop/mobile screenshots inspected.
- Static collection to a temporary root, strict OpenSpec validation and whitespace checks passed.
- Workflow, rollback and limits documented in `docs/frontend-migration/django-html-shell.md`. Browser execution used the real Django WSGI entry points behind a temporary local dispatcher; live Apache/Docker integration remains unverified because those services were unavailable.
