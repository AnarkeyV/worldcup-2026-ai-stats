# Changelog

All notable changes to this project are documented in this file.

This project follows semantic versioning and milestone-based releases.

---

## [1.7.0] - Provider Sync Observability and Runtime Demo

### Added

- Added fixture sync runtime status tracking for the latest sample or provider sync run.
- Added `GET /fixtures/sync/status` for demo-friendly sync visibility.
- Added Prometheus metrics for fixture sync duration, fetched count, last run timestamp, and last successful sync timestamp.
- Added Provider Sync Runtime panel to the FastAPI static dashboard.
- Added provider sync observability panels to the provisioned Grafana dashboard.
- Added `docs/v1.7.0-provider-sync-observability-runtime-demo.md` as a dedicated runtime demo guide.

### Changed

- Updated the static dashboard footer and content to reflect v1.7.0.
- Updated the Grafana dashboard title to `World Cup 2026 AI Stats - Provider Sync Observability`.
- Improved monitoring configuration tests to validate Grafana dashboard JSON and provider sync panels.

### Tested

- Expanded full test baseline from `123 passed` to `138 passed`.
- Added tests for fixture sync runtime status, dashboard sync panel coverage, and Grafana provider sync observability.

### Notes

- Runtime sync status is intentionally stored in process memory for local demo clarity.
- Sync status resets when the backend process or container restarts.
- A future milestone can persist sync run history in PostgreSQL.

---

## [1.6.0] - Real Match Data Sync Improvement

### Added

- Added API-Football provider error wrapping for request failures, HTTP failures, invalid JSON, and invalid provider payloads.
- Added provider fixture validation so incomplete provider rows are skipped before database sync.
- Added team-code fallback logic for provider payloads that do not include country/team codes.
- Added route-level tests for successful mocked provider sync and provider failure handling.
- Added sync service validation for missing or blank fixture `external_id` values.

### Changed

- Normalized API-Football fixture statuses into app-friendly states such as `scheduled`, `live`, `complete`, `postponed`, `cancelled`, and `abandoned`.
- Hardened fixture completion detection so provider-native completed statuses such as `FT`, `AET`, and `PEN` are handled case-insensitively.
- Updated `/fixtures/sync/provider` to return `502` for provider-side sync failures.
- Updated release metadata from `1.5.0` to `1.6.0`.

### Tested

- Expanded full test baseline from `114 passed` to `123 passed`.
- Added focused tests for provider normalization, incomplete provider rows, invalid provider payloads, request failures, sync-service validation, and provider route behavior.

### Notes

- This release focuses on real match data-sync reliability rather than dashboard redesign.
- API-Football credentials are still optional and must be configured by the user before live provider sync can run.

---

## [1.5.0] - Portfolio Release Polish

### Added

- Added `docs/portfolio-release.md` as a recruiter/interviewer-friendly release summary.
- Added `docs/demo-walkthrough.md` for structured portfolio demo delivery.
- Added clearer v1.5.0 portfolio positioning across documentation.

### Changed

- Refreshed `README.md` as the main GitHub portfolio landing page.
- Updated `docs/architecture.md` to reflect the current v1.5.0 application architecture.
- Updated `docs/roadmap.md` to mark v1.5.0 as completed.
- Updated release metadata from `1.4.3` to `1.5.0`.
- Improved documentation around Docker Compose services, API routes, monitoring files, dashboards, Telegram, and local AI summaries.

### Tested

- Preserved full test baseline: `114 passed`.

### Notes

- This release does not add new backend features.
- This release is focused on portfolio quality, documentation accuracy, demo readiness, and release consistency.

---

## [1.4.3] - Documentation and Demo Evidence Cleanup

### Changed

- Updated README current version from `v1.4.0` to `v1.4.3`.
- Updated README release history and roadmap references.
- Cleaned documentation around ports, screenshots, and demo evidence.
- Updated screenshot evidence notes for v1.4.0, v1.4.1, and v1.4.2.
- Updated release metadata to `1.4.3`.

### Notes

- This release focused on documentation cleanup after the Grafana and Telegram hardening milestones.

---

## [1.4.2] - Telegram API Live Integration Hardening

### Added

- Added Telegram readiness/status endpoint.
- Added Telegram test notification endpoint.
- Added stronger Telegram notifier coverage.
- Added safer behavior for missing or placeholder Telegram credentials.

### Changed

- Hardened Telegram API live integration workflow.
- Improved documentation for Telegram setup and testing.
- Bumped application version metadata to `1.4.2`.

### Tested

- Validated Telegram notifier behavior.
- Validated notification routes.
- Preserved full automated test coverage.

### Security

- Telegram bot token and chat ID remain environment-driven.
- No secrets are committed to the repository.

---

## [1.4.1] - Grafana Dashboard Polish

### Added

- Added Grafana dashboard provisioning polish.
- Added Prometheus datasource provisioning support.
- Added default Grafana dashboard configuration.
- Added local monitoring demo evidence guidance.

### Changed

- Improved Grafana dashboard startup experience.
- Improved local observability documentation.
- Improved dashboard-related README sections.

### Tested

- Validated monitoring configuration.
- Confirmed Grafana and Prometheus local demo workflow.

---

## [1.4.0] - Monitoring and Observability Foundation

### Added

- Added Prometheus metrics endpoint.
- Added Prometheus Docker Compose service.
- Added Grafana Docker Compose service.
- Added monitoring configuration files.
- Added metrics service layer.
- Added monitoring-related tests.

### Tested

- Verified metrics endpoint behavior.
- Verified monitoring configuration tests.
- Confirmed Docker Compose monitoring services.

---

## [1.3.0] - Player-Level Statistics Foundation

### Added

- Added player statistics service.
- Added sample player statistics data.
- Added player statistics API routes.
- Added tests for player stats service and routes.

### Tested

- Verified player statistics sync.
- Verified player statistics listing, filtering, and sorting.

---

## [1.2.0] - Team Insights and Group Analytics

### Added

- Added group insights route.
- Added insights service.
- Added group-level analytics output.
- Added tests for insights routes and service.

---

## [1.1.2] - Version and Container Workflow Cleanup

### Changed

- Cleaned version metadata.
- Improved container workflow documentation.
- Added release consistency checks.

---

## [1.1.1] - README and Project Documentation Refresh

### Changed

- Refreshed README content.
- Improved project documentation and milestone descriptions.
- Updated version history.

---

## [1.1.0] - Group Standings Engine

### Added

- Added standings service.
- Added standings API route.
- Added group table calculation logic.
- Added tests for standings behavior.

---

## [1.0.0] - AI Summary Quality and Dashboard Polish

### Added

- Improved AI summary behavior.
- Improved dashboard presentation.
- Added additional route and service tests.

---

## [0.8.0] - Local Llama Summary Agent

### Added

- Added local Llama/Ollama client.
- Added AI health endpoint.
- Added fixture summary endpoints.
- Added tests for local AI workflow.

---

## [0.7.0] - API-Level Fixture Filters

### Added

- Added fixture filtering by group.
- Added fixture filtering by status.
- Added team search support.
- Added route tests for filters.

---

## [0.6.0] - Interactive Dashboard

### Added

- Added dashboard route.
- Added static dashboard assets.
- Added dashboard tests.
- Added local dashboard documentation.

---

## [0.5.0] - Telegram Notifications

### Added

- Added Telegram notifier service.
- Added Telegram notification workflow.
- Added environment-based Telegram configuration.
- Added notification tests.

---

## [0.4.0] - Match Completion Detection

### Added

- Added match completion detection behavior.
- Added completed fixture handling.
- Added tests for completion workflows.

---

## [0.3.0] - Real Football API Provider Layer

### Added

- Added provider abstraction.
- Added API-Football provider support.
- Added provider sync route.
- Added provider tests.

---

## [0.2.0] - Football API Integration Foundation

### Added

- Added fixture model foundation.
- Added fixture API routes.
- Added sample fixture sync.
- Added database-backed fixture persistence.
- Added tests for fixture workflows.

### Changed

- Updated backend version from `0.1.0` to `0.2.0`.

### Tested

- Verified fixture listing.
- Verified sample fixture sync.
- Verified health route.

### Notes

- This version introduced the foundation for future real provider integration.

---

## [0.1.1] - Documentation Polish

### Added

- Added documentation improvements.
- Added initial architecture notes.
- Added version history.

### Changed

- Improved README readability.
- Improved setup instructions.

---

## [0.1.0] - Project Foundation

### Added

- Added FastAPI backend foundation.
- Added project structure.
- Added Dockerfile.
- Added basic health check.
- Added pytest setup.
- Added initial CI workflow.
