const state = {
    allFixtures: [],
    visibleFixtures: [],
    filters: {
        team: "",
        group: "",
        status: "",
    },
    debounceTimer: null,
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
    generateAiSummary: document.querySelector("#generate-ai-summary"),
    aiSummaryMessage: document.querySelector("#ai-summary-message"),
    aiSummaryOutput: document.querySelector("#ai-summary-output"),
};

async function fetchFixtures(filters = {}) {
    const queryString = buildFixtureQueryString(filters);

    const possibleEndpoints = [
        `/api/fixtures${queryString}`,
        `/fixtures${queryString}`,
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

function buildFixtureQueryString(filters) {
    const params = new URLSearchParams();

    if (filters.group) {
        params.set("group_name", filters.group);
    }

    if (filters.status) {
        params.set("status", filters.status);
    }

    if (filters.team && filters.team.trim()) {
        params.set("team", filters.team.trim());
    }

    const queryString = params.toString();

    return queryString ? `?${queryString}` : "";
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
    resetSelectOptions(elements.groupFilter, "All groups");
    resetSelectOptions(elements.statusFilter, "All statuses");

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

function resetSelectOptions(selectElement, defaultLabel) {
    selectElement.innerHTML = "";

    const option = document.createElement("option");
    option.value = "";
    option.textContent = defaultLabel;

    selectElement.appendChild(option);
}

function updateSummary(allFixtures, visibleFixtures) {
    const completed = allFixtures.filter((fixture) => fixture.status === "complete").length;
    const scheduled = allFixtures.filter((fixture) => fixture.status === "scheduled").length;

    elements.totalFixtures.textContent = allFixtures.length;
    elements.completedFixtures.textContent = completed;
    elements.scheduledFixtures.textContent = scheduled;
    elements.visibleFixtures.textContent = visibleFixtures.length;
}

async function applyFilters() {
    setLoadingState();

    try {
        state.visibleFixtures = await fetchFixtures(state.filters);

        updateSummary(state.allFixtures, state.visibleFixtures);
        renderFixtures(state.visibleFixtures);
    } catch (error) {
        console.error(error);
        elements.dashboardMessage.textContent = "Unable to apply filters.";
        elements.fixturesContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load filtered fixture data. Please check that the fixtures API is running.
            </div>
        `;
    }
}

function setLoadingState() {
    elements.dashboardMessage.textContent = "Loading fixtures...";
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

async function generateAiSummary() {
    elements.generateAiSummary.disabled = true;
    elements.generateAiSummary.textContent = "Generating...";
    elements.aiSummaryMessage.textContent = "Asking your local Llama model for a fixture summary...";
    elements.aiSummaryOutput.className = "ai-summary-output";
    elements.aiSummaryOutput.textContent = "Generating AI summary. This may take a few seconds.";

    try {
        const response = await fetch("/ai/fixtures/summary");

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Unable to generate AI summary.");
        }

        const data = await response.json();

        elements.aiSummaryMessage.textContent = `Generated by ${data.provider} using ${data.model}.`;
        elements.aiSummaryOutput.className = "ai-summary-output success";
        elements.aiSummaryOutput.textContent = data.summary;
    } catch (error) {
        console.error(error);
        elements.aiSummaryMessage.textContent = "Unable to generate AI summary.";
        elements.aiSummaryOutput.className = "ai-summary-output error";
        elements.aiSummaryOutput.textContent =
            "Please check that the SSH tunnel to your Windows laptop is active and Ollama is running.";
    } finally {
        elements.generateAiSummary.disabled = false;
        elements.generateAiSummary.textContent = "Generate AI Summary";
    }
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

function scheduleFilterApply() {
    window.clearTimeout(state.debounceTimer);

    state.debounceTimer = window.setTimeout(() => {
        applyFilters();
    }, 250);
}

function bindEvents() {
    elements.teamSearch.addEventListener("input", (event) => {
        state.filters.team = event.target.value;
        scheduleFilterApply();
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

    elements.generateAiSummary.addEventListener("click", () => {
        generateAiSummary();
    });
}

async function initializeDashboard() {
    try {
        bindEvents();

        state.allFixtures = await fetchFixtures();
        state.visibleFixtures = state.allFixtures;

        populateFilters(state.allFixtures);
        updateSummary(state.allFixtures, state.visibleFixtures);
        renderFixtures(state.visibleFixtures);
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
