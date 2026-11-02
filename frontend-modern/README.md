# Frontend

Vue/TypeScript islands and htmx enhance Django-rendered pages. Use Node.js 22.12
or later:

```sh
npm ci
npm run type-check
npm test
npm run build
npm run dev       # rebuild on changes
```

Vite writes a manifest and hashed assets to `backend/elixir/static/modern/`.
Run Django `collectstatic` after rebuilding for a proxy-served development site.
The root Dockerfile builds these assets automatically for production.

See [architecture](../docs/architecture.md), [installation](../INSTALL.md) and
[testing](../docs/testing.md).
