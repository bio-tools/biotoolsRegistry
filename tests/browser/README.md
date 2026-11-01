# Browser regression tests

These Playwright tests exercise the Django, htmx and Vue frontend. Use Node 22
or later and an isolated registry with disposable fixtures; some opt-in tests
create accounts, edit records or send ownership requests. Never point write
tests at production.

```sh
cd tests/browser
npm ci
npx playwright install chromium
BIOTOOLS_BASE_URL=https://localhost npm test
```

The default fixture is `signalp`; set `BIOTOOLS_TEST_TOOL_ID` and
`BIOTOOLS_TEST_QUERY` to a public, indexed tool in the test database. For a
local self-signed certificate set `BIOTOOLS_TEST_LOCAL_TLS=1`. The HTML-shell,
detail, search, editor, account, management and workflow suites each require
corresponding `BIOTOOLS_TEST_*` flags and, in several cases, seeded data. See
skip messages and fixture scripts in this directory. Authenticated tests also
need `BIOTOOLS_TEST_USERNAME` and `BIOTOOLS_TEST_PASSWORD`.

Tests that mutate records require `BIOTOOLS_TEST_EDITOR_WRITES=1` and disposable
credentials. The packaged-image smoke test uses `BIOTOOLS_TEST_NATIVE_PACKAGE=1`;
set `BIOTOOLS_TEST_SECURE_COOKIES=1` only for an HTTPS rehearsal with a disposable
account. The working application and production-like image setup are described in
[INSTALL.md](../../INSTALL.md). Historical migration and rollback evidence is in
[the archived harness notes](../../docs/frontend-migration/browser-harness-history.md).
