# bio.tools registry

[bio.tools](https://bio.tools) is the ELIXIR registry for discovering and
curating bioinformatics tools and data services. It provides a searchable
catalogue, an editor, a REST API and a workflow planner based on
[biotoolsSchema](https://github.com/bio-tools/biotoolsSchema) and EDAM.

## Getting started

Install Docker Compose and Node.js 22.12 or newer, then run:

```sh
cp .env.example .env
npm --prefix frontend-modern ci
npm --prefix frontend-modern run build
docker compose up -d --build mysql elasticsearch backend
docker compose exec backend python manage.py migrate --noinput
docker compose exec -u 0 backend python manage.py collectstatic --noinput
docker compose up -d caddy
```

Open **https://localhost/** and accept the local development certificate. The
new database is empty: use an authorized data import or disposable test
fixtures before expecting search results. See [installation](INSTALL.md) for
setup, the optional GitHub bridge and production configuration. Edit `.env`
for your installation and keep it private; use a separate file for production.

## Project layout

- `backend/`: Django models, API, page handlers, templates and static assets.
- `frontend-modern/`: Vue/TypeScript components and Vite build.
- `registry-assets/`: retained public schemas, images and static references.
- `tests/`: browser tests and isolated test/rehearsal configurations.
- `docs/`: architecture, workflow planning, testing and release guidance.
- `openspec/`: concise capability specifications and the remaining readiness work.

The root `Dockerfile` builds the production image, including the frontend and
Apache. `backend/Dockerfile` builds the Django development container. The two
main Compose files are `compose.yml` for development and `compose.prod.yml` for
production; test configurations are under `tests/rehearsal/`.

## Documentation

- [Architecture](docs/architecture.md)
- [Workflow planner](docs/workflows.md)
- [Testing](docs/testing.md)
- [Production readiness](docs/operations.md)
- [Contribution guide](CONTRIBUTING.md)

Production readiness remains open: local tests are not approval to deploy. See
[the readiness checklist](openspec/changes/verify-production-migration-readiness/tasks.md).

## License and citation

The source is available under the [project license](LICENSE); registry content is
available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Please cite Ison et al., [The bio.tools registry of software tools and data
resources for the life sciences](https://doi.org/10.1186/s13059-019-1772-6),
*Genome Biology* (2019).
