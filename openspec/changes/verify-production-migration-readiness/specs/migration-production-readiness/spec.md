## Purpose

Preview cutover and deterministic tests are not production approval. Configured account providers, deployment assets, security, indexing, performance and rollback need explicit evidence on the cleaned release.

## ADDED Requirements

### Requirement: Release readiness is a separate gate
The change SHALL document successful release readiness only after functional parity, experience acceptance, configured checks and rollback preparation pass. The user authorized source removal before these checks were complete.

#### Scenario: Active functional dependency remains
- **WHEN** the release-candidate audit finds a route or failure path still requiring AngularJS
- **THEN** release approval is withheld and the blocker receives an explicit owner

#### Scenario: Only enumerated cleanup references remain
- **WHEN** all native journeys and replacement destinations are verified and only audited legacy build/proxy/service references remain
- **THEN** the record identifies the cleanup and does not claim final release approval until the remaining checks pass

### Requirement: Configured provider and security checks are real evidence
The change SHALL verify authorized configured ORCID and email journeys and production-like security boundaries, separately from deterministic fixtures.

#### Scenario: Provider configuration unavailable
- **WHEN** required credentials, callback configuration or test-mail delivery are unavailable
- **THEN** the relevant gate remains incomplete and the record does not substitute fixture success

#### Scenario: Public token client after browser migration
- **WHEN** an external client authenticates to the public API while native browser sessions are enabled
- **THEN** its token contract remains intact and browser cookies do not grant unauthorized API access

### Requirement: Indexing and performance are explicitly evaluated
The change SHALL verify browser/crawler routing and indexing policy and measure representative workloads against budgets recorded before measurement.

#### Scenario: Preview and production indexing policies differ
- **WHEN** the production-like configuration is prepared for release
- **THEN** robots, sitemap, canonical URLs and headers match the recorded production policy without copying preview deny-all behavior accidentally

#### Scenario: Performance evidence reported
- **WHEN** representative workload tests complete
- **THEN** the record includes dataset size, concurrency, hardware, cache state, metrics and pre-agreed pass/fail budgets

### Requirement: Final readiness uses the cleaned artifact
The change SHALL withhold final readiness until the actual legacy-free artifact passes clean startup and full acceptance without retired frontend services or asset volumes.

#### Scenario: Clean deployment after retirement
- **WHEN** the cleaned release is built and started in a disposable production-like environment
- **THEN** native routes, API/admin, static/media and browser journeys work through both proxies without AngularJS or Rendertron dependencies

#### Scenario: Rollback after deletion
- **WHEN** the cleaned release is rolled back in a rehearsal
- **THEN** the prior deployable artifact and compatible configuration are restored using the documented procedure rather than a nonexistent legacy flag fallback

### Requirement: Deployment approval is explicit
The change SHALL produce an evidence-backed operator handover and SHALL NOT treat test completion as authorization to change production.

#### Scenario: Final gate passes
- **WHEN** all required final-artifact checks succeed
- **THEN** the handover records artifact IDs, commands, risks and go/no-go while leaving actual production deployment subject to operator approval

#### Scenario: Required check fails or is skipped
- **WHEN** a required acceptance check is not satisfied
- **THEN** final readiness remains incomplete and the gap is visible in the handover
