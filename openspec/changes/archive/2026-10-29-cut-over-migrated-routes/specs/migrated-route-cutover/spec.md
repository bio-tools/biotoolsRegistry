## Purpose

Move canonical user-facing routes from the legacy AngularJS frontend to verified migrated implementations incrementally, without affecting unrelated routes or the public API and with a documented rollback path.

## ADDED Requirements

### Requirement: Cutover preserves develop proxy and crawler behavior
Each route cutover SHALL be verified through develop's Caddy and production Apache paths for browser and crawler requests. Supported API/schema/account routing, static assets, cache Vary semantics and applicable search noindex behavior SHALL be preserved. Rendertron dependencies SHALL be verified before their routing is retained or removed.

#### Scenario: Crawler requests a cut-over route
- **WHEN** a crawler requests a migrated canonical URL through either supported proxy
- **THEN** the intended owner returns the page with applicable indexing/cache headers without a prerender loop or missing-service failure

#### Scenario: Cutover is rolled back through a supported proxy
- **WHEN** the documented rollback is applied in either deployment configuration
- **THEN** the prior route owner is restored without changing API, schema, account or static routing

### Requirement: Route ownership is explicit and evidence-gated
The migration SHALL maintain an explicit ownership record for user-facing route families and SHALL cut over a route only after its migrated implementation and required acceptance tests are complete.

#### Scenario: Migrated route is not ready
- **WHEN** a route family lacks required parity, browser tests, permission tests or other readiness evidence
- **THEN** its canonical route remains owned by the legacy frontend

#### Scenario: Migrated route is ready
- **WHEN** the documented readiness criteria for a route family are satisfied
- **THEN** the route ownership record identifies the new owner, cutover mechanism and rollback procedure before canonical routing is changed

### Requirement: Cutover affects only the intended route family
Changing ownership of a migrated route SHALL preserve unrelated legacy user-facing routes and all supported public API routes.

#### Scenario: Tool-detail route is cut over
- **WHEN** the canonical public tool-detail route is switched to Django ownership
- **THEN** unrelated legacy search or editor routes continue to resolve through their existing owner until separately migrated

#### Scenario: Public API request after browser-route cutover
- **WHEN** an external client requests an existing supported API endpoint after a browser route is cut over
- **THEN** API routing remains unaffected by the browser-route ownership change

### Requirement: Migrated canonical routes support direct browser navigation
A cut-over route SHALL support direct links, refresh and applicable canonical or legacy URL redirects through the production-like reverse-proxy stack.

#### Scenario: Direct refresh of migrated route
- **WHEN** a user directly loads or refreshes a cut-over canonical URL
- **THEN** the migrated owner renders or serves the route successfully without prior SPA navigation state

#### Scenario: Legacy URL variant has a defined replacement
- **WHEN** a supported obsolete URL variant is requested after cutover
- **THEN** routing applies the documented redirect or compatibility behavior without creating a redirect loop

### Requirement: Each route cutover is reversible
Every route family moved to the migrated implementation SHALL have a documented, small-scope rollback procedure that can restore the previous owner without reverting unrelated migration work.

#### Scenario: New route owner has a production regression
- **WHEN** operators decide to roll back a cut-over route family
- **THEN** the documented routing or configuration change restores the previous route owner while leaving unrelated migrated routes unchanged

### Requirement: Authenticated route cutover is gated by security behavior
Authenticated editor or account route families SHALL NOT be cut over until authentication, authorization, CSRF, session-expiry and relevant mutation tests pass for the migrated implementation.

#### Scenario: Editor route lacks CSRF or permission evidence
- **WHEN** the migrated editor has not passed the required security-oriented acceptance coverage
- **THEN** its canonical route remains on the legacy owner

#### Scenario: Owner changes editing permissions
- **WHEN** an owner or administrator saves private, public or named-group editing permissions through the migrated editor
- **THEN** the authoritative validation, CSRF and revision checks apply and unrelated resource metadata is preserved

#### Scenario: An ordinary editor attempts to change permissions
- **WHEN** a group or public editor submits changed editing permissions
- **THEN** the server rejects the change without replacing or indexing the resource, regardless of client controls

### Requirement: Cutover is observable
The deployed routing arrangement SHALL provide sufficient route-level logging or metrics to detect unexpected 4xx/5xx patterns and material latency regressions on newly migrated routes.

#### Scenario: Newly migrated search route degrades
- **WHEN** the migrated search route produces elevated errors or latency after cutover
- **THEN** operators can identify the affected route family from available logs or metrics and use the documented rollback path if necessary

### Requirement: Ownership requests use current resource authorization
Migrated request forms SHALL reuse authoritative request validation and owner/admin authorization. Decisions SHALL target the visible resource even when a request references a historical version, and completed requests SHALL NOT be processed twice.

#### Scenario: An owner accepts a request after editing the resource
- **WHEN** the owner accepts an ownership request after the resource has been replaced by a saved edit
- **THEN** the current resource transfers to the requester, pending requests follow its current owner, and the historical resource is not changed

#### Scenario: An unauthorized user or stale owner submits a decision
- **WHEN** a user who is neither the current owner nor an administrator submits an accept or decline
- **THEN** the request and resource remain unchanged

### Requirement: Browser interoperability does not expose API credentials
The opt-in retained-browser session transport SHALL use same-origin sessions and CSRF checks, including unauthenticated credential submissions. Existing public API routes SHALL remain token-authenticated. Browser logout SHALL clear the shared browser session without revoking external API tokens.

#### Scenario: A user moves between migrated and retained pages
- **WHEN** a user signs in through either browser implementation with the session bridge enabled
- **THEN** both implementations recognize the same session without storing an API token in browser storage

#### Scenario: An operator rolls back the browser transport
- **WHEN** the session bridge is disabled and retained pages are reloaded
- **THEN** retained pages return to the existing token API, the session API mount is unavailable, and read-only route ownership is unchanged

### Requirement: Canonical editor and request ownership requires session interoperability
Canonical `/register`, `/<id>/edit` and `/requests` workflows SHALL use the migrated implementations only when both the editor cutover and session bridge are enabled. Their mutation endpoints SHALL retain the existing CSRF, authorization, revision and data-preservation checks. Login, signup, recovery, profile and ORCID route families SHALL remain on their existing handlers until separately verified.

#### Scenario: A signed-in user enters the editor from a retained page
- **WHEN** a user follows retained navigation to registration, editing or requests with both switches enabled
- **THEN** a document navigation reaches the migrated implementation with the same session and supports direct refresh

#### Scenario: An operator rolls back only the editor family
- **WHEN** the editor cutover is disabled on the backend and proxies
- **THEN** the legacy editor and request pages are restored without changing detail, search or session transport

#### Scenario: Session interoperability is disabled while the editor switch remains enabled
- **WHEN** the session bridge is disabled on the backend and proxies
- **THEN** canonical editor/request ownership also returns to the legacy implementation

#### Scenario: The migrated editor cannot load its JavaScript
- **WHEN** JavaScript is unavailable on a migrated editor page
- **THEN** its explicit legacy link includes `_legacy=1` and does not return to the same migrated editor
