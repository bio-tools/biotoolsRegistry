# Installation

## Development

Install Docker Compose and Node.js 22.12 or later. From the repository root:

```sh
cp .env.example .env
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

## Configuration

Edit the private `.env` file created above. Compose reads it from the project
directory and passes the settings declared in its service definitions to each
container. Use `docker compose --env-file /path/to/private.env ...` to select a
different file. `.env` and `.env.*` are ignored by Git; `.env.example` is the
tracked template. For a non-Docker Django process, export the settings in its
environment instead.

Database credentials in `.env` apply when MySQL first creates its data volume;
changing them later does not update existing MySQL accounts. Keep the existing
credentials unless you also update the database accounts through MySQL.

For GitHub metadata import, set `BIOTOOLS_GITHUB_BRIDGE_URL` to
`http://bridge:8000/github-to-biotools`, set `GITHUB_TOKEN` and
`HUGGINGFACE_TOKEN` as required by the provider, and start Compose with
`--profile github-import`. The bridge suggests changes; saving remains a
separate action.

For ecosystem exports, set `BIOTOOLS_GITHUB_ECOSYSTEM_ON=1`, the
`ECO_GITHUB_ORGANIZATION_NAME`, `ECO_GITHUB_REPO_NAME`, and
`ECO_PERSONAL_TOKEN` for a GitHub account with access to the target repository.
Set `ECO_MASTER_BRANCH` and `ECO_ROOT_GITHUB_FOLDER` if the repository differs
from the defaults. Start the `ecosystem` profile in development so its task
worker runs; production starts its worker normally. Use a separate test
repository and token for local work. Changing a record can create GitHub
branches and pull requests when this integration is enabled.

The local database preview at port 8005 uses
`/tmp/biotools-database-preview.yml`. To read this repository's `.env`, run its
Compose commands with `--project-directory /path/to/biotoolsRegistry`; enable
the same `github-import` or `ecosystem` profiles as needed. The preview remains
isolated from those services until its containers are recreated with the new
settings. Rebuild its `biotools-database-preview:local` image from the root
Dockerfile before starting the ecosystem worker so it includes the corrected
token handling. Its MySQL and Elasticsearch configuration is fixed to the local
database copy. Its app is on an internal network, so external sign-in and email
delivery require a suitable network configuration. The preview uses its own
local secret key and dummy email backend. For ORCID on port 8005, set a callback
URL registered for that origin in the selected environment file.

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
Use a separate production environment file and replace every local default,
especially the secret key, database passwords, debug mode, public URL, hosts,
email and ORCID settings. Do not commit it.

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
