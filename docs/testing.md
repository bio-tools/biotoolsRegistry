# Testing

Run the modern frontend checks from the repository root:

```sh
npm --prefix frontend-modern ci
npm --prefix frontend-modern run type-check
npm --prefix frontend-modern test
npm --prefix frontend-modern run build
```

## Isolated backend and browser stack

`tests/rehearsal/browser.yml` uses temporary MySQL, Elasticsearch, EDAM and media
storage. Its data is disposable; never connect these fixtures to production or
to a database containing data you want to retain.

Start the disposable stack and load its EDAM seed:

```sh
docker build --target prod -t biotools-refresh/production:review .
docker compose -f tests/rehearsal/browser.yml up -d browser-app browser-bridge browser-caddy
docker compose -f tests/rehearsal/browser.yml exec -T browser-app cp -r /edam-seed/. /elixir/application/backend/data/
docker compose -f tests/rehearsal/browser.yml exec -T browser-app python manage.py migrate --noinput
```

For the full backend suite, grant the isolated user access to Django's test
database and run the tests:

```sh
docker compose -f tests/rehearsal/browser.yml exec -T browser-db \
  mysql -uroot -pisolated-root-only -e "GRANT ALL ON test_elixir.* TO 'elixir'@'%';"
docker compose -f tests/rehearsal/browser.yml exec -T browser-app \
  python manage.py test --noinput --keepdb
```

The backend suite mutates its temporary search index. Start a fresh disposable
stack before seeding the browser fixtures below.

To seed fictional browser fixtures, run the following once in a fresh stack:

```sh
docker compose -f tests/rehearsal/browser.yml exec -T \
  -e BIOTOOLS_ALLOW_TEST_SEED=biotools-refresh \
  -e BIOTOOLS_TEST_PASSWORD=Migration-test-only-2026 browser-app sh -c \
  'for f in seed.py seed_detail.py seed_search.py seed_search_parity.py seed_editor.py seed_management.py seed_bridge.py; do python manage.py shell < /fixtures/$f || exit; done'
docker compose -f tests/rehearsal/browser.yml exec -T \
  -e BIOTOOLS_ALLOW_TEST_SEED=biotools-refresh \
  -e BIOTOOLS_TEST_ENRICHED_EDITOR=1 browser-app sh -c \
  'python manage.py shell < /fixtures/seed_editor.py'
```

Install the browser harness and run the desired scenarios:

```sh
npm --prefix tests/browser ci
cd tests/browser
npx playwright install chromium
BIOTOOLS_BASE_URL=http://localhost:8010 \
BIOTOOLS_TEST_TOOL_ID=migration-fixture BIOTOOLS_TEST_QUERY=Migration \
BIOTOOLS_TEST_USERNAME=migration-test BIOTOOLS_TEST_PASSWORD=Migration-test-only-2026 \
BIOTOOLS_TEST_CUTOVER=1 npm test -- cutover.spec.js discovery.spec.js
```

Other suites are opt-in; see their skip messages and [browser test guide](../tests/browser/README.md).
Some create accounts or modify records and require `BIOTOOLS_TEST_EDITOR_WRITES=1`.
The isolated Apache endpoint is `http://localhost:8010/`; Caddy forwards through
`http://localhost:8011/`. Stop this disposable stack with
`docker compose -f tests/rehearsal/browser.yml down` when finished. Its tmpfs
data is lost; this command is for the test stack only.

For backend tests that regenerate EDAM and mutate Elasticsearch, the separate
`tests/rehearsal/compose.yml` has a `tests` profile with a private EDAM tmpfs
and separate search service. It uses the `biotools-refresh` rehearsal MySQL
service and Django's test database; use it only with disposable test data.
The `packaged`, `secure`, `native-dev` and `backup` profiles retain the other
local rehearsal configurations. Production and development are unaffected by
stopping these test services.

The same-build schema update test uses the `biotools-refresh` rehearsal stack
and creates its own test database and search index. It restarts the rehearsal
backend and Apache, so run it only on a disposable preview, never production.
Local verification results and remaining release limits are in [operations](operations.md).
