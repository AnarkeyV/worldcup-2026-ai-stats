# Roadmap

This roadmap tracks the planned development journey for the World Cup 2026 AI Stats Dashboard.

The project follows semantic versioning and is being built progressively so each milestone can be tested, documented, and demonstrated clearly.

---

## v0.1.0 - Project Foundation

Status: Completed

### Goals

- Create the initial repository structure
- Add Docker-first project setup
- Add backend health check
- Add dashboard placeholder
- Add CI foundation

### Completed

- Docker Compose setup
- FastAPI backend
- Streamlit dashboard
- PostgreSQL container
- Basic health endpoint
- Basic pytest test
- GitHub Actions CI
- Version file

---

## v0.1.1 - README and Documentation Polish

Status: Completed

### Goals

- Improve the public GitHub presentation
- Add a personal but professional README
- Make the project easier to understand for visitors

### Completed

- Capstone-style README
- Project story
- Architecture section
- Tech stack section
- Setup instructions
- Roadmap section
- Security notes
- Version history

---

## v0.2.0 - Football API Integration Foundation

Status: Completed

### Goals

- Add fixture data structure
- Store sample fixtures in PostgreSQL
- Expose fixture data through FastAPI
- Display fixtures on the dashboard
- Add proper endpoint tests

### Completed

- SQLAlchemy database layer
- Fixture model
- Sample fixture data
- Manual sample sync endpoint
- Fixture listing endpoint
- Fixture detail endpoint
- Streamlit fixture table
- SQLite test database
- Fixture endpoint test coverage

### Notes

This version uses sample data instead of a live football API provider.

This is intentional because the app should remain usable by public GitHub users without requiring an API key.

---

## v0.3.0 - Real Football API Provider Integration

Status: Planned

### Goals

- Select a football data API provider
- Connect the backend to a real World Cup data source
- Fetch real fixtures from the provider
- Normalize provider responses into the internal fixture model
- Keep sample data as a fallback/demo mode

### Planned Tasks

- Add football API client service
- Add provider configuration
- Add request timeout and error handling
- Add provider response validation
- Add real fixture sync endpoint
- Add tests with mocked provider responses
- Update dashboard to show provider/source status

---

## v0.4.0 - Match Completion Detector

Status: Planned

### Goals

- Detect when a match has finished
- Fetch final match status
- Prepare data for notification and reporting

### Planned Tasks

- Add background worker
- Add scheduled match checks
- Detect finished matches
- Store match completion state
- Avoid duplicate processing
- Add tests for match status transitions

---

## v0.5.0 - Telegram Notifications

Status: Planned

### Goals

- Send a Telegram message when a match finishes
- Include a dashboard link in each notification
- Track whether a notification has already been sent

### Planned Tasks

- Add Telegram bot integration
- Add notification service
- Add notification status tracking
- Add Telegram message template
- Add tests for notification logic

---

## v0.6.0 - Interactive Dashboard

Status: Planned

### Goals

- Improve the dashboard beyond a basic table
- Make the dashboard useful on mobile
- Add match detail views

### Planned Tasks

- Finished matches page
- Upcoming matches page
- Match detail page
- Team comparison section
- Match status filters
- Mobile-friendly layout improvements

---

## v0.7.0 - Local Llama Summary Agent

Status: Planned

### Goals

- Add controlled local LLM summarisation
- Generate readable match reports from structured data
- Keep the LLM isolated from system-level access

### Planned Tasks

- Add Ollama integration
- Add Llama 1B summary service
- Generate match summaries from structured JSON
- Add fallback when LLM is unavailable
- Store generated summaries in the database
- Add tests for summary prompt formatting

---

## v0.8.0 - Player-Level Statistics

Status: Planned

### Goals

- Add deeper player-level analysis
- Allow users to inspect players from either team
- Prepare richer data for AI summaries

### Planned Tasks

- Player statistics model
- Player statistics API routes
- Player table on dashboard
- Team/player filters
- Player detail view
- Top performers section

---

## v0.9.0 - Monitoring and Observability

Status: Planned

### Goals

- Add DevOps monitoring layer
- Track service health and failures
- Showcase observability skills

### Planned Tasks

- Prometheus metrics
- Grafana dashboard
- Service health panels
- API sync failure metrics
- Worker status metrics
- Documentation for monitoring setup

---

## v1.0.0 - Portfolio Release

Status: Planned

### Goals

- Produce a complete working portfolio release
- Demonstrate football data ingestion, dashboarding, notifications, local AI, and DevOps practices

### Planned Completion Criteria

- Real fixture sync works
- Finished match detection works
- Telegram notifications work
- Dashboard is mobile-friendly
- Local Llama summaries work
- Tests pass in CI
- Docker Compose deployment is documented
- Security notes are complete
- Screenshots are included
- Public demo deployment is documented