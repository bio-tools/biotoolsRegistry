# Installation

## Development

Install Docker Compose and Node.js 22.12 or later. From the repository root:
Existing MySQL 8.0 data must be backed up and upgraded or restored into a
separate MySQL 8.4 volume before starting the new database image; see the
production section below.

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

## Staging behind an HTTPS gateway

These steps apply to the default `compose.yml` when a campus gateway terminates
HTTPS and forwards requests to Caddy over HTTP. Replace `staging.example.org`
with the hostname users see in their browsers. Use an internal server name only
if users also open that name in their browsers.

Set `BIOTOOLS_DEBUG=0` in the staging `.env`. An existing `BIOTOOLS_DEBUG=1`
overrides the Compose default and exposes tracebacks and request details in the
browser. Apply the change with `docker compose up -d --no-deps backend`. Check
the effective setting and read exception details in the backend logs:

```sh
docker compose exec -T backend python manage.py shell -c 'from django.conf import settings; print(settings.DEBUG)'
docker compose logs --tail 100 backend
```

### Gateway and Caddy

The `caddy` service mounts
[`backend/runtime/Caddyfile.native-dev`](backend/runtime/Caddyfile.native-dev)
at `/etc/caddy/Caddyfile`. Its default `https://localhost` site is for local
development. For an HTTP upstream, use `http://staging.example.org` as the site
address and point the gateway at Caddy's port 80. If an HTTPS request returns
`308` with the same URL in `Location`, check whether the gateway is forwarding
to a Caddy listener that redirects HTTP back to HTTPS.

Have the gateway preserve the browser's `Host` and set `X-Forwarded-Proto` to
`https` on requests it forwards from HTTPS. Configure Caddy's
[`trusted_proxies`](https://caddyserver.com/docs/caddyfile/options#trusted-proxies)
with the gateway's source IP or CIDR as seen by Caddy. This lets Caddy preserve
the gateway's forwarded scheme so Django generates HTTPS links and callbacks.
Set `BIOTOOLS_URL_FRONT=https://staging.example.org/` in the staging `.env`.

### Missing styles or interactive features

With the default Compose file, `docker compose up --build` builds the Python
backend and starts the services without preparing frontend assets. If the
homepage loads but `/static/html/shell.css` returns `404`, build the assets and
run `collectstatic`. From the deployed checkout, you can run the build in a
temporary container without installing Node.js on the server:

```sh
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --env npm_config_cache=/tmp/npm-cache \
  --mount "type=bind,source=$PWD,target=/workspace" \
  --workdir /workspace/frontend-modern \
  node:22-bookworm-slim sh -c 'npm ci && npm run build'
docker compose up -d
docker compose exec -T -u 0 backend python manage.py collectstatic --noinput
```

`collectstatic` copies the files into `registry-assets/static`, which Caddy
serves directly. Run it again after rebuilding the frontend. If Compose says
the backend is stopped, check `docker compose ps -a` and
`docker compose logs --tail 100 backend`, then retry `collectstatic` once the
backend is running. When collection succeeds, verify that
`/static/html/shell.css` and `/static/modern/manifest.json` return `200`.

### Login returns 403

If `/login` loads but submitting the form returns `403`, check the backend logs
for `Origin checking failed`. Django compares the browser's origin by scheme,
hostname and port. For the default `compose.yml`, replace the
`BIOTOOLS_CSRF_TRUSTED_ORIGINS` entry under `services.backend.environment` with
this single line. Compose sets this value explicitly, so changing `.env` alone
has no effect.

```yaml
      - 'BIOTOOLS_CSRF_TRUSTED_ORIGINS=["https://localhost","https://staging.example.org"]'
```

Recreate the backend from the deployed checkout and verify its effective value.
Use the same Compose files, project name and environment file as at startup.

```sh
docker compose up -d --no-deps backend
docker compose exec -T backend printenv BIOTOOLS_CSRF_TRUSTED_ORIGINS
docker compose logs --since 5m backend
```

Reload `/login` before retrying. If ORCID still fails after the form submits,
check that the authorization request sends
`https://staging.example.org/orcid/callback/` as its `redirect_uri` and that the
same URL is registered in the ORCID sandbox application.

## Configuration

Edit the private `.env` file created above. Compose reads it from the project
directory and passes the settings declared in its service definitions to each
container. Use `docker compose --env-file /path/to/private.env ...` to select a
different file. `.env` and `.env.*` are ignored by Git; `.env.example` is the
tracked template. For a non-Docker Django process, export the settings in its
environment instead.

`BIOTOOLS_DEPLOYMENT` identifies the instance and controls the non-production
notice independently of Django's debug setting. It defaults to `dev`; set it to
`production` only for the production instance. Test and staging instances
should keep another value so their pages display the notice.

Database credentials in `.env` apply when MySQL first creates its data volume;
changing them later does not update existing MySQL accounts. Keep the existing
credentials unless you also update the database accounts through MySQL.

For GitHub metadata import, set `BIOTOOLS_GITHUB_BRIDGE_URL` to
`http://bridge:8000/github-to-biotools`, set `GITHUB_TOKEN` and
`HUGGINGFACE_TOKEN` as required by the provider, and start Compose with
`--profile github-import`. The bridge suggests changes; saving remains a
separate action.

Publication metadata suggestions use Pub2Tools at
`https://elixir.ut.ee/pub2tools/api` by default. Set `BIOTOOLS_PUB2TOOLS_URL` to
a compatible instance, or leave it empty to disable the option. The service
receives the publication identifier and any optional supporting webpage URL.
Pub2Tools requires a DOI, PMID or PMCID; a webpage alone is not sufficient.
Suggestions are reviewed in the editor and saved only when the record is
published or updated. The backend needs outbound access to the chosen service.

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
local secret key and dummy email backend by default. To capture test email
locally, see [testing](docs/testing.md#local-email-testing). For ORCID on port 8005, set a callback
URL registered for that origin in the selected environment file.

Workflow images are media files, not part of the SQL dump. Restore the matching
media backup alongside the database. The local database preview reads them from
`database_test/media/workflows/`, with the original filenames from the database.
Its media mount is read-only; supplying files there does not change the database.
Production uses the persistent `media_data` volume and must retain its existing
media when updating or migrating the service.

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

Django 6.1 requires Python 3.12 or later and MySQL 8.4 or later. Set
`BIOTOOLS_MYSQL_IMAGE` to a tested MySQL 8.4 image, for example `mysql:8.4.13`.
Before switching an existing 8.0 installation, back up and rehearse a supported
database upgrade or restore into a separate 8.4 volume. Do not point the new
image at the only copy of an existing data volume: upgrading its on-disk data
can prevent the old server from starting. Keep the previous image and backup for
rollback, and apply Django migrations to the upgraded copy before cutover.

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
