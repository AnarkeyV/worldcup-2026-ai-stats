# Changelog

All notable changes to this project will be documented here.

This project follows semantic versioning.

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