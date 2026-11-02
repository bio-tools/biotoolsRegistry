# Browser tests

Playwright tests cover search, tool detail, accounts, the editor, management and
workflow planning. Tests that create or change data require an explicit opt-in
and disposable credentials. Never run write tests against production.

See [testing](../../docs/testing.md) for the isolated stack, seed commands and a
sample invocation. Each optional suite states its required environment flags in
its skip message. `BIOTOOLS_BASE_URL`, `BIOTOOLS_TEST_TOOL_ID` and
`BIOTOOLS_TEST_QUERY` select the target and fixture; authenticated tests also
need `BIOTOOLS_TEST_USERNAME` and `BIOTOOLS_TEST_PASSWORD`.

Use `BIOTOOLS_TEST_LOCAL_TLS=1` for a local self-signed certificate. Set
`BIOTOOLS_TEST_SECURE_COOKIES=1` only for an HTTPS rehearsal and
`BIOTOOLS_TEST_EDITOR_WRITES=1` only for a disposable data set. Reports and traces
are generated under ignored `test-results*` and `playwright-report` directories.
