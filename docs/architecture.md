# Architecture

Django owns the public pages, account and editor routes, registry API and
server-side validation. Templates provide complete pages and forms; htmx adds
partial updates, and Vue islands provide interactive search, EDAM selection,
resource editing and workflow planning. Direct URLs and essential forms have
server-rendered fallbacks when JavaScript is unavailable.

`backend/elixir/` contains models, serializers, query services and schema
metadata. `backend/elixirapp/` contains browser routes and page handlers;
`backend/templates/` and `backend/elixir/static/` contain templates and source
assets. `frontend-modern/src/` contains the Vue/TypeScript code. Vite builds a
manifest and hashed files into `backend/elixir/static/modern/`; Django
`collectstatic` publishes them. `registry-assets/` preserves public schema
references, images and other existing asset URLs.

## Data and security

MySQL stores registry records, accounts, domains and workflow drafts;
Elasticsearch supplies search and domain indexes. EDAM vocabulary records support
ontology lookups. Public API clients retain token authentication. Browser
sessions use server-side permissions and CSRF protection; editor and management
mutations recheck permissions. Protected failures preserve unsaved drafts.

The activated biotoolsSchema and generated resource descriptor determine field
labels, choices, validation and public projections. Compatible schema or
vocabulary updates propagate through the backend contract without a frontend
rebuild. Existing values are preserved when editing; incompatible updates require
an explicit compatibility decision. Specialized function diagrams and publication
views must not hide newly advertised schema fields.

Decorative field icons use descriptor kinds and a small optional section mapping;
unknown fields receive a generic icon. Icons do not control visibility, choices,
validation or saved values. The local SVG sprite also works without JavaScript.

Search state and supported filters are represented in URLs. Server results are
authoritative; local filtering is limited to the loaded candidates and is labeled
accordingly. Async responses must not replace newer requests. EDAM selectors store
stable concept URIs and support keyboard navigation.

Tool pages link to OpenEBench, TeSS and relevant ELIXIR or SciCrunch resources.
For valid publication identifiers, the browser loads Dimensions, BIP! and
Altmetric badges from those providers. Citations and their identifier links
remain usable if a provider is unavailable or has no matching data. The header
tool count comes from search and is cached in browser session storage for five
minutes; search remains usable when the count cannot be loaded.

## Workflow planning

The existing image-based workflow gallery remains available. The separate
[workflow planner](workflows.md) matches tool functions by input, output, format
and optional EDAM operation, then lets users connect and save planning drafts.
It does not generate executable workflows.

## Deployment

`compose.yml` starts the development stack with Caddy and Django runserver.
`compose.prod.yml` uses the root Dockerfile's Apache/Django image and a task
runner. The GitHub import bridge is optional and disabled by default. The two
stacks preserve the public API, admin, `/static/`, `/resources/`, `/img/`,
`/json/` and `/media/` routes. The image's deny-all robots policy and the
production network and proxy settings need an explicit deployment decision.
