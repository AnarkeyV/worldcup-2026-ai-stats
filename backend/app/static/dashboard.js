const state = {
    fixtures: [],
    filters: {
        team: "",
        group: "",
        status: "",
    },
};

const elements = {
    totalFixtures: document.querySelector("#total-fixtures"),
    completedFixtures: document.querySelector("#completed-fixtures"),
    scheduledFixtures: document.querySelector("#scheduled-fixtures"),
    visibleFixtures: document.querySelector("#visible-fixtures"),
    teamSearch: document.querySelector("#team-search"),
    groupFilter: document.querySelector("#group-filter"),
    statusFilter: document.querySelector("#status-filter"),
    resetFilters: document.querySelector("#reset-filters"),
    dashboardMessage: document.querySelector("#dashboard-message"),
    fixturesContainer: document.querySelector("#fixtures-container"),
};

async function fetchFixtures() {
    const possibleEndpoints = [
        "/api/fixtures",
        "/fixtures",
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            const data = await response.json();
            return normalizeFixturesResponse(data);
        } catch (error) {
            console.warn(`Unable to fetch from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load fixtures from available API endpoints.");
}

function normalizeFixturesResponse(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data.fixtures)) {
        return data.fixtures;
    }

    if (Array.isArray(data.results)) {
        return data.results;
    }

    return [];
}

function populateFilters(fixtures) {
    const groups = [...new Set(
        fixtures
            .map((fixture) => fixture.group_name)
            .filter(Boolean)
    )].sort();

    const statuses = [...new Set(
        fixtures
            .map((fixture) => fixture.status)
            .filter(Boolean)
    )].sort();

    groups.forEach((group) => {
        const option = document.createElement("option");
        option.value = group;
        option.textContent = group;
        elements.groupFilter.appendChild(option);
    });

    statuses.forEach((status) => {
        const option = document.createElement("option");
        option.value = status;
        option.textContent = formatStatus(status);
        elements.statusFilter.appendChild(option);
    });
}

function updateSummary(fixtures, visibleFixtures) {
    const completed = fixtures.filter((fixture) => fixture.status === "complete").length;
    const scheduled = fixtures.filter((fixture) => fixture.status === "scheduled").length;

    elements.totalFixtures.textContent = fixtures.length;
    elements.completedFixtures.textContent = completed;
    elements.scheduledFixtures.textContent = scheduled;
    elements.visibleFixtures.textContent = visibleFixtures.length;
}

function applyFilters() {
    const teamQuery = state.filters.team.toLowerCase().trim();

    const visibleFixtures = state.fixtures.filter((fixture) => {
        const homeTeam = fixture.home_team?.toLowerCase() || "";
        const awayTeam = fixture.away_team?.toLowerCase() || "";
        const homeCode = fixture.home_team_code?.toLowerCase() || "";
        const awayCode = fixture.away_team_code?.toLowerCase() || "";

        const matchesTeam =
            !teamQuery ||
            homeTeam.includes(teamQuery) ||
            awayTeam.includes(teamQuery) ||
            homeCode.includes(teamQuery) ||
            awayCode.includes(teamQuery);

        const matchesGroup =
            !state.filters.group ||
            fixture.group_name === state.filters.group;

        const matchesStatus =
            !state.filters.status ||
            fixture.status === state.filters.status;

        return matchesTeam && matchesGroup && matchesStatus;
    });

    updateSummary(state.fixtures, visibleFixtures);
    renderFixtures(visibleFixtures);
}

function renderFixtures(fixtures) {
    elements.fixturesContainer.innerHTML = "";

    if (fixtures.length === 0) {
        elements.fixturesContainer.innerHTML = `
            <div class="empty-state">
                No fixtures match the selected filters.
            </div>
        `;
        elements.dashboardMessage.textContent = "Try changing or resetting the filters.";
        return;
    }

    elements.dashboardMessage.textContent = `Showing ${fixtures.length} fixture${fixtures.length === 1 ? "" : "s"}.`;

    fixtures.forEach((fixture) => {
        const card = document.createElement("article");
        card.className = "fixture-card";

        card.innerHTML = `
            <div class="fixture-meta">
                <span>${escapeHtml(fixture.competition || "World Cup 2026")}</span>
                <span>${escapeHtml(fixture.group_name || fixture.stage || "Fixture")}</span>
            </div>

            <div class="fixture-teams">
                <div class="team-row">
                    <span>
                        ${escapeHtml(fixture.home_team)}
                        <span class="team-code">${escapeHtml(fixture.home_team_code || "")}</span>
                    </span>
                    <span class="score">${formatScore(fixture.home_score)}</span>
                </div>

                <div class="team-row">
                    <span>
                        ${escapeHtml(fixture.away_team)}
                        <span class="team-code">${escapeHtml(fixture.away_team_code || "")}</span>
                    </span>
                    <span class="score">${formatScore(fixture.away_score)}</span>
                </div>
            </div>

            <div class="fixture-footer">
                <span>${formatDateTime(fixture.kickoff_time)}</span>
                <span class="status-pill ${getStatusClass(fixture.status)}">
                    ${formatStatus(fixture.status)}
                </span>
            </div>
        `;

        elements.fixturesContainer.appendChild(card);
    });
}

function formatScore(score) {
    return score === null || score === undefined ? "-" : score;
}

function formatStatus(status) {
    if (!status) {
        return "Unknown";
    }

    return status.replaceAll("_", " ");
}

function getStatusClass(status) {
    if (status === "complete") {
        return "status-complete";
    }

    if (status === "scheduled") {
        return "status-scheduled";
    }

    if (status === "live") {
        return "status-live";
    }

    return "status-default";
}

function formatDateTime(value) {
    if (!value) {
        return "Kickoff TBC";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat("en-SG", {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(date);
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function bindEvents() {
    elements.teamSearch.addEventListener("input", (event) => {
        state.filters.team = event.target.value;
        applyFilters();
    });

    elements.groupFilter.addEventListener("change", (event) => {
        state.filters.group = event.target.value;
        applyFilters();
    });

    elements.statusFilter.addEventListener("change", (event) => {
        state.filters.status = event.target.value;
        applyFilters();
    });

    elements.resetFilters.addEventListener("click", () => {
        state.filters.team = "";
        state.filters.group = "";
        state.filters.status = "";

        elements.teamSearch.value = "";
        elements.groupFilter.value = "";
        elements.statusFilter.value = "";

        applyFilters();
    });
}

async function initializeDashboard() {
    try {
        bindEvents();

        state.fixtures = await fetchFixtures();

        populateFilters(state.fixtures);
        applyFilters();
    } catch (error) {
        console.error(error);
        elements.dashboardMessage.textContent = "Unable to load fixtures.";
        elements.fixturesContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load fixture data. Please check that the fixtures API is running.
            </div>
        `;
    }
}

initializeDashboard();