# Installing bio.tools

The browser interface uses Django templates, htmx and Vue. Django also serves
the REST API. Docker Compose runs MySQL, Elasticsearch, the Django backend and
Caddy for local development; the production image uses Apache and mod_wsgi.

## Local development

Install Docker with Compose and Node 22.12 or newer. From the repository root:

```sh
npm --prefix frontend-modern ci
npm --prefix frontend-modern run type-check
npm --prefix frontend-modern test
npm --prefix frontend-modern run build
docker compose up -d --build mysql elasticsearch backend
docker compose exec backend python manage.py migrate --noinput
docker compose exec -u 0 backend python manage.py collectstatic --noinput
docker compose up -d caddy
```

Open `https://localhost/`. Caddy uses a local certificate, so the browser will
ask you to trust it. The backend is also available on `http://localhost:8000/`
on loopback. The Vite build writes to `backend/elixir/static/modern/`; after a
frontend rebuild, run `collectstatic` again so Caddy serves the updated assets.
The command above uses root inside the container because collected files can be
owned by a different user; it writes to the checkout's `registry-assets/static/`.

Migrations create tables but do not populate a registry or EDAM vocabulary.
Use a maintained disposable fixture or a properly authorized database import,
then populate its matching search index. The historical `initial_db.sql` drops
tables and must only be loaded into a disposable empty database. Never purge an
existing database, index or Docker volume as a setup step. See the
[browser regression guide](tests/browser/README.md) for guarded test fixtures and
the [rehearsal runbook](docs/frontend-migration/develop-refresh.md#run-and-verify)
for historical preview setup; use the Compose configuration above for new work.

For frontend work, run `npm --prefix frontend-modern run dev` to rebuild on
changes and republish the output with `collectstatic`. Backend and template
sources are mounted into the Django development container. Keep production
credentials and private data out of local fixtures.

## Production image

The repository-root `Dockerfile` builds the migrated Apache image with
`docker build --target prod -t IMAGE .`; it includes modern assets and the
historical public schema resources. `compose.prod.yml` runs the backend,
taskrunner, MySQL and Elasticsearch. It requires `BIOTOOLS_SECRET_KEY`,
`BIOTOOLS_ALLOWED_HOSTS` as a JSON array, `BIOTOOLS_MYSQL_ROOT_PASSWORD`,
`BIOTOOLS_MYSQL_PASSWORD` and an explicit `BIOTOOLS_EMAIL_BACKEND`. Supply the
existing secrets through the deployment's secret mechanism, set
`BIOTOOLS_URL_FRONT` to the public origin ending in `/`, and configure email,
ORCID, CSRF origins and proxy trust for the actual deployment.

Read the [production readiness record](docs/frontend-migration/production-readiness.md)
before activation. It covers migrations, database and media backups, rollback,
the existing deny-all robots policy and the remaining provider/security checks.
The optional GitHub import bridge is configured separately; see the
[integration notes](docs/frontend-migration/upstream-dev-integration.md).

The [historical installation reference](docs/frontend-migration/legacy-installation-reference.md)
is retained for migration evidence; its Angular/Gulp commands and container
cleanup instructions do not describe the current deployment.
