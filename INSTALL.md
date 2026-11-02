# Installation

## Development

Install Docker Compose and Node.js 22.12 or later. From the repository root:

```sh
npm --prefix frontend-modern ci
npm --prefix frontend-modern run build
docker compose up -d --build mysql elasticsearch backend
docker compose exec backend python manage.py migrate --noinput
docker compose exec -u 0 backend python manage.py collectstatic --noinput
docker compose up -d caddy
```

Visit `https://localhost/`; Caddy uses a local certificate. Django is also
available at `http://localhost:8000/` on loopback. After rebuilding the frontend,
run `collectstatic` again. `npm --prefix frontend-modern run dev` rebuilds on
changes. Migrations do not populate registry records or EDAM data; use an
authorized import or isolated test fixtures. Do not load `initial_db.sql` into
an existing database: it can drop tables.

## Production

The root Dockerfile builds a self-contained Apache/Django image and the Vite
assets. Build it with `docker build --target prod -t IMAGE .`;
`docker compose -f compose.prod.yml` defines the backend, task runner, MySQL and
Elasticsearch. Configure secrets outside the repository, including
`BIOTOOLS_SECRET_KEY`, `BIOTOOLS_ALLOWED_HOSTS` as a JSON array,
`BIOTOOLS_MYSQL_ROOT_PASSWORD`, `BIOTOOLS_MYSQL_PASSWORD` and
`BIOTOOLS_EMAIL_BACKEND`. Set `BIOTOOLS_URL_FRONT`, ORCID, email, CSRF origins,
TLS and proxy trust for the actual deployment. The image currently serves a
deny-all `robots.txt`; decide the real indexing policy before deployment.

The optional GitHub bridge is available in either main Compose file through
`--profile github-import`. Set `BIOTOOLS_GITHUB_BRIDGE_URL` for the backend and
provide bridge credentials through the deployment's secret mechanism. It is
disabled by default; manual editing remains available.

Read [production readiness](docs/operations.md) before deployment. Never remove
existing database, index or media volumes as part of installation.

## Rehearsals

Local migration/rollback rehearsals use `tests/rehearsal/compose.yml`; browser
acceptance uses the disposable `tests/rehearsal/browser.yml`. See
[testing](docs/testing.md) for isolation and commands.
