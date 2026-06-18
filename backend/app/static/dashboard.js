const state = {
    allFixtures: [],
    visibleFixtures: [],
    standings: [],
    insights: null,
    playerStats: null,
    fixtureSummaries: {},
    fixtureSyncStatus: null,
    aiAvailable: false,
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
    standingsMessage: document.querySelector("#standings-message"),
    standingsContainer: document.querySelector("#standings-container"),
    insightsMessage: document.querySelector("#insights-message"),
    insightsContainer: document.querySelector("#insights-container"),
    playerStatsMessage: document.querySelector("#player-stats-message"),
    playerStatsContainer: document.querySelector("#player-stats-container"),
    generateAiSummary: document.querySelector("#generate-ai-summary"),
    aiSummaryMessage: document.querySelector("#ai-summary-message"),
    aiSummaryOutput: document.querySelector("#ai-summary-output"),
    aiHealthBadge: document.querySelector("#ai-health-badge"),
    aiHealthDetails: document.querySelector("#ai-health-details"),
    providerSyncMessage: document.querySelector("#provider-sync-message"),
    syncStatusBadge: document.querySelector("#sync-status-badge"),
    refreshSyncStatus: document.querySelector("#refresh-sync-status"),
    syncProvider: document.querySelector("#sync-provider"),
    syncLastRun: document.querySelector("#sync-last-run"),
    syncDuration: document.querySelector("#sync-duration"),
    syncTotalFixtures: document.querySelector("#sync-total-fixtures"),
    syncCreated: document.querySelector("#sync-created"),
    syncUpdated: document.querySelector("#sync-updated"),
    syncNewlyCompleted: document.querySelector("#sync-newly-completed"),
    syncLastSuccess: document.querySelector("#sync-last-success"),
    syncErrorMessage: document.querySelector("#sync-error-message"),
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

async function fetchFixtureSyncStatus() {
    const possibleEndpoints = [
        "/api/fixtures/sync/status",
        "/fixtures/sync/status",
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            return await response.json();
        } catch (error) {
            console.warn(`Unable to fetch sync status from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load fixture sync runtime status.");
}

async function fetchStandings(filters = {}) {
    const queryString = buildGroupOnlyQueryString(filters);

    const possibleEndpoints = [
        `/api/standings${queryString}`,
        `/standings${queryString}`,
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            const data = await response.json();
            return normalizeStandingsResponse(data);
        } catch (error) {
            console.warn(`Unable to fetch standings from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load standings from available API endpoints.");
}

async function fetchInsights(filters = {}) {
    const queryString = buildGroupOnlyQueryString(filters);

    const possibleEndpoints = [
        `/api/insights/groups${queryString}`,
        `/insights/groups${queryString}`,
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            const data = await response.json();
            return normalizeInsightsResponse(data);
        } catch (error) {
            console.warn(`Unable to fetch insights from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load insights from available API endpoints.");
}

async function fetchPlayerStats(filters = {}, sortBy = "goals", limit = 5) {
    const queryString = buildPlayerStatsQueryString(filters, sortBy, limit);

    const possibleEndpoints = [
        `/api/players/stats${queryString}`,
        `/players/stats${queryString}`,
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            const data = await response.json();
            return normalizePlayerStatsResponse(data);
        } catch (error) {
            console.warn(`Unable to fetch player stats from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load player stats from available API endpoints.");
}

async function fetchPlayerStatsSummary(filters = {}) {
    const [
        topScorers,
        topAssists,
        yellowCards,
        redCards,
    ] = await Promise.all([
        fetchPlayerStats(filters, "goals", 5),
        fetchPlayerStats(filters, "assists", 5),
        fetchPlayerStats(filters, "yellow_cards", 5),
        fetchPlayerStats(filters, "red_cards", 5),
    ]);

    return {
        topScorers,
        topAssists,
        yellowCards,
        redCards,
    };
}

async function refreshFixtureSyncStatus() {
    setSyncStatusLoading();

    try {
        const data = await fetchFixtureSyncStatus();

        state.fixtureSyncStatus = data;
        renderFixtureSyncStatus(data);
    } catch (error) {
        console.error(error);
        setSyncStatusError("Unable to load fixture sync runtime status.");
    }
}

async function checkAiHealth() {
    setAiHealthChecking();

    try {
        const response = await fetch("/ai/health");

        if (!response.ok) {
            throw new Error("AI health endpoint returned an error.");
        }

        const data = await response.json();

        state.aiAvailable = Boolean(data.available);

        if (state.aiAvailable) {
            setAiHealthAvailable(data);
        } else {
            setAiHealthUnavailable(data);
        }
    } catch (error) {
        console.error(error);
        state.aiAvailable = false;
        setAiHealthUnavailable({
            provider: "local_llama",
            configured_model: "unknown",
            error: "Unable to reach the AI health endpoint.",
        });
    }
}

function setAiHealthChecking() {
    elements.aiHealthBadge.className = "ai-health-badge checking";
    elements.aiHealthBadge.textContent = "Checking AI...";
    elements.aiHealthDetails.textContent = "Checking whether Local Llama is reachable.";
}

function setAiHealthAvailable(data) {
    const model = data.configured_model || "configured model";
    const provider = data.provider || "local_llama";

    elements.aiHealthBadge.className = "ai-health-badge available";
    elements.aiHealthBadge.textContent = "AI Online";
    elements.aiHealthDetails.textContent = `${provider} is available using ${model}.`;
}

function setAiHealthUnavailable(data) {
    const model = data.configured_model || "configured model";
    const error = data.error || "Local Llama is currently unavailable.";

    elements.aiHealthBadge.className = "ai-health-badge unavailable";
    elements.aiHealthBadge.textContent = "AI Offline";
    elements.aiHealthDetails.textContent = `${model} is not reachable. ${error}`;
}

function setSyncStatusLoading() {
    elements.providerSyncMessage.textContent = "Checking latest fixture sync status...";
    elements.syncStatusBadge.className = "sync-status-badge not-started";
    elements.syncStatusBadge.textContent = "Checking";
}

function setSyncStatusError(message) {
    elements.providerSyncMessage.textContent = message;
    elements.syncStatusBadge.className = "sync-status-badge error";
    elements.syncStatusBadge.textContent = "Error";
    elements.syncErrorMessage.className = "sync-error-message has-error";
    elements.syncErrorMessage.textContent = message;
}

function renderFixtureSyncStatus(data) {
    const status = data.status || "not_started";
    const source = data.source || "No source yet";
    const provider = data.provider || "No provider yet";
    const totalFixtures = formatNumber(data.total_fixtures);
    const created = formatNumber(data.created);
    const updated = formatNumber(data.updated);
    const newlyCompleted = formatNumber(data.newly_completed_count);

    elements.syncStatusBadge.className = `sync-status-badge ${getSyncStatusClass(status)}`;
    elements.syncStatusBadge.textContent = formatSyncStatus(status);
    elements.syncProvider.textContent = provider;
    elements.syncLastRun.textContent = formatDateTime(data.last_run_at);
    elements.syncDuration.textContent = formatDurationSeconds(data.duration_seconds);
    elements.syncTotalFixtures.textContent = totalFixtures;
    elements.syncCreated.textContent = created;
    elements.syncUpdated.textContent = updated;
    elements.syncNewlyCompleted.textContent = newlyCompleted;
    elements.syncLastSuccess.textContent = formatDateTime(data.last_success_at);

    if (status === "not_started") {
        elements.providerSyncMessage.textContent =
            "No fixture sync has been recorded yet. Run sample or provider sync to populate runtime data.";
    } else if (status === "success") {
        elements.providerSyncMessage.textContent =
            `Last ${source} sync succeeded using ${provider}: ${totalFixtures} fetched, ${created} created, ${updated} updated.`;
    } else {
        elements.providerSyncMessage.textContent =
            `Last ${source} sync failed using ${provider}. Check the error message below.`;
    }

    if (data.last_error) {
        elements.syncErrorMessage.className = "sync-error-message has-error";
        elements.syncErrorMessage.textContent = data.last_error;
    } else {
        elements.syncErrorMessage.className = "sync-error-message";
        elements.syncErrorMessage.textContent = "No sync errors recorded.";
    }
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

function buildGroupOnlyQueryString(filters) {
    const params = new URLSearchParams();

    if (filters.group) {
        params.set("group_name", filters.group);
    }

    const queryString = params.toString();

    return queryString ? `?${queryString}` : "";
}

function buildPlayerStatsQueryString(filters, sortBy, limit) {
    const params = new URLSearchParams();

    if (filters.group) {
        params.set("group_name", filters.group);
    }

    if (filters.team && filters.team.trim()) {
        params.set("team", filters.team.trim());
    }

    params.set("sort_by", sortBy);
    params.set("limit", limit);

    return `?${params.toString()}`;
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

function normalizeStandingsResponse(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data.standings)) {
        return data.standings;
    }

    if (Array.isArray(data.results)) {
        return data.results;
    }

    return [];
}

function normalizeInsightsResponse(data) {
    if (data && data.insights) {
        return data.insights;
    }

    if (data && data.summary) {
        return data;
    }

    return {
        summary: {
            teams_analyzed: 0,
            groups_analyzed: 0,
            has_data: false,
        },
        group_leaders: [],
        strongest_attacks: [],
        best_defences: [],
        unbeaten_teams: [],
        winless_teams: [],
    };
}

function normalizePlayerStatsResponse(data) {
    if (data && Array.isArray(data.stats)) {
        return data.stats;
    }

    if (Array.isArray(data)) {
        return data;
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
        const [fixtures, standings, insights, playerStats] = await Promise.all([
            fetchFixtures(state.filters),
            fetchStandings(state.filters),
            fetchInsights(state.filters),
            fetchPlayerStatsSummary(state.filters),
        ]);

        state.visibleFixtures = fixtures;
        state.standings = standings;
        state.insights = insights;
        state.playerStats = playerStats;

        updateSummary(state.allFixtures, state.visibleFixtures);
        renderInsights(state.insights);
        renderPlayerStats(state.playerStats);
        renderStandings(state.standings);
        renderFixtures(state.visibleFixtures);
    } catch (error) {
        console.error(error);
        elements.dashboardMessage.textContent = "Unable to apply filters.";
        elements.fixturesContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load filtered fixture data. Please check that the fixtures API is running.
            </div>
        `;
        elements.standingsMessage.textContent = "Unable to load standings.";
        elements.standingsContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load standings data. Please check that the standings API is running.
            </div>
        `;
        elements.insightsMessage.textContent = "Unable to load insights.";
        elements.insightsContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load group insight data. Please check that the insights API is running.
            </div>
        `;
        elements.playerStatsMessage.textContent = "Unable to load player statistics.";
        elements.playerStatsContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load player statistics. Please check that the player stats API is running.
            </div>
        `;
    }
}

function setLoadingState() {
    elements.dashboardMessage.textContent = "Loading fixtures...";
    elements.standingsMessage.textContent = "Loading standings...";
    elements.insightsMessage.textContent = "Loading insights...";
    elements.playerStatsMessage.textContent = "Loading player statistics...";
}

function renderInsights(insights) {
    elements.insightsContainer.innerHTML = "";

    if (!insights || !insights.summary || !insights.summary.has_data) {
        elements.insightsContainer.innerHTML = `
            <div class="empty-state">
                Insights will appear after completed fixtures are synced.
            </div>
        `;
        elements.insightsMessage.textContent = "No completed fixture data is available for insights yet.";
        return;
    }

    const selectedGroup = state.filters.group || "all groups";
    elements.insightsMessage.textContent =
        `Analyzing ${insights.summary.teams_analyzed} team${insights.summary.teams_analyzed === 1 ? "" : "s"} across ${insights.summary.groups_analyzed} group${insights.summary.groups_analyzed === 1 ? "" : "s"} for ${selectedGroup}.`;

    const cards = [
        {
            label: "Group Leaders",
            value: formatTeamList(insights.group_leaders),
            detail: "Top teams by points, goal difference, and goals scored.",
        },
        {
            label: "Strongest Attack",
            value: formatTopTeamMetric(insights.strongest_attacks, "goals_for", "GF"),
            detail: "Teams with the most goals scored.",
        },
        {
            label: "Best Defence",
            value: formatTopTeamMetric(insights.best_defences, "goals_against", "GA"),
            detail: "Teams with the fewest goals conceded.",
        },
        {
            label: "Unbeaten Teams",
            value: formatTeamList(insights.unbeaten_teams),
            detail: "Teams without a loss in completed fixtures.",
        },
        {
            label: "Winless Teams",
            value: formatTeamList(insights.winless_teams),
            detail: "Teams still looking for their first win.",
        },
    ];

    cards.forEach((item) => {
        const card = document.createElement("article");
        card.className = "insight-card";

        card.innerHTML = `
            <span class="insight-label">${escapeHtml(item.label)}</span>
            <strong>${escapeHtml(item.value)}</strong>
            <p>${escapeHtml(item.detail)}</p>
        `;

        elements.insightsContainer.appendChild(card);
    });
}

function renderPlayerStats(playerStats) {
    elements.playerStatsContainer.innerHTML = "";

    if (!hasPlayerStatsData(playerStats)) {
        elements.playerStatsContainer.innerHTML = `
            <div class="empty-state">
                Player statistics will appear after sample player stats are synced.
            </div>
        `;
        elements.playerStatsMessage.textContent = "No player statistics are available yet.";
        return;
    }

    const selectedGroup = state.filters.group || "all groups";
    const selectedTeam = state.filters.team ? ` matching "${state.filters.team}"` : "";

    elements.playerStatsMessage.textContent =
        `Showing player leaders for ${selectedGroup}${selectedTeam}.`;

    const cards = [
        {
            label: "Top Scorers",
            value: formatPlayerMetricList(playerStats.topScorers, "goals", "G"),
            detail: "Players ranked by goals, then assists.",
        },
        {
            label: "Top Assists",
            value: formatPlayerMetricList(playerStats.topAssists, "assists", "A"),
            detail: "Players creating the most goals.",
        },
        {
            label: "Yellow Cards",
            value: formatPlayerMetricList(playerStats.yellowCards, "yellow_cards", "YC"),
            detail: "Players with the most yellow cards.",
        },
        {
            label: "Red Cards",
            value: formatPlayerMetricList(playerStats.redCards, "red_cards", "RC"),
            detail: "Players with red card records.",
        },
    ];

    cards.forEach((item) => {
        const card = document.createElement("article");
        card.className = "player-stat-card";

        card.innerHTML = `
            <span class="player-stat-label">${escapeHtml(item.label)}</span>
            <strong>${escapeHtml(item.value)}</strong>
            <p>${escapeHtml(item.detail)}</p>
        `;

        elements.playerStatsContainer.appendChild(card);
    });
}

function renderStandings(standings) {
    elements.standingsContainer.innerHTML = "";

    if (standings.length === 0) {
        elements.standingsContainer.innerHTML = `
            <div class="empty-state">
                No completed fixtures are available for the selected group yet.
            </div>
        `;
        elements.standingsMessage.textContent = "Standings will appear after completed fixtures are synced.";
        return;
    }

    const selectedGroup = state.filters.group || "all groups";

    elements.standingsMessage.textContent =
        `Showing ${standings.length} team${standings.length === 1 ? "" : "s"} for ${selectedGroup}.`;

    const table = document.createElement("div");
    table.className = "standings-table-wrapper";

    table.innerHTML = `
        <table class="standings-table">
            <thead>
                <tr>
                    <th>Group</th>
                    <th>Team</th>
                    <th>P</th>
                    <th>W</th>
                    <th>D</th>
                    <th>L</th>
                    <th>GF</th>
                    <th>GA</th>
                    <th>GD</th>
                    <th>Pts</th>
                </tr>
            </thead>
            <tbody>
                ${standings.map((team) => `
                    <tr>
                        <td>${escapeHtml(team.group_name)}</td>
                        <td>
                            <strong>${escapeHtml(team.team)}</strong>
                            <span class="team-code">${escapeHtml(team.team_code || "")}</span>
                        </td>
                        <td>${formatNumber(team.played)}</td>
                        <td>${formatNumber(team.wins)}</td>
                        <td>${formatNumber(team.draws)}</td>
                        <td>${formatNumber(team.losses)}</td>
                        <td>${formatNumber(team.goals_for)}</td>
                        <td>${formatNumber(team.goals_against)}</td>
                        <td>${formatSignedNumber(team.goal_difference)}</td>
                        <td><strong>${formatNumber(team.points)}</strong></td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;

    elements.standingsContainer.appendChild(table);
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

        const fixtureId = fixture.id;
        const savedSummary = state.fixtureSummaries[fixtureId];

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

            <div class="fixture-ai-actions">
                <button
                    class="fixture-ai-button"
                    type="button"
                    data-fixture-summary-id="${fixtureId}"
                >
                    Generate Match Summary
                </button>
            </div>

            <div
                class="fixture-ai-summary ${savedSummary ? "success" : ""}"
                id="fixture-summary-${fixtureId}"
            >
                ${savedSummary ? escapeHtml(savedSummary) : "No match summary generated yet."}
            </div>
        `;

        elements.fixturesContainer.appendChild(card);
    });
}

async function generateAiSummary() {
    elements.generateAiSummary.disabled = true;
    elements.generateAiSummary.textContent = "Generating...";
    elements.aiSummaryMessage.textContent = "Generating a deterministic tournament summary...";
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
        await checkAiHealth();
    } catch (error) {
        console.error(error);
        elements.aiSummaryMessage.textContent = "Unable to generate AI summary.";
        elements.aiSummaryOutput.className = "ai-summary-output error";
        elements.aiSummaryOutput.textContent =
            "Please check that the API server is running and fixture data is available.";
        await checkAiHealth();
    } finally {
        elements.generateAiSummary.disabled = false;
        elements.generateAiSummary.textContent = "Generate AI Summary";
    }
}

async function generateSingleFixtureSummary(fixtureId, button) {
    const summaryElement = document.querySelector(`#fixture-summary-${fixtureId}`);

    if (!summaryElement) {
        return;
    }

    button.disabled = true;
    button.textContent = "Generating...";
    summaryElement.className = "fixture-ai-summary";
    summaryElement.textContent = "Generating match summary...";

    try {
        const response = await fetch(`/ai/fixtures/${fixtureId}/summary`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Unable to generate match summary.");
        }

        const data = await response.json();

        state.fixtureSummaries[fixtureId] = data.summary;
        summaryElement.className = "fixture-ai-summary success";
        summaryElement.textContent = data.summary;
        await checkAiHealth();
    } catch (error) {
        console.error(error);
        summaryElement.className = "fixture-ai-summary error";
        summaryElement.textContent =
            "Unable to generate this match summary. Check that the API server is running and fixture data is available.";
        await checkAiHealth();
    } finally {
        button.disabled = false;
        button.textContent = "Generate Match Summary";
    }
}

function hasPlayerStatsData(playerStats) {
    if (!playerStats) {
        return false;
    }

    return [
        playerStats.topScorers,
        playerStats.topAssists,
        playerStats.yellowCards,
        playerStats.redCards,
    ].some((items) => Array.isArray(items) && items.length > 0);
}

function formatPlayerMetricList(players, metricKey, metricLabel) {
    if (!players || players.length === 0) {
        return "No players yet";
    }

    return players
        .slice(0, 3)
        .map((player) => {
            const value = formatNumber(player[metricKey]);
            const teamCode = player.team_code || player.team || "Team";
            return `${player.player_name} (${teamCode}, ${value} ${metricLabel})`;
        })
        .join(", ");
}

function formatScore(score) {
    return score === null || score === undefined ? "-" : score;
}

function formatNumber(value) {
    return value === null || value === undefined ? 0 : value;
}

function formatSignedNumber(value) {
    const number = formatNumber(value);

    return number > 0 ? `+${number}` : number;
}

function formatTeamList(teams) {
    if (!teams || teams.length === 0) {
        return "No teams yet";
    }

    return teams
        .slice(0, 3)
        .map((team) => `${team.team} (${team.team_code || team.group_name})`)
        .join(", ");
}

function formatTopTeamMetric(teams, metricKey, metricLabel) {
    if (!teams || teams.length === 0) {
        return "No teams yet";
    }

    const team = teams[0];
    return `${team.team} (${formatNumber(team[metricKey])} ${metricLabel})`;
}

function formatStatus(status) {
    if (!status) {
        return "Unknown";
    }

    return status.replaceAll("_", " ");
}

function formatSyncStatus(status) {
    if (!status) {
        return "Unknown";
    }

    return status
        .replaceAll("_", " ")
        .replace(/\b\w/g, (letter) => letter.toUpperCase());
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

function getSyncStatusClass(status) {
    if (status === "success") {
        return "success";
    }

    if (status === "error") {
        return "error";
    }

    return "not-started";
}

function formatDateTime(value) {
    if (!value) {
        return "-";
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

function formatDurationSeconds(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    const duration = Number(value);

    if (Number.isNaN(duration)) {
        return "-";
    }

    if (duration < 1) {
        return `${Math.round(duration * 1000)} ms`;
    }

    return `${duration.toFixed(2)} s`;
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

    elements.generateAiSummary.addEventListener("click", generateAiSummary);
    elements.refreshSyncStatus.addEventListener("click", refreshFixtureSyncStatus);

    elements.fixturesContainer.addEventListener("click", (event) => {
        const button = event.target.closest("[data-fixture-summary-id]");

        if (!button) {
            return;
        }

        const fixtureId = button.dataset.fixtureSummaryId;
        generateSingleFixtureSummary(fixtureId, button);
    });
}

async function initializeDashboard() {
    bindEvents();
    setLoadingState();
    checkAiHealth();
    refreshFixtureSyncStatus();

    try {
        const [fixtures, standings, insights, playerStats] = await Promise.all([
            fetchFixtures(),
            fetchStandings(),
            fetchInsights(),
            fetchPlayerStatsSummary(),
        ]);

        state.allFixtures = fixtures;
        state.visibleFixtures = fixtures;
        state.standings = standings;
        state.insights = insights;
        state.playerStats = playerStats;

        populateFilters(state.allFixtures);
        updateSummary(state.allFixtures, state.visibleFixtures);
        renderInsights(state.insights);
        renderPlayerStats(state.playerStats);
        renderStandings(state.standings);
        renderFixtures(state.visibleFixtures);
    } catch (error) {
        console.error(error);
        elements.dashboardMessage.textContent = "Unable to load fixtures.";
        elements.fixturesContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load fixture data. Please check that the API server is running.
            </div>
        `;
        elements.standingsMessage.textContent = "Unable to load standings.";
        elements.standingsContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load standings data. Please check that the standings API is running.
            </div>
        `;
        elements.insightsMessage.textContent = "Unable to load insights.";
        elements.insightsContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load group insight data. Please check that the insights API is running.
            </div>
        `;
        elements.playerStatsMessage.textContent = "Unable to load player statistics.";
        elements.playerStatsContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load player statistics. Please check that the player stats API is running.
            </div>
        `;
    }
}

document.addEventListener("DOMContentLoaded", initializeDashboard);
