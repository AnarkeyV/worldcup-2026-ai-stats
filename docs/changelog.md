# Changelog

All notable changes to this project will be documented here.

This project follows semantic versioning.

---

## [1.4.3] - Documentation and Demo Evidence Cleanup

### Changed

- Updated README current version from `v1.4.0` to `v1.4.3`
- Updated README test badge to `114 passed`
- Updated service URL documentation for Grafana and Streamlit dashboard access
- Updated Telegram notification documentation with the readiness endpoint
- Updated observability documentation to reflect both Prometheus and Grafana
- Updated screenshot evidence notes for v1.4.0, v1.4.1, and v1.4.2
- Updated roadmap to reflect completed milestones and next planned work
- Updated release metadata to `1.4.3`

### Notes

This is a documentation and release cleanup milestone.

No functional application behavior was intentionally changed.

---

## [1.4.2] - Telegram API Live Integration Hardening

### Added

- Telegram readiness endpoint:
  - `GET /notifications/telegram/status`
- `TelegramNotificationError` for configured-but-failed Telegram API requests
- Empty Telegram message validation
- Telegram HTTP status error handling
- Telegram request/network error handling
- Telegram rejected-message handling
- Additional Telegram service tests
- Additional notification route tests

### Changed

- Improved Telegram test notification error handling
- Updated fixture sync notification handling to return failed status when Telegram API calls fail
- Bumped application version metadata to `1.4.2`

### Tested

- Full backend test suite passing: `114 passed`
- Docker Compose runtime verified locally
- Telegram readiness endpoint verified
- Real Telegram Bot API test message delivered successfully

### Security

- Real Telegram bot token and chat ID remain local-only in `.env`
- No Telegram secrets are committed
- Telegram readiness endpoint exposes only boolean readiness flags

---

## [1.4.1] - Grafana Dashboard Polish

### Added

- Grafana service in Docker Compose
- Grafana Prometheus datasource provisioning
- Grafana dashboard provisioning
- World Cup overview dashboard JSON
- Backend target status panel
- Scrape sample panel
- Scrape duration panel
- Python runtime metrics panels
- Backend memory panels
- Backend CPU panel
- Python garbage collection panels
- Backend metrics inventory panel

### Changed

- Updated local Streamlit dashboard host port to `18501`
- Updated observability stack to include both Prometheus and Grafana

### Tested

- Docker Compose stack verified locally
- Prometheus target verified
- Grafana dashboard verified
- Screenshot evidence captured locally

---

## [1.4.0] - Monitoring and Observability Foundation

### Added

- `prometheus-client` dependency
- `backend/app/services/metrics_service.py`
- `backend/app/routes/metrics.py`
- `GET /metrics` endpoint
- HTTP request count metrics
- HTTP request duration metrics
- Fixture sync run metrics
- Fixture sync created/updated/newly-completed metrics
- Player stats sync metrics
- Notification result metrics
- AI summary request metrics
- `/metrics` link to the root API response
- Prometheus service in Docker Compose
- `monitoring/prometheus.yml`
- Persistent `worldcup_prometheus_data` volume
- Metrics endpoint tests
- Monitoring configuration tests

### Tested

- Backend Docker image build
- Dashboard Docker image build
- Docker Compose configuration
- Full backend test suite passing: `105 passed`

---

## [1.3.0] - Player-Level Statistics Foundation

### Added

- Player statistics model
- Player statistics sample data
- Player statistics service
- Player statistics API routes
- Player statistics dashboard cards
- Player stats sync endpoint
- Player stat filtering and sorting
- Player statistics tests

### Tested

- Full backend test suite passing: `94 passed`

---

## [1.2.0] - Team Insights and Group Analytics

### Added

- Group insights service
- Group insights API endpoint
- Dashboard insight cards
- Insights-aware tournament summary logic
- Group analytics tests

---

## [1.1.2] - Version and Container Workflow Cleanup

### Changed

- Cleaned version metadata and container workflow documentation
- Improved local run instructions and release consistency

---

## [1.1.1] - README and Project Documentation Refresh

### Changed

- Refreshed README and supporting documentation
- Improved project explanations and milestone notes

---

## [1.1.0] - Group Standings Engine

### Added

- Group standings calculation engine
- Standings API endpoint
- Dashboard standings table
- Standings-aware AI summary logic
- Standings tests

---

## [1.0.0] - AI Summary Quality and Dashboard Polish

### Added

- Deterministic tournament summaries
- Improved dashboard AI summary display
- Safer fallback summary behavior

---

## [0.8.0] - Local Llama Summary Agent

### Added

- Local Llama/Ollama client
- AI health endpoint
- AI fixture summary endpoint
- Dashboard AI summary button
- Local AI route and client tests

---

## [0.7.0] - API-Level Fixture Filters

### Added

- Fixture filtering by group
- Fixture filtering by status
- Fixture search by team
- Dashboard query integration
- Expanded fixture and dashboard tests

---

## [0.6.0] - Interactive Dashboard

### Added

- FastAPI static dashboard
- Fixture cards
- Summary stats
- Static HTML/CSS/JS assets
- Dashboard route
- Dashboard tests

---

## [0.5.0] - Telegram Notifications

### Added

- Telegram settings
- Telegram notifier service
- Completed fixture Telegram message formatter
- Safe Telegram send function
- Completed fixture notification helper
- Safe Telegram test endpoint
- Telegram notification wiring into fixture sync responses
- Telegram notification tests

---

## [0.4.0] - Match Completion Detection

### Added

- Match completion detection during fixture sync
- Newly completed fixture response fields
- Completion detection tests

---

## [0.3.0] - Real Football API Provider Layer

### Added

- API-Football provider client
- Provider configuration
- Provider sync endpoint
- Provider response normalization
- Mocked provider tests

---

## [0.2.0] - Football API Integration Foundation

### Added

- SQLAlchemy database connection layer
- PostgreSQL-backed fixture model
- Fixture routes in FastAPI
- Sample World Cup fixture data
- Manual sample fixture sync endpoint
- Fixture listing endpoint
- Single fixture detail endpoint
- Streamlit dashboard fixture table
- Dashboard button to sync sample fixtures
- SQLite-based test database for local and CI tests
- Fixture endpoint test coverage

### Changed

- Updated backend version from `0.1.0` to `0.2.0`
- Updated dashboard content to reflect fixture data foundation
- Updated database configuration to support PostgreSQL in Docker and SQLite during tests
- Moved database table creation into FastAPI lifespan startup
- Improved Docker dashboard build reliability

### Tested

- `/health` endpoint
- `/fixtures` endpoint before sync
- `/fixtures/sync/sample` endpoint
- `/fixtures` endpoint after sync
- `/fixtures/{fixture_id}` endpoint
- Missing fixture 404 response
- Idempotent fixture sync behavior

### Notes

This version does not connect to a real football data API yet.

Instead, it introduces the database, API, dashboard, and test foundation required before adding a real provider. This keeps the project working for public GitHub users even without an API key.

---

## [0.1.1] - Documentation Polish

### Added

- Capstone-style README
- Personal project story
- Project goals
- Tech stack section
- Roadmap section
- Security notes
- Development setup notes

### Changed

- Improved public GitHub presentation
- Clarified current project status and future milestones

---

## [0.1.0] - Project Foundation

### Added

- Initial project structure
- FastAPI backend
- Backend health check endpoint
- Streamlit dashboard placeholder
- PostgreSQL service through Docker Compose
- Dockerfiles for backend and dashboard
- Environment variable template
- Basic backend test
- GitHub Actions CI workflow
- Version file
