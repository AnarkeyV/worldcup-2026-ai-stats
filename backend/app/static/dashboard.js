const state = {
    allFixtures: [],
    visibleFixtures: [],
    standings: [],
    insights: null,
    aiInsights: null,
    providerLeaders: null,
    latestCompletedSummary: null,
    fixtureSummaries: {},
    fixtureSyncStatus: null,
    aiAvailable: false,
    fixtureStatusScope: "completed",
    fixtureScope: "all",
    fixtureBrowserFixtures: [],
    selectedFixture: null,
    selectedFixtureDetail: null,
    selectedFixtureCoverage: null,
    selectedFixtureId: null,
    activeMatchDetailTab: "overview",
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
    aiInsightsMessage: document.querySelector("#ai-insights-message"),
    aiInsightsSummary: document.querySelector("#ai-insights-summary"),
    groupRaceMessage: document.querySelector("#group-race-message"),
    groupRaceContainer: document.querySelector("#group-race-container"),
    aiInsightsContainer: document.querySelector("#ai-insights-container"),
    refreshAiInsights: document.querySelector("#refresh-ai-insights"),
    playerStatsMessage: document.querySelector("#player-stats-message"),
    playerStatsContainer: document.querySelector("#player-stats-container"),
    generateAiSummary: document.querySelector("#generate-ai-summary"),
    aiSummaryMessage: document.querySelector("#ai-summary-message"),
    aiSummaryOutput: document.querySelector("#ai-summary-output"),
    latestCompletedSummary: document.querySelector("#latest-completed-summary"),
    aiHealthBadge: document.querySelector("#ai-health-badge"),
    aiHealthDetails: document.querySelector("#ai-health-details"),
    providerSyncMessage: document.querySelector("#provider-sync-message"),
    syncStatusBadge: document.querySelector("#sync-status-badge"),
    syncFreshnessBadge: document.querySelector("#sync-freshness-badge"),
    refreshSyncStatus: document.querySelector("#refresh-sync-status"),
    syncProvider: document.querySelector("#sync-provider"),
    syncLastRun: document.querySelector("#sync-last-run"),
    syncDuration: document.querySelector("#sync-duration"),
    syncTotalFixtures: document.querySelector("#sync-total-fixtures"),
    syncCreated: document.querySelector("#sync-created"),
    syncUpdated: document.querySelector("#sync-updated"),
    syncNewlyCompleted: document.querySelector("#sync-newly-completed"),
    syncLastSuccess: document.querySelector("#sync-last-success"),
    syncDataFreshness: document.querySelector("#sync-data-freshness"),
    syncDataAge: document.querySelector("#sync-data-age"),
    syncSchedulerMode: document.querySelector("#sync-scheduler-mode"),
    syncAlertPolicy: document.querySelector("#sync-alert-policy"),
    syncErrorMessage: document.querySelector("#sync-error-message"),
    fixtureStatusTabs: document.querySelector("#fixture-status-tabs"),
    fixtureGroupTabs: document.querySelector("#fixture-group-tabs"),
    fixtureBrowserMessage: document.querySelector("#fixture-browser-message"),
    matchDetailPanel: document.querySelector("#match-detail-panel"),
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

async function fetchAiInsights(filters = {}) {
    const params = new URLSearchParams();

    if (filters.group) {
        params.set("group_name", filters.group);
    }

    if (filters.team) {
        params.set("team", filters.team);
    }

    params.set("limit", "5");

    const queryString = `?${params.toString()}`;

    const possibleEndpoints = [
        `/api/ai/insights${queryString}`,
        `/ai/insights${queryString}`,
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            return await response.json();
        } catch (error) {
            console.warn(`Unable to fetch AI insights from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load structured AI insights from available API endpoints.");
}

function buildProviderLeadersQueryString(filters = {}) {
    const params = new URLSearchParams();

    if (filters.group) {
        params.set("group_name", filters.group);
    }

    if (filters.team && filters.team.trim()) {
        params.set("team", filters.team.trim());
    }

    params.set("limit", "5");

    const queryString = params.toString();

    return queryString ? `?${queryString}` : "";
}

async function fetchProviderLeaders(filters = {}) {
    const queryString = buildProviderLeadersQueryString(filters);

    const possibleEndpoints = [
        `/api/players/leaders${queryString}`,
        `/players/leaders${queryString}`,
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            return await response.json();
        } catch (error) {
            console.warn(`Unable to fetch provider-backed player leaders from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load provider-backed player leaders.");
}

async function fetchLatestCompletedSummary() {
    const possibleEndpoints = [
        "/api/ai/latest-completed/summary",
        "/ai/latest-completed/summary",
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            return await response.json();
        } catch (error) {
            console.warn(`Unable to fetch the latest completed match summary from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load the latest completed match summary.");
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

async function refreshAiInsights() {
    setAiInsightsLoading();

    try {
        const data = await fetchAiInsights(state.filters);

        state.aiInsights = data;
        renderAiInsights(data);
    } catch (error) {
        console.error(error);
        setAiInsightsError("Unable to load structured AI insights.");
    }
}

async function refreshProviderLeaders(filters = state.filters) {
    setProviderLeadersLoading();

    try {
        const data = await fetchProviderLeaders(filters);

        state.providerLeaders = data;
        renderProviderLeaders(data);
    } catch (error) {
        console.error(error);
        setProviderLeadersError();
    }
}

async function refreshLatestCompletedSummary() {
    setLatestCompletedSummaryLoading();

    try {
        const data = await fetchLatestCompletedSummary();

        state.latestCompletedSummary = data;
        renderLatestCompletedSummary(data);
    } catch (error) {
        console.error(error);
        setLatestCompletedSummaryError();
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
    elements.syncFreshnessBadge.className = "sync-freshness-badge not-started";
    elements.syncFreshnessBadge.textContent = "Data: Checking";
}

function setSyncStatusError(message) {
    elements.providerSyncMessage.textContent = message;
    elements.syncStatusBadge.className = "sync-status-badge error";
    elements.syncStatusBadge.textContent = "Error";
    elements.syncFreshnessBadge.className = "sync-freshness-badge unavailable";
    elements.syncFreshnessBadge.textContent = "Data: Unavailable";
    elements.syncDataFreshness.textContent = "Unavailable";
    elements.syncDataAge.textContent = "The dashboard could not read persisted sync status.";
    elements.syncSchedulerMode.textContent = "Unknown";
    elements.syncAlertPolicy.textContent = "Telegram sync-alert policy could not be loaded.";
    elements.syncErrorMessage.className = "sync-error-message has-error";
    elements.syncErrorMessage.textContent = message;
}

function renderFixtureSyncStatus(data) {
    const status = data.status || "not_started";
    const source = data.source || "No source yet";
    const provider = data.provider || "No provider yet";
    const triggerType = data.trigger_type || "manual";
    const totalFixtures = formatNumber(data.total_fixtures);
    const created = formatNumber(data.created);
    const updated = formatNumber(data.updated);
    const newlyCompleted = formatNumber(data.newly_completed_count);
    const freshness = data.freshness || { state: "unavailable" };
    const freshnessState = freshness.state || "unavailable";
    const scheduler = data.scheduler || {};

    elements.syncStatusBadge.className = `sync-status-badge ${getSyncStatusClass(status)}`;
    elements.syncStatusBadge.textContent = formatSyncStatus(status);
    elements.syncFreshnessBadge.className = `sync-freshness-badge ${getSyncFreshnessClass(freshnessState)}`;
    elements.syncFreshnessBadge.textContent = `Data: ${formatSyncFreshness(freshnessState)}`;
    elements.syncProvider.textContent = provider;
    elements.syncLastRun.textContent = formatDateTime(data.last_run_at);
    elements.syncDuration.textContent = formatDurationSeconds(data.duration_seconds);
    elements.syncTotalFixtures.textContent = totalFixtures;
    elements.syncCreated.textContent = created;
    elements.syncUpdated.textContent = updated;
    elements.syncNewlyCompleted.textContent = newlyCompleted;
    elements.syncLastSuccess.textContent = formatDateTime(data.last_success_at);
    elements.syncDataFreshness.textContent = formatSyncFreshness(freshnessState);
    elements.syncDataAge.textContent = formatDataAgeSeconds(freshness.data_age_seconds);
    elements.syncSchedulerMode.textContent = formatSchedulerMode(scheduler);
    elements.syncAlertPolicy.textContent = data.completed_match_alerts_enabled
        ? "Completed-match Telegram alerts are explicitly enabled."
        : "Completed-match Telegram alerts are disabled by configuration.";

    if (status === "not_started") {
        elements.providerSyncMessage.textContent =
            "No fixture sync has been recorded yet. Automated provider sync is disabled unless explicitly enabled in configuration.";
    } else if (status === "success") {
        elements.providerSyncMessage.textContent =
            `Last ${triggerType} ${source} sync succeeded using ${provider}: ${totalFixtures} fetched, ${created} created, ${updated} updated. Stored data is ${formatSyncFreshness(freshnessState).toLowerCase()}.`;
    } else {
        elements.providerSyncMessage.textContent =
            `Last ${triggerType} ${source} sync failed using ${provider}. The dashboard continues to show the last stored data state; check the safe error message below.`;
    }

    if (data.last_error) {
        elements.syncErrorMessage.className = "sync-error-message has-error";
        elements.syncErrorMessage.textContent = data.last_error;
    } else {
        elements.syncErrorMessage.className = "sync-error-message";
        elements.syncErrorMessage.textContent = "No sync errors recorded in the latest persisted run.";
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

function populateFilters(fixtures) {
    resetSelectOptions(elements.groupFilter, "All groups");
    resetSelectOptions(elements.statusFilter, "All statuses");

    const groups = getFixtureGroups(fixtures);
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

    renderFixtureGroupTabs(fixtures);
}

function resetSelectOptions(selectElement, defaultLabel) {
    selectElement.innerHTML = "";

    const option = document.createElement("option");
    option.value = "";
    option.textContent = defaultLabel;

    selectElement.appendChild(option);
}

function getFixtureGroups(fixtures) {
    return [...new Set(
        fixtures
            .map((fixture) => fixture.group_name)
            .filter(Boolean)
    )].sort((left, right) => left.localeCompare(right, undefined, { numeric: true }));
}

const COMPLETED_FIXTURE_STATUSES = new Set([
    "complete",
    "completed",
    "finished",
    "final",
    "ft",
    "full-time",
    "full time",
    "full_time",
    "match finished",
]);

const LIVE_FIXTURE_STATUSES = new Set([
    "live",
    "in_play",
    "in play",
    "halftime",
    "half-time",
    "ht",
    "1h",
    "2h",
]);

function normalizeFixtureStatus(fixture) {
    return String(fixture?.status || "")
        .trim()
        .toLowerCase()
        .replaceAll("_", " ");
}

function getFixtureStatusCategory(fixture) {
    const status = normalizeFixtureStatus(fixture);

    if (COMPLETED_FIXTURE_STATUSES.has(status)) {
        return "completed";
    }

    if (LIVE_FIXTURE_STATUSES.has(status) || status.includes("live") || status.includes("in play")) {
        return "live";
    }

    return "upcoming";
}

function getFixtureStatusCounts(fixtures) {
    return fixtures.reduce((counts, fixture) => {
        counts[getFixtureStatusCategory(fixture)] += 1;
        return counts;
    }, {
        completed: 0,
        live: 0,
        upcoming: 0,
    });
}

function getFixtureScopeFromGroup(groupName) {
    return groupName ? `group:${groupName}` : "all";
}

function getGroupNameFromScope(scope) {
    return scope && scope.startsWith("group:")
        ? scope.slice("group:".length)
        : "";
}

function isKnockoutFixture(fixture) {
    if (fixture.group_name) {
        return false;
    }

    const stage = String(fixture.stage || "").toLowerCase();

    return Boolean(stage) && !stage.includes("group");
}

function getFixturesForStatus(fixtures, statusScope = state.fixtureStatusScope) {
    return fixtures.filter((fixture) => getFixtureStatusCategory(fixture) === statusScope);
}

function filterFixturesForScope(fixtures) {
    const statusFixtures = getFixturesForStatus(fixtures);

    if (state.fixtureScope === "knockout") {
        return statusFixtures.filter(isKnockoutFixture);
    }

    const groupName = getGroupNameFromScope(state.fixtureScope);

    if (groupName) {
        return statusFixtures.filter((fixture) => fixture.group_name === groupName);
    }

    return statusFixtures;
}

function getFixtureDisplayGroup(fixture) {
    return fixture.group_name || fixture.stage || "Other matches";
}

function getAvailableFixtureStatusScopes(fixtures) {
    const counts = getFixtureStatusCounts(fixtures);

    return ["completed", "live", "upcoming"].filter((scope) => counts[scope] > 0);
}

function ensureFixtureBrowserSelection(fixtures) {
    const availableStatuses = getAvailableFixtureStatusScopes(fixtures);

    if (!availableStatuses.length) {
        state.fixtureStatusScope = "completed";
        state.fixtureScope = "all";
        return;
    }

    if (!availableStatuses.includes(state.fixtureStatusScope)) {
        state.fixtureStatusScope = availableStatuses.includes("completed")
            ? "completed"
            : availableStatuses[0];
        state.fixtureScope = "all";
    }

    const statusFixtures = getFixturesForStatus(fixtures);
    const selectedGroup = getGroupNameFromScope(state.fixtureScope);
    const availableGroups = getFixtureGroups(statusFixtures);
    const hasSelectedGroup = selectedGroup && availableGroups.includes(selectedGroup);
    const hasKnockoutFixtures = statusFixtures.some(isKnockoutFixture);

    if (state.filters.group && availableGroups.includes(state.filters.group)) {
        state.fixtureScope = getFixtureScopeFromGroup(state.filters.group);
        return;
    }

    if (hasSelectedGroup || (state.fixtureScope === "knockout" && hasKnockoutFixtures)) {
        return;
    }

    if (availableGroups.length > 0) {
        state.fixtureScope = getFixtureScopeFromGroup(availableGroups[0]);
    } else if (hasKnockoutFixtures) {
        state.fixtureScope = "knockout";
    } else {
        state.fixtureScope = "all";
    }
}

function renderFixtureStatusTabs(fixtures) {
    if (!elements.fixtureStatusTabs) {
        return;
    }

    const counts = getFixtureStatusCounts(fixtures);
    const tabs = [
        {
            scope: "completed",
            label: "Completed",
            description: "Finished matches",
        },
        {
            scope: "live",
            label: "Live",
            description: "Matches in progress",
        },
        {
            scope: "upcoming",
            label: "Upcoming",
            description: "Scheduled or not started",
        },
    ];

    elements.fixtureStatusTabs.innerHTML = tabs.map((tab) => {
        const active = tab.scope === state.fixtureStatusScope;
        const count = counts[tab.scope];

        return `
            <button
                class="fixture-status-tab ${active ? "is-active" : ""} ${count === 0 ? "is-empty" : ""}"
                type="button"
                role="tab"
                aria-selected="${active ? "true" : "false"}"
                aria-label="${escapeHtml(tab.label)} matches: ${formatNumber(count)}"
                data-fixture-status-scope="${escapeHtml(tab.scope)}"
                ${count === 0 ? "disabled" : ""}
            >
                <span>${escapeHtml(tab.label)}</span>
                <strong>${formatNumber(count)}</strong>
                <small>${escapeHtml(tab.description)}</small>
            </button>
        `;
    }).join("");
}

function renderFixtureGroupTabs(fixtures) {
    if (!elements.fixtureGroupTabs) {
        return;
    }

    const statusFixtures = getFixturesForStatus(fixtures);
    const groups = getFixtureGroups(statusFixtures);
    const tabs = [
        {
            scope: "all",
            label: "All groups",
            count: statusFixtures.length,
        },
        ...groups.map((group) => ({
            scope: getFixtureScopeFromGroup(group),
            label: group,
            count: statusFixtures.filter((fixture) => fixture.group_name === group).length,
        })),
    ];

    const knockoutFixtures = statusFixtures.filter(isKnockoutFixture);

    if (knockoutFixtures.length > 0) {
        tabs.push({
            scope: "knockout",
            label: "Knockout",
            count: knockoutFixtures.length,
        });
    }

    if (tabs.length === 1 && statusFixtures.length === 0) {
        elements.fixtureGroupTabs.innerHTML = `
            <span class="fixture-group-tabs-loading">No ${escapeHtml(state.fixtureStatusScope)} fixtures are available.</span>
        `;
        return;
    }

    elements.fixtureGroupTabs.innerHTML = tabs.map((tab) => {
        const active = tab.scope === state.fixtureScope;

        return `
            <button
                class="fixture-group-tab ${active ? "is-active" : ""}"
                type="button"
                role="tab"
                aria-selected="${active ? "true" : "false"}"
                data-fixture-scope="${escapeHtml(tab.scope)}"
            >
                <span>${escapeHtml(tab.label)}</span>
                <small>${formatNumber(tab.count)}</small>
            </button>
        `;
    }).join("");
}

function updateFixtureBrowserMessage(fixtures) {
    if (!elements.fixtureBrowserMessage) {
        return;
    }

    const label = state.fixtureStatusScope === "upcoming"
        ? "upcoming"
        : state.fixtureStatusScope;
    const scopeLabel = state.fixtureScope === "all"
        ? "all groups"
        : state.fixtureScope === "knockout"
            ? "the knockout stage"
            : getGroupNameFromScope(state.fixtureScope);

    elements.fixtureBrowserMessage.textContent =
        `Showing ${fixtures.length} ${label} fixture${fixtures.length === 1 ? "" : "s"} for ${scopeLabel}.`;
}

function syncFixtureScopeFromGroupFilter() {
    state.fixtureScope = state.filters.group
        ? getFixtureScopeFromGroup(state.filters.group)
        : "all";
}

function setFixtureStatusScope(scope) {
    state.fixtureStatusScope = scope;
    state.fixtureScope = "all";
    renderFixtureBrowser(state.fixtureBrowserFixtures, { selectFirst: true });
}

function setFixtureScope(scope) {
    state.fixtureScope = scope;
    renderFixtureBrowser(state.fixtureBrowserFixtures, { selectFirst: true });
}

function renderFixtureBrowser(fixtures, options = {}) {
    state.fixtureBrowserFixtures = Array.isArray(fixtures) ? fixtures : [];
    ensureFixtureBrowserSelection(state.fixtureBrowserFixtures);

    const browserFixtures = filterFixturesForScope(state.fixtureBrowserFixtures);

    state.visibleFixtures = browserFixtures;
    updateSummary(state.allFixtures, state.visibleFixtures);
    renderFixtureStatusTabs(state.fixtureBrowserFixtures);
    renderFixtureGroupTabs(state.fixtureBrowserFixtures);
    updateFixtureBrowserMessage(browserFixtures);
    renderFixtures(browserFixtures);

    const selectionIsVisible = state.selectedFixtureId
        && browserFixtures.some((fixture) => String(fixture.id) === String(state.selectedFixtureId));

    if (options.selectFirst !== false && !selectionIsVisible && browserFixtures.length > 0) {
        selectFixture(browserFixtures[0].id, { scroll: false });
    }
}

function updateSummary(allFixtures, visibleFixtures) {
    const statusCounts = getFixtureStatusCounts(allFixtures);

    elements.totalFixtures.textContent = allFixtures.length;
    elements.completedFixtures.textContent = statusCounts.completed;
    elements.scheduledFixtures.textContent = statusCounts.upcoming;
    elements.visibleFixtures.textContent = visibleFixtures.length;
}

async function applyFilters() {
    setLoadingState();

    try {
        const [fixtures, standings, insights, aiInsights] = await Promise.all([
            fetchFixtures(state.filters),
            fetchStandings(state.filters),
            fetchInsights(state.filters),
            fetchAiInsights(state.filters),
        ]);

        state.standings = standings;
        state.insights = insights;
        state.aiInsights = aiInsights;

        renderInsights(state.insights);
        renderAiInsights(state.aiInsights);
        void refreshProviderLeaders(state.filters);
        renderStandings(state.standings);
        renderFixtureBrowser(fixtures, { selectFirst: true });
    } catch (error) {
        console.error(error);
        elements.dashboardMessage.textContent = "Unable to apply filters.";
        if (elements.fixtureBrowserMessage) {
            elements.fixtureBrowserMessage.textContent = "Unable to load the selected fixture browser view.";
        }
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
        setAiInsightsError("Unable to load structured AI insights.");
        setProviderLeadersError();
    }
}

function setLoadingState() {
    elements.dashboardMessage.textContent = "Loading fixtures...";
    elements.standingsMessage.textContent = "Loading standings...";
    elements.insightsMessage.textContent = "Loading insights...";
    setAiInsightsLoading();
    setProviderLeadersLoading();
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

function setGroupRaceLoading() {
    if (!elements.groupRaceMessage || !elements.groupRaceContainer) {
        return;
    }

    elements.groupRaceMessage.textContent =
        "Loading the current top two teams in each group.";
    elements.groupRaceContainer.innerHTML = `
        <div class="group-race-empty">
            Checking completed-fixture standings for the current group race.
        </div>
    `;
}

function setGroupRaceError() {
    if (!elements.groupRaceMessage || !elements.groupRaceContainer) {
        return;
    }

    elements.groupRaceMessage.textContent =
        "The group race could not be loaded.";
    elements.groupRaceContainer.innerHTML = `
        <div class="group-race-empty">
            Top-two group positions are currently unavailable.
        </div>
    `;
}

function renderGroupRace(groupRace, filters = {}) {
    if (!elements.groupRaceMessage || !elements.groupRaceContainer) {
        return;
    }

    const groups = Array.isArray(groupRace?.groups) ? groupRace.groups : [];
    const teamsPerGroup = Number(groupRace?.teams_per_group) || 2;
    const scopeParts = [];

    if (filters.group_name) {
        scopeParts.push(filters.group_name);
    }

    if (filters.team) {
        scopeParts.push(filters.team);
    }

    const scope = scopeParts.length
        ? ` for ${scopeParts.join(" / ")}`
        : "";

    if (groups.length === 0) {
        elements.groupRaceMessage.textContent =
            `No completed-fixture group race is available${scope} yet.`;
        elements.groupRaceContainer.innerHTML = `
            <div class="group-race-empty">
                Top-two positions will appear after completed group-stage fixtures are available.
            </div>
        `;
        return;
    }

    elements.groupRaceMessage.textContent =
        `Showing the current top ${teamsPerGroup} team${teamsPerGroup === 1 ? "" : "s"} across ${groups.length} group${groups.length === 1 ? "" : "s"}${scope}.`;

    elements.groupRaceContainer.innerHTML = groups.map((group) => {
        const teams = Array.isArray(group.teams) ? group.teams : [];

        return `
            <article class="group-race-card">
                <div class="group-race-card-heading">
                    <div>
                        <span class="group-race-label">Qualification picture</span>
                        <h4>${escapeHtml(group.group_name || "Group")}</h4>
                    </div>
                    <span class="group-race-card-count">Top ${formatNumber(teamsPerGroup)}</span>
                </div>

                <div class="group-race-table" role="table" aria-label="${escapeHtml(group.group_name || "Group")} top two">
                    <div class="group-race-row group-race-table-heading" role="row">
                        <span role="columnheader">#</span>
                        <span role="columnheader">Team</span>
                        <span role="columnheader">P</span>
                        <span role="columnheader">GD</span>
                        <span role="columnheader">Pts</span>
                    </div>
                    ${teams.map((team, index) => `
                        <div class="group-race-row" role="row">
                            <span class="group-race-rank" role="cell">${formatNumber(team.rank || index + 1)}</span>
                            <span class="group-race-team" role="cell">
                                <strong>${escapeHtml(team.team || "Team unavailable")}</strong>
                                <small>${escapeHtml(team.team_code || "")}</small>
                            </span>
                            <span role="cell">${formatNumber(team.played)}</span>
                            <span role="cell">${formatSignedNumber(team.goal_difference)}</span>
                            <strong role="cell">${formatNumber(team.points)}</strong>
                        </div>
                    `).join("")}
                </div>
            </article>
        `;
    }).join("");
}

function setAiInsightsLoading() {
    elements.aiInsightsMessage.textContent = "Loading structured AI insights...";
    elements.aiInsightsSummary.className = "ai-insights-summary";
    elements.aiInsightsSummary.textContent = "Checking fixture, standings, and provider sync context.";
    elements.aiInsightsContainer.innerHTML = "";
    setGroupRaceLoading();
}

function setAiInsightsError(message) {
    elements.aiInsightsMessage.textContent = message;
    elements.aiInsightsSummary.className = "ai-insights-summary error";
    elements.aiInsightsSummary.textContent =
        "The dashboard could not load structured AI insights. Please check that the AI insights API is running.";
    elements.aiInsightsContainer.innerHTML = `
        <div class="empty-state">
            Structured AI insights are currently unavailable.
        </div>
    `;
    setGroupRaceError();
}

function renderAiInsights(aiInsights) {
    elements.aiInsightsContainer.innerHTML = "";

    if (!aiInsights || !Array.isArray(aiInsights.insights)) {
        setAiInsightsError("Unable to load structured AI insights.");
        return;
    }

    const mode = aiInsights.mode || "fallback";
    const provider = aiInsights.provider || "rules_based_ai_insights";
    const model = aiInsights.model || "rules_based_v1";
    const fixtureCount = aiInsights.metadata?.fixture_count ?? 0;
    const completedCount = aiInsights.metadata?.completed_count ?? 0;
    const syncStatus = aiInsights.metadata?.sync_status || "unknown";

    elements.aiInsightsMessage.textContent =
        `Generated ${aiInsights.insights.length} structured insight${aiInsights.insights.length === 1 ? "" : "s"} using ${provider} (${model}).`;

    elements.aiInsightsSummary.className = "ai-insights-summary success";
    elements.aiInsightsSummary.textContent =
        `${aiInsights.summary} Mode: ${mode}. Fixtures: ${fixtureCount}. Completed: ${completedCount}. Sync status: ${syncStatus}.`;

    renderGroupRace(aiInsights.group_race, aiInsights.filters || {});

    if (aiInsights.insights.length === 0) {
        elements.aiInsightsContainer.innerHTML = `
            <div class="empty-state">
                No structured AI insights are available yet.
            </div>
        `;
        return;
    }

    aiInsights.insights.forEach((insight) => {
        const card = document.createElement("article");
        card.className = "ai-insight-card";

        card.innerHTML = `
            <span class="ai-insight-category">${escapeHtml(insight.category || "insight")}</span>
            <strong>${escapeHtml(insight.title || "AI Insight")}</strong>
            <p>${escapeHtml(insight.message || "No insight message available.")}</p>
        `;

        elements.aiInsightsContainer.appendChild(card);
    });
}

function setProviderLeadersLoading() {
    if (!elements.playerStatsMessage || !elements.playerStatsContainer) {
        return;
    }

    elements.playerStatsMessage.textContent =
        "Loading provider-backed scorer and card leaderboards...";
    elements.playerStatsContainer.innerHTML = `
        <div class="empty-state">
            Loading real scorer and discipline events from stored provider match details.
        </div>
    `;
}

function setProviderLeadersError() {
    if (!elements.playerStatsMessage || !elements.playerStatsContainer) {
        return;
    }

    elements.playerStatsMessage.textContent =
        "Provider-backed player leaderboards are currently unavailable.";
    elements.playerStatsContainer.innerHTML = `
        <div class="empty-state">
            Player leaders are shown only when real provider match details are available.
        </div>
    `;
}

function getProviderLeaderScope(filters = {}) {
    const scope = [];

    if (filters.group_name) {
        scope.push(filters.group_name);
    }

    if (filters.team) {
        scope.push(filters.team);
    }

    if (scope.length === 0) {
        return "";
    }

    return ` for ${scope.join(" / ")}`;
}

function getPlayerMetricText(value, singularLabel, pluralLabel) {
    const metricValue = Number(formatNumber(value));

    return `${metricValue} ${metricValue === 1 ? singularLabel : pluralLabel}`;
}

function renderPlayerLeaderList(players, metricKey, singularLabel, pluralLabel) {
    if (!Array.isArray(players) || players.length === 0) {
        return `
            <p class="player-leader-empty">
                No provider-backed ${pluralLabel.toLowerCase()} have been recorded in this scope.
            </p>
        `;
    }

    return `
        <ol class="player-leader-list">
            ${players.map((player, index) => {
                const playerName = player?.player_name || "Player unavailable";
                const team = player?.team || "Team unavailable";
                const teamCode = player?.team_code ? ` · ${player.team_code}` : "";
                const groupName = player?.group_name || "Group unavailable";
                const metricText = getPlayerMetricText(
                    player?.[metricKey],
                    singularLabel,
                    pluralLabel,
                );

                return `
                    <li class="player-leader-row">
                        <span class="player-leader-rank">${index + 1}</span>
                        <span class="player-leader-identity">
                            <strong>${escapeHtml(playerName)}</strong>
                            <small>${escapeHtml(`${team}${teamCode} · ${groupName}`)}</small>
                        </span>
                        <span class="player-leader-metric">${escapeHtml(metricText)}</span>
                    </li>
                `;
            }).join("")}
        </ol>
    `;
}

function renderPlayerLeaderboardCard({
    title,
    detail,
    players,
    metricKey,
    singularLabel,
    pluralLabel,
}) {
    return `
        <article class="player-leaderboard-card">
            <div class="player-leaderboard-heading">
                <div>
                    <span class="player-stat-label">${escapeHtml(title)}</span>
                    <p>${escapeHtml(detail)}</p>
                </div>
            </div>
            ${renderPlayerLeaderList(
                players,
                metricKey,
                singularLabel,
                pluralLabel,
            )}
        </article>
    `;
}

function renderProviderLeaders(data) {
    if (!data || !data.leaderboards) {
        setProviderLeadersError();
        return;
    }

    const coverage = data.coverage || {};
    const leaderboards = data.leaderboards || {};
    const assistData = data.assist_data || {};
    const filters = data.filters || {};
    const completedFixtureCount = formatNumber(coverage.completed_fixture_count);
    const detailedFixtureCount = formatNumber(coverage.detailed_fixture_count);
    const provider = data.provider || "provider";
    const scope = getProviderLeaderScope(filters);

    elements.playerStatsMessage.textContent =
        `Showing real scorer and card leaders${scope} from ${detailedFixtureCount} detailed completed fixture${detailedFixtureCount === 1 ? "" : "s"}.`;

    elements.playerStatsContainer.innerHTML = `
        <article class="provider-coverage-card">
            <div>
                <span class="provider-coverage-label">Live data coverage</span>
                <strong>${escapeHtml(`${detailedFixtureCount} of ${completedFixtureCount} completed fixtures have stored match details`)}</strong>
                <p>
                    Goals and cards are derived from the stored ${escapeHtml(provider)} event payload.
                    No generic sample player records are used here.
                </p>
            </div>
            <span class="provider-source-badge">${escapeHtml(provider)}</span>
        </article>

        ${renderPlayerLeaderboardCard({
            title: "Top scorers",
            detail: "Goal events from completed provider-backed matches.",
            players: leaderboards.top_scorers,
            metricKey: "goals",
            singularLabel: "goal",
            pluralLabel: "goals",
        })}

        ${renderPlayerLeaderboardCard({
            title: "Yellow card leaders",
            detail: "Discipline events recorded in completed matches.",
            players: leaderboards.yellow_card_leaders,
            metricKey: "yellow_cards",
            singularLabel: "yellow card",
            pluralLabel: "yellow cards",
        })}

        ${renderPlayerLeaderboardCard({
            title: "Red card leaders",
            detail: "Dismissal events recorded in completed matches.",
            players: leaderboards.red_card_leaders,
            metricKey: "red_cards",
            singularLabel: "red card",
            pluralLabel: "red cards",
        })}

        <aside class="assist-availability-note">
            <strong>Assist leaders unavailable</strong>
            <p>${escapeHtml(
                assistData.message
                || "The current provider match-detail payload does not include assist events."
            )}</p>
        </aside>
    `;
}

function setLatestCompletedSummaryLoading() {
    if (!elements.latestCompletedSummary) {
        return;
    }

    elements.latestCompletedSummary.className = "latest-completed-summary";
    elements.latestCompletedSummary.innerHTML = `
        <span class="latest-completed-loading">
            Loading the latest provider-backed completed match...
        </span>
    `;
}

function setLatestCompletedSummaryError() {
    if (!elements.latestCompletedSummary) {
        return;
    }

    elements.latestCompletedSummary.className = "latest-completed-summary error";
    elements.latestCompletedSummary.innerHTML = `
        <strong>Latest completed match unavailable</strong>
        <p>
            The provider-backed latest-result summary could not be loaded right now.
        </p>
    `;
}

function formatLatestMajorIncident(incident) {
    if (incident?.description) {
        return String(incident.description);
    }

    const player = incident?.player || "Player unavailable";
    const team = incident?.team || incident?.team_code || "team unavailable";
    const color = incident?.color || "red";
    const minute = incident?.minute === null || incident?.minute === undefined
        ? ""
        : ` · ${incident.minute}'`;

    return `${player} (${team}) · ${color} card${minute}`;
}

function renderLatestCompletedSummary(data) {
    const fixture = data?.fixture;

    if (!fixture || !fixture.home_team || !fixture.away_team) {
        setLatestCompletedSummaryError();
        return;
    }

    const majorIncidents = Array.isArray(data.major_incidents)
        ? data.major_incidents
        : [];
    const scoreLine = `${fixture.home_team} ${formatScore(fixture.home_score)}–${formatScore(fixture.away_score)} ${fixture.away_team}`;
    const provider = data.provider || "provider";
    const resultSummary = data.summary || "No provider-backed summary is available for this completed match.";
    const detailLabel = data.detail_available
        ? "Detailed events stored"
        : "Fixture result only";

    const incidentsMarkup = majorIncidents.length > 0
        ? `
            <div class="latest-major-incidents">
                <strong>Major incidents</strong>
                <ul>
                    ${majorIncidents.map((incident) => `
                        <li>${escapeHtml(formatLatestMajorIncident(incident))}</li>
                    `).join("")}
                </ul>
            </div>
        `
        : "";

    elements.latestCompletedSummary.className = "latest-completed-summary success";
    elements.latestCompletedSummary.innerHTML = `
        <div class="latest-completed-heading">
            <div>
                <span class="latest-completed-label">Provider-backed latest result</span>
                <h3>Latest Completed Match</h3>
            </div>
            <span class="provider-source-badge">${escapeHtml(provider)}</span>
        </div>

        <strong class="latest-completed-score">${escapeHtml(scoreLine)}</strong>

        ${incidentsMarkup}

        <p class="latest-completed-copy">${escapeHtml(resultSummary)}</p>

        <div class="latest-completed-meta">
            <span>${escapeHtml(fixture.group_name || "Group unavailable")}</span>
            <span>${escapeHtml(formatDateTime(fixture.kickoff_time))}</span>
            <span>${escapeHtml(detailLabel)}</span>
        </div>
    `;
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

    const standingsByGroup = standings.reduce((groups, team) => {
        const groupName = team.group_name || "Other";
        groups[groupName] = groups[groupName] || [];
        groups[groupName].push(team);
        return groups;
    }, {});

    const groupNames = Object.keys(standingsByGroup).sort((left, right) =>
        left.localeCompare(right, undefined, { numeric: true })
    );

    if (state.fixtureScope === "knockout") {
        elements.standingsMessage.textContent =
            "Knockout fixtures are selected above. Group standings remain based on completed group-stage results.";
    } else {
        const selectedGroup = state.filters.group || "all groups";
        elements.standingsMessage.textContent =
            `Showing compact standings for ${groupNames.length} group${groupNames.length === 1 ? "" : "s"} in ${selectedGroup}.`;
    }

    const groupGrid = document.createElement("div");
    groupGrid.className = "group-standings-grid";

    groupNames.forEach((groupName) => {
        const rows = standingsByGroup[groupName];

        const card = document.createElement("article");
        card.className = "group-standings-card";

        card.innerHTML = `
            <div class="group-standings-header">
                <div>
                    <span class="group-standings-label">Standings</span>
                    <h3>${escapeHtml(groupName)}</h3>
                </div>
                <span>${formatNumber(rows.length)} teams</span>
            </div>

            <div class="standings-compact-table" role="table" aria-label="${escapeHtml(groupName)} standings">
                <div class="standings-compact-row standings-compact-heading" role="row">
                    <span role="columnheader">#</span>
                    <span role="columnheader">Team</span>
                    <span role="columnheader">P</span>
                    <span role="columnheader">GD</span>
                    <span role="columnheader">Pts</span>
                </div>
                ${rows.map((team, index) => `
                    <div class="standings-compact-row" role="row">
                        <span role="cell">${index + 1}</span>
                        <span class="standings-team" role="cell">
                            <strong>${escapeHtml(team.team)}</strong>
                            <small>${escapeHtml(team.team_code || "")}</small>
                        </span>
                        <span role="cell">${formatNumber(team.played)}</span>
                        <span role="cell">${formatSignedNumber(team.goal_difference)}</span>
                        <strong role="cell">${formatNumber(team.points)}</strong>
                    </div>
                `).join("")}
            </div>
        `;

        groupGrid.appendChild(card);
    });

    elements.standingsContainer.appendChild(groupGrid);
}

function buildFixtureCardMarkup(fixture) {
    const fixtureId = fixture.id;
    const savedSummary = state.fixtureSummaries[fixtureId];
    const matchLabel = `${fixture.home_team || "Home team"} vs ${fixture.away_team || "Away team"}`;
    const selected = String(state.selectedFixtureId) === String(fixtureId);

    return `
        <article
            class="fixture-card ${selected ? "is-selected" : ""}"
            tabindex="0"
            role="button"
            aria-label="Open match detail for ${escapeHtml(matchLabel)}"
            aria-pressed="${selected ? "true" : "false"}"
            data-fixture-card-id="${escapeHtml(fixtureId)}"
        >
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

            <div class="fixture-card-hint">Open match detail</div>

            <div class="fixture-ai-actions">
                <button
                    class="fixture-ai-button"
                    type="button"
                    data-fixture-summary-id="${escapeHtml(fixtureId)}"
                >
                    Generate Match Summary
                </button>
            </div>

            <div
                class="fixture-ai-summary ${savedSummary ? "success" : ""}"
                id="fixture-summary-${escapeHtml(fixtureId)}"
                ${savedSummary ? "" : "hidden"}
            >
                ${savedSummary ? escapeHtml(savedSummary) : ""}
            </div>
        </article>
    `;
}

function groupFixturesForDisplay(fixtures) {
    return fixtures.reduce((groups, fixture) => {
        const groupName = getFixtureDisplayGroup(fixture);

        if (!groups[groupName]) {
            groups[groupName] = [];
        }

        groups[groupName].push(fixture);
        return groups;
    }, {});
}

function renderFixtures(fixtures) {
    elements.fixturesContainer.innerHTML = "";

    if (fixtures.length === 0) {
        elements.fixturesContainer.className = "fixtures-grid";
        elements.fixturesContainer.innerHTML = `
            <div class="empty-state">
                No fixtures match the selected status and group.
            </div>
        `;
        elements.dashboardMessage.textContent = "Choose another match status or group.";
        return;
    }

    const activeLabel = state.fixtureStatusScope === "upcoming"
        ? "upcoming"
        : state.fixtureStatusScope;
    elements.dashboardMessage.textContent =
        `Showing ${fixtures.length} ${activeLabel} fixture${fixtures.length === 1 ? "" : "s"}.`;

    const renderAllGroups = state.fixtureScope === "all" && fixtures.length > 6;

    if (!renderAllGroups) {
        elements.fixturesContainer.className = "fixtures-grid";
        elements.fixturesContainer.innerHTML = fixtures
            .map((fixture) => buildFixtureCardMarkup(fixture))
            .join("");
        return;
    }

    const groups = groupFixturesForDisplay(fixtures);
    const groupNames = Object.keys(groups).sort((left, right) =>
        left.localeCompare(right, undefined, { numeric: true })
    );

    elements.fixturesContainer.className = "fixtures-grouped-sections";
    elements.fixturesContainer.innerHTML = groupNames.map((groupName, index) => `
        <details class="fixture-group-section" ${index === 0 ? "open" : ""}>
            <summary>
                <span>${escapeHtml(groupName)}</span>
                <small>${formatNumber(groups[groupName].length)} match${groups[groupName].length === 1 ? "" : "es"}</small>
            </summary>
            <div class="fixture-group-fixtures">
                ${groups[groupName].map((fixture) => buildFixtureCardMarkup(fixture)).join("")}
            </div>
        </details>
    `).join("");
}

function syncSelectedFixtureCard() {
    document.querySelectorAll("[data-fixture-card-id]").forEach((card) => {
        const selected = String(card.dataset.fixtureCardId) === String(state.selectedFixtureId);

        card.classList.toggle("is-selected", selected);
        card.setAttribute("aria-pressed", selected ? "true" : "false");
    });
}

function getMatchDetailElements() {
    return {
        panel: elements.matchDetailPanel || document.querySelector("#match-detail-panel"),
        title: document.querySelector("#match-detail-title"),
        status: document.querySelector("#match-detail-status"),
        detail: document.querySelector("#selected-match-detail"),
    };
}

async function fetchFixtureDetail(fixtureId) {
    const possibleEndpoints = [
        `/api/fixtures/${fixtureId}/detail`,
        `/fixtures/${fixtureId}/detail`,
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            return await response.json();
        } catch (error) {
            console.warn(`Unable to fetch fixture detail from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load provider-backed fixture detail.");
}

function formatMatchScoreline(fixture) {
    const homeScore = formatScore(fixture.home_score);
    const awayScore = formatScore(fixture.away_score);

    return `${homeScore} - ${awayScore}`;
}

function getTeamNameFromSide(side, fixture) {
    return side === "away"
        ? fixture.away_team || "Away team"
        : fixture.home_team || "Home team";
}

function formatDetailMinute(value) {
    if (value === null || value === undefined || value === "") {
        return "–";
    }

    return `${value}'`;
}

function getMatchDetailTabs() {
    return [
        { id: "overview", label: "Overview" },
        { id: "timeline", label: "Timeline" },
        { id: "stats", label: "Stats" },
        { id: "lineups", label: "Lineups" },
    ];
}

function renderMatchDetailTabs() {
    return `
        <div class="match-detail-tabs" role="tablist" aria-label="Selected match detail">
            ${getMatchDetailTabs().map((tab) => {
                const active = tab.id === state.activeMatchDetailTab;

                return `
                    <button
                        class="match-detail-tab ${active ? "is-active" : ""}"
                        type="button"
                        role="tab"
                        aria-selected="${active ? "true" : "false"}"
                        data-match-detail-tab="${tab.id}"
                    >
                        ${tab.label}
                    </button>
                `;
            }).join("")}
        </div>
    `;
}

function isRedCard(card) {
    const color = String(card?.color || "").toLowerCase();

    return color.includes("red") || color.includes("second");
}

function buildTimelineEvents(fixture, detail) {
    const events = [];

    (detail?.goals || []).forEach((goal) => {
        events.push({
            minute: goal.minute,
            kind: "goal",
            team: getTeamNameFromSide(goal.team, fixture),
            actor: goal.scorer || "Scorer unavailable",
            description: "Goal",
        });
    });

    (detail?.cards || []).forEach((card) => {
        const redCard = isRedCard(card);

        events.push({
            minute: card.minute,
            kind: redCard ? "red-card" : "yellow-card",
            team: getTeamNameFromSide(card.team, fixture),
            actor: card.player || "Player unavailable",
            description: redCard ? "Red card" : "Yellow card",
        });
    });

    (detail?.substitutions || []).forEach((substitution) => {
        events.push({
            minute: substitution.minute,
            kind: "substitution",
            team: getTeamNameFromSide(substitution.team, fixture),
            actor: substitution.on || "Substitute",
            description: `On for ${substitution.off || "player unavailable"}`,
        });
    });

    return events.sort((left, right) => {
        const leftMinute = parseMatchMinute(left.minute);
        const rightMinute = parseMatchMinute(right.minute);

        if (leftMinute !== rightMinute) {
            return leftMinute - rightMinute;
        }

        return left.kind.localeCompare(right.kind);
    });
}

function parseMatchMinute(value) {
    const match = String(value ?? "").match(/^(\d+)(?:\+(\d+))?/);

    if (!match) {
        return Number.MAX_SAFE_INTEGER;
    }

    return Number(match[1]) + (Number(match[2] || 0) / 100);
}

function renderKeyMatchEvents(fixture, detail) {
    const events = buildTimelineEvents(fixture, detail)
        .filter((event) => event.kind === "goal" || event.kind === "red-card")
        .slice(0, 6);

    if (events.length === 0) {
        return `
            <div class="match-detail-empty">
                No goals or red-card incidents have been supplied for this match.
            </div>
        `;
    }

    return `
        <div class="match-key-events">
            ${events.map((event) => `
                <div class="match-key-event ${event.kind}">
                    <span>${escapeHtml(formatDetailMinute(event.minute))}</span>
                    <div>
                        <strong>${escapeHtml(event.description)} · ${escapeHtml(event.actor)}</strong>
                        <small>${escapeHtml(event.team)}</small>
                    </div>
                </div>
            `).join("")}
        </div>
    `;
}

function formatWeather(weather) {
    if (!weather || Object.keys(weather).length === 0) {
        return "Weather data unavailable";
    }

    const parts = [];

    if (weather.tempC !== undefined && weather.tempC !== null) {
        parts.push(`${weather.tempC}°C`);
    }

    if (weather.humidityPct !== undefined && weather.humidityPct !== null) {
        parts.push(`${weather.humidityPct}% humidity`);
    }

    if (weather.windKmh !== undefined && weather.windKmh !== null) {
        parts.push(`${weather.windKmh} km/h wind`);
    }

    return parts.length ? parts.join(" · ") : "Weather data unavailable";
}

function renderStoredProviderDetailCoverage(coverage) {
    const hasStoredDetail = coverage?.detail_state === "available";
    const message = coverage?.message || (
        "Stored provider event coverage is unavailable for this fixture. "
        + "No live provider lookup was attempted."
    );

    if (!hasStoredDetail) {
        return `
            <section class="stored-detail-coverage unavailable">
                <div class="stored-detail-coverage-heading">
                    <div>
                        <span>Stored provider detail</span>
                        <h4>Unavailable</h4>
                    </div>
                    <strong>Read-only</strong>
                </div>
                <p>${escapeHtml(message)}</p>
            </section>
        `;
    }

    const eventTypes = coverage.event_types || {};
    const eventCoverage = [
        ["Goals", eventTypes.goals || {}],
        ["Cards", eventTypes.cards || {}],
        ["Substitutions", eventTypes.substitutions || {}],
    ];

    return `
        <section class="stored-detail-coverage available">
            <div class="stored-detail-coverage-heading">
                <div>
                    <span>Stored provider detail</span>
                    <h4>${escapeHtml(coverage.provider || "Provider not recorded")}</h4>
                </div>
                <strong>${escapeHtml(formatStoredDetailRefresh(coverage.stored_detail_updated_at))}</strong>
            </div>

            <div class="stored-detail-coverage-grid">
                ${eventCoverage.map(([label, eventType]) => {
                    const state = eventType.state || "unavailable";
                    const count = eventType.count;
                    const status = state === "recorded"
                        ? `${formatNumber(count)} recorded`
                        : state === "no_stored_events"
                            ? "No stored events"
                            : "Unavailable";

                    return `
                        <article class="stored-detail-event-coverage ${escapeHtml(state)}">
                            <span>${escapeHtml(label)}</span>
                            <strong>${escapeHtml(status)}</strong>
                            <p>${escapeHtml(eventType.message || "Stored event coverage is unavailable.")}</p>
                        </article>
                    `;
                }).join("")}
            </div>

            <p class="stored-detail-coverage-note">${escapeHtml(message)}</p>
        </section>
    `;
}

function renderMatchDetailOverview(fixture, detail, options = {}) {
    const savedSummary = state.fixtureSummaries[fixture.id];
    const formations = detail?.formations || {};
    const referee = detail?.referee || {};
    const weather = detail?.weather || {};
    const storedEventCoverage = options.coverage || null;

    if (options.isLoading) {
        return `
            <div class="match-detail-loading">
                Loading provider-backed timeline, statistics, and lineup data...
            </div>
        `;
    }

    if (!detail) {
        const reason = options.error
            ? "Provider match detail could not be loaded right now."
            : "Provider match detail has not been stored for this fixture yet.";

        return `
            ${renderStoredProviderDetailCoverage(storedEventCoverage)}
            <div class="match-detail-note ${options.error ? "error" : ""}">
                <strong>Provider detail status:</strong> ${escapeHtml(reason)}
            </div>
            <div class="match-detail-context">
                <h4>AI match summary</h4>
                <p>${escapeHtml(savedSummary || "No match summary generated yet. Use the Generate Match Summary button on the fixture card.")}</p>
            </div>
        `;
    }

    return `
        <div class="match-detail-overview-grid">
            <article class="match-detail-fact">
                <span>Formation</span>
                <strong>${escapeHtml(formations.home || "–")} <small>vs</small> ${escapeHtml(formations.away || "–")}</strong>
            </article>
            <article class="match-detail-fact">
                <span>Referee</span>
                <strong>${escapeHtml(referee.name || "Not supplied")}</strong>
                <small>${escapeHtml(referee.country || "")}</small>
            </article>
            <article class="match-detail-fact">
                <span>Conditions</span>
                <strong>${escapeHtml(formatWeather(weather))}</strong>
            </article>
            <article class="match-detail-fact">
                <span>Provider</span>
                <strong>${escapeHtml(detail.provider || "Unknown provider")}</strong>
                <small>Match ID ${escapeHtml(detail.provider_match_id || "–")}</small>
            </article>
            <article class="match-detail-fact">
                <span>Stored detail refresh</span>
                <strong>${escapeHtml(formatStoredDetailRefresh(detail.updated_at))}</strong>
                <small>Stored provider payload; not a live detail request.</small>
            </article>
        </div>

        ${renderStoredProviderDetailCoverage(storedEventCoverage)}

        <div class="match-detail-context">
            <h4>Key incidents</h4>
            ${renderKeyMatchEvents(fixture, detail)}
        </div>

        <div class="match-detail-context">
            <h4>AI match summary</h4>
            <p>${escapeHtml(savedSummary || "No match summary generated yet. Use the Generate Match Summary button on the fixture card.")}</p>
        </div>
    `;
}

function renderMatchTimelineTab(fixture, detail) {
    if (!detail) {
        return `
            <div class="match-detail-empty">
                Timeline data is not available for this fixture yet.
            </div>
        `;
    }

    const events = buildTimelineEvents(fixture, detail);

    if (events.length === 0) {
        return `
            <div class="match-detail-empty">
                No provider event timeline is available for this fixture.
            </div>
        `;
    }

    return `
        <div class="match-timeline" aria-label="Match event timeline">
            ${events.map((event) => `
                <article class="timeline-event ${event.kind}">
                    <span class="timeline-minute">${escapeHtml(formatDetailMinute(event.minute))}</span>
                    <div class="timeline-marker" aria-hidden="true"></div>
                    <div class="timeline-content">
                        <strong>${escapeHtml(event.description)} · ${escapeHtml(event.actor)}</strong>
                        <p>${escapeHtml(event.team)}</p>
                    </div>
                </article>
            `).join("")}
        </div>
    `;
}

function getStatisticNumber(statistics, key) {
    const value = Number(statistics?.[key]);

    return Number.isFinite(value) ? value : 0;
}

function formatMatchStatistic(key, value) {
    if (key === "possessionPct") {
        return `${value}%`;
    }

    if (key === "expectedGoals") {
        return value.toFixed(2);
    }

    return String(value);
}

function getStatisticShare(homeValue, awayValue) {
    const total = homeValue + awayValue;

    if (total <= 0) {
        return 50;
    }

    return Math.max(0, Math.min(100, (homeValue / total) * 100));
}

function renderStatisticComparison(label, key, homeStats, awayStats) {
    const homeValue = getStatisticNumber(homeStats, key);
    const awayValue = getStatisticNumber(awayStats, key);
    const homeShare = getStatisticShare(homeValue, awayValue);

    return `
        <article class="stat-comparison-row">
            <div class="stat-comparison-values">
                <strong>${escapeHtml(formatMatchStatistic(key, homeValue))}</strong>
                <span>${escapeHtml(label)}</span>
                <strong>${escapeHtml(formatMatchStatistic(key, awayValue))}</strong>
            </div>
            <div class="stat-comparison-track" aria-label="${escapeHtml(label)} comparison">
                <span class="stat-comparison-home" style="width: ${homeShare.toFixed(2)}%"></span>
                <span class="stat-comparison-away" style="width: ${(100 - homeShare).toFixed(2)}%"></span>
            </div>
        </article>
    `;
}

function renderMatchStatsTab(fixture, detail) {
    const statistics = detail?.statistics || {};
    const homeStats = statistics.home || {};
    const awayStats = statistics.away || {};

    if (Object.keys(homeStats).length === 0 && Object.keys(awayStats).length === 0) {
        return `
            <div class="match-detail-empty">
                Team statistics are not available for this fixture yet.
            </div>
        `;
    }

    const metrics = [
        ["Possession", "possessionPct"],
        ["Shots", "shotsTotal"],
        ["Shots on target", "shotsOnGoal"],
        ["Expected goals", "expectedGoals"],
        ["Accurate passes", "passesAccurate"],
        ["Corners", "corners"],
        ["Fouls", "fouls"],
    ];

    return `
        <div class="match-stats-heading">
            <span>${escapeHtml(fixture.home_team || "Home")}</span>
            <strong>Match statistics</strong>
            <span>${escapeHtml(fixture.away_team || "Away")}</span>
        </div>
        <div class="match-stats-comparison">
            ${metrics.map(([label, key]) =>
                renderStatisticComparison(label, key, homeStats, awayStats)
            ).join("")}
        </div>
        <p class="match-stats-note">
            Comparison bars use provider-supplied values for this completed match.
        </p>
    `;
}

function getLineupGroups(players) {
    const safePlayers = Array.isArray(players) ? players : [];

    return {
        starters: safePlayers.filter((player) => player?.starter),
        substitutes: safePlayers.filter((player) => !player?.starter),
    };
}

function renderLineupList(players, emptyMessage) {
    if (!players.length) {
        return `<div class="match-detail-empty compact">${escapeHtml(emptyMessage)}</div>`;
    }

    return `
        <div class="lineup-list">
            ${players.map((player) => `
                <div class="lineup-player">
                    <span class="lineup-number">${escapeHtml(player.number ?? "–")}</span>
                    <div>
                        <strong>${escapeHtml(player.player || "Player unavailable")}</strong>
                        <small>
                            ${escapeHtml(player.position || "Position unavailable")}
                            ${player.captain ? " · Captain" : ""}
                        </small>
                    </div>
                </div>
            `).join("")}
        </div>
    `;
}

function renderLineupTeam(teamName, formation, players) {
    const groups = getLineupGroups(players);

    return `
        <article class="lineup-team-card">
            <div class="lineup-team-heading">
                <div>
                    <span>Lineup</span>
                    <h4>${escapeHtml(teamName)}</h4>
                </div>
                <strong>${escapeHtml(formation || "Formation unavailable")}</strong>
            </div>

            <h5>Starting XI</h5>
            ${renderLineupList(groups.starters, "Starting lineup not supplied.")}

            ${groups.substitutes.length ? `
                <h5>Bench</h5>
                ${renderLineupList(groups.substitutes, "No bench data supplied.")}
            ` : ""}
        </article>
    `;
}

function renderMatchLineupsTab(fixture, detail) {
    const lineups = detail?.lineups || {};
    const formations = detail?.formations || {};

    if (!Array.isArray(lineups.home) && !Array.isArray(lineups.away)) {
        return `
            <div class="match-detail-empty">
                Lineups are not available for this fixture yet.
            </div>
        `;
    }

    return `
        <div class="lineup-grid">
            ${renderLineupTeam(fixture.home_team || "Home", formations.home, lineups.home || [])}
            ${renderLineupTeam(fixture.away_team || "Away", formations.away, lineups.away || [])}
        </div>
    `;
}

function renderMatchDetailContent(fixture, detail, options = {}) {
    if (state.activeMatchDetailTab === "timeline") {
        return renderMatchTimelineTab(fixture, detail);
    }

    if (state.activeMatchDetailTab === "stats") {
        return renderMatchStatsTab(fixture, detail);
    }

    if (state.activeMatchDetailTab === "lineups") {
        return renderMatchLineupsTab(fixture, detail);
    }

    return renderMatchDetailOverview(fixture, detail, options);
}

function renderFixtureDetail(fixture, detail = null, options = {}) {
    const matchDetail = getMatchDetailElements();
    const detailOptions = {
        ...options,
        coverage: options.coverage ?? state.selectedFixtureCoverage,
    };

    if (!matchDetail.panel || !matchDetail.title || !matchDetail.status || !matchDetail.detail) {
        return;
    }

    const homeTeam = fixture.home_team || "Home team";
    const awayTeam = fixture.away_team || "Away team";

    matchDetail.title.textContent = `${homeTeam} vs ${awayTeam}`;
    matchDetail.status.className = `status-pill ${getStatusClass(fixture.status)}`;
    matchDetail.status.textContent = formatStatus(fixture.status);

    if (options.scroll) {
        matchDetail.panel.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    matchDetail.detail.innerHTML = `
        <div class="match-detail-scoreboard">
            <div class="match-detail-team">
                <span>${escapeHtml(homeTeam)}</span>
                <small>${escapeHtml(fixture.home_team_code || "HOME")}</small>
            </div>
            <strong>${escapeHtml(formatMatchScoreline(fixture))}</strong>
            <div class="match-detail-team">
                <span>${escapeHtml(awayTeam)}</span>
                <small>${escapeHtml(fixture.away_team_code || "AWAY")}</small>
            </div>
        </div>

        <div class="match-detail-grid">
            <div>
                <span>Kickoff</span>
                <strong>${escapeHtml(formatDateTime(fixture.kickoff_time))}</strong>
            </div>
            <div>
                <span>Venue</span>
                <strong>${escapeHtml(fixture.venue || "Venue not available yet")}</strong>
            </div>
            <div>
                <span>Competition</span>
                <strong>${escapeHtml(fixture.competition || "FIFA World Cup 2026")}</strong>
            </div>
            <div>
                <span>Stage / Group</span>
                <strong>${escapeHtml(fixture.group_name || fixture.stage || "Not available yet")}</strong>
            </div>
        </div>

        ${renderMatchDetailTabs()}

        <div class="match-detail-tab-panel" role="tabpanel">
            ${renderMatchDetailContent(fixture, detail, detailOptions)}
        </div>
    `;
}

async function selectFixture(fixtureId, options = {}) {
    const fixtureFromState = state.visibleFixtures.find((fixture) => String(fixture.id) === String(fixtureId))
        || state.allFixtures.find((fixture) => String(fixture.id) === String(fixtureId));

    if (!fixtureFromState) {
        return;
    }

    state.selectedFixture = fixtureFromState;
    state.selectedFixtureId = String(fixtureId);
    state.selectedFixtureDetail = null;
    state.selectedFixtureCoverage = null;
    state.activeMatchDetailTab = "overview";
    syncSelectedFixtureCard();

    renderFixtureDetail(fixtureFromState, null, {
        isLoading: true,
        scroll: options.scroll === true,
    });

    try {
        const payload = await fetchFixtureDetail(fixtureId);
        const fixture = payload.fixture || fixtureFromState;
        const detail = payload.detail_available ? payload.detail : null;
        const coverage = payload.stored_event_coverage || null;

        state.selectedFixture = fixture;
        state.selectedFixtureDetail = detail;
        state.selectedFixtureCoverage = coverage;

        renderFixtureDetail(fixture, detail, { coverage });
    } catch (error) {
        console.error(error);

        renderFixtureDetail(fixtureFromState, null, {
            error: true,
        });
    }
}

async function generateAiSummary() {
    elements.generateAiSummary.disabled = true;
    elements.generateAiSummary.textContent = "Generating...";
    elements.aiSummaryMessage.textContent = "Generating a live local AI summary with deterministic fallback...";
    elements.aiSummaryOutput.className = "ai-summary-output";
    elements.aiSummaryOutput.textContent = "Generating AI summary. This may take a few seconds.";

    try {
        const response = await fetch("/ai/fixtures/summary");

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Unable to generate AI summary.");
        }

        const data = await response.json();

        const mode = data.mode || "unknown";
        const fallbackReason = data.fallback_reason ? ` Fallback reason: ${data.fallback_reason}` : "";

        elements.aiSummaryMessage.textContent =
            `Generated by ${data.provider} using ${data.model}. Mode: ${mode}.${fallbackReason}`;
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
    summaryElement.hidden = false;
    summaryElement.className = "fixture-ai-summary";
    summaryElement.textContent = "Generating match summary...";

    try {
        const response = await fetch(`/ai/fixtures/${fixtureId}/summary`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Unable to generate match summary.");
        }

        const data = await response.json();

        const mode = data.mode || "unknown";
        const summaryText = `[${mode}] ${data.summary}`;

        state.fixtureSummaries[fixtureId] = summaryText;
        summaryElement.className = "fixture-ai-summary success";
        summaryElement.textContent = summaryText;

        if (
            state.selectedFixture
            && String(state.selectedFixtureId) === String(fixtureId)
        ) {
            renderFixtureDetail(
                state.selectedFixture,
                state.selectedFixtureDetail,
                { scroll: false },
            );
        }

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
    const category = getFixtureStatusCategory({ status });

    if (category === "completed") {
        return "status-complete";
    }

    if (category === "upcoming") {
        return "status-scheduled";
    }

    if (category === "live") {
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

function getSyncFreshnessClass(state) {
    return String(state || "unavailable").replaceAll("_", "-");
}

function formatSyncFreshness(state) {
    const labels = {
        fresh: "Fresh",
        aging: "Aging",
        stale: "Stale",
        last_sync_failed: "Last Sync Failed",
        not_started: "No Sync Yet",
        unavailable: "Unavailable",
    };

    return labels[state] || "Unavailable";
}

function formatDataAgeSeconds(value) {
    if (value === null || value === undefined) {
        return "No successful sync is recorded yet.";
    }

    const seconds = Number(value);

    if (Number.isNaN(seconds) || seconds < 0) {
        return "The latest successful sync timestamp is unavailable.";
    }

    if (seconds < 60) {
        return "Last successful sync was less than a minute ago.";
    }

    if (seconds < 3600) {
        return `Last successful sync was ${Math.floor(seconds / 60)} minute${Math.floor(seconds / 60) === 1 ? "" : "s"} ago.`;
    }

    return `Last successful sync was ${Math.floor(seconds / 3600)} hour${Math.floor(seconds / 3600) === 1 ? "" : "s"} ago.`;
}

function formatSchedulerMode(scheduler) {
    if (!scheduler || !scheduler.enabled) {
        return "Manual only";
    }

    const interval = Number(scheduler.interval_minutes);

    if (Number.isNaN(interval) || interval <= 0) {
        return "Automatic";
    }

    return `Every ${interval} min`;
}

function formatStoredDetailRefresh(value) {
    if (!value) {
        return "Not recorded";
    }

    return formatDateTime(value);
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

function setActiveSectionNavLink(sectionId) {
    const links = document.querySelectorAll("[data-section-nav-link]");

    links.forEach((link) => {
        const isActive = link.dataset.sectionNavLink === sectionId;

        link.classList.toggle("is-active", isActive);

        if (isActive) {
            link.setAttribute("aria-current", "page");
        } else {
            link.removeAttribute("aria-current");
        }
    });
}

function initializeSectionNavigation() {
    const links = document.querySelectorAll("[data-section-nav-link]");
    const sections = document.querySelectorAll("[data-dashboard-section]");

    if (links.length === 0 || sections.length === 0) {
        return;
    }

    links.forEach((link) => {
        link.addEventListener("click", () => {
            setActiveSectionNavLink(link.dataset.sectionNavLink);
        });
    });

    if (!("IntersectionObserver" in window)) {
        setActiveSectionNavLink(sections[0].id);
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        const activeEntry = entries
            .filter((entry) => entry.isIntersecting)
            .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];

        if (activeEntry) {
            setActiveSectionNavLink(activeEntry.target.id);
        }
    }, {
        rootMargin: "-25% 0px -60% 0px",
        threshold: [0.1, 0.25, 0.5],
    });

    sections.forEach((section) => observer.observe(section));
}

function bindEvents() {
    elements.teamSearch.addEventListener("input", (event) => {
        state.filters.team = event.target.value;
        scheduleFilterApply();
    });

    elements.groupFilter.addEventListener("change", (event) => {
        state.filters.group = event.target.value;
        syncFixtureScopeFromGroupFilter();
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
        state.fixtureStatusScope = "completed";
        state.fixtureScope = "all";

        elements.teamSearch.value = "";
        elements.groupFilter.value = "";
        elements.statusFilter.value = "";

        applyFilters();
    });

    elements.generateAiSummary.addEventListener("click", generateAiSummary);
    elements.refreshSyncStatus.addEventListener("click", refreshFixtureSyncStatus);
    elements.refreshAiInsights.addEventListener("click", refreshAiInsights);

    if (elements.fixtureStatusTabs) {
        elements.fixtureStatusTabs.addEventListener("click", (event) => {
            const tab = event.target.closest("[data-fixture-status-scope]");

            if (!tab || tab.disabled) {
                return;
            }

            setFixtureStatusScope(tab.dataset.fixtureStatusScope);
        });
    }

    if (elements.fixtureGroupTabs) {
        elements.fixtureGroupTabs.addEventListener("click", (event) => {
            const tab = event.target.closest("[data-fixture-scope]");

            if (!tab) {
                return;
            }

            setFixtureScope(tab.dataset.fixtureScope);
        });
    }

    elements.fixturesContainer.addEventListener("click", (event) => {
        const button = event.target.closest("[data-fixture-summary-id]");

        if (button) {
            event.stopPropagation();
            const fixtureId = button.dataset.fixtureSummaryId;
            generateSingleFixtureSummary(fixtureId, button);
            return;
        }

        const fixtureCard = event.target.closest("[data-fixture-card-id]");

        if (!fixtureCard) {
            return;
        }

        selectFixture(fixtureCard.dataset.fixtureCardId, {
            scroll: window.matchMedia("(max-width: 900px)").matches,
        });
    });

    elements.fixturesContainer.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
            return;
        }

        const fixtureCard = event.target.closest("[data-fixture-card-id]");

        if (!fixtureCard) {
            return;
        }

        event.preventDefault();
        selectFixture(fixtureCard.dataset.fixtureCardId, {
            scroll: window.matchMedia("(max-width: 900px)").matches,
        });
    });

    if (elements.matchDetailPanel) {
        elements.matchDetailPanel.addEventListener("click", (event) => {
            const tab = event.target.closest("[data-match-detail-tab]");

            if (!tab || !state.selectedFixture) {
                return;
            }

            state.activeMatchDetailTab = tab.dataset.matchDetailTab;
            renderFixtureDetail(
                state.selectedFixture,
                state.selectedFixtureDetail,
                { scroll: false },
            );
        });
    }
}

async function initializeDashboard() {
    initializeSectionNavigation();
    bindEvents();
    setLoadingState();
    checkAiHealth();
    refreshFixtureSyncStatus();
    void refreshLatestCompletedSummary();
    void refreshProviderLeaders();

    try {
        const [fixtures, standings, insights, aiInsights] = await Promise.all([
            fetchFixtures(),
            fetchStandings(),
            fetchInsights(),
            fetchAiInsights(),
        ]);

        state.allFixtures = fixtures;
        state.standings = standings;
        state.insights = insights;
        state.aiInsights = aiInsights;

        populateFilters(state.allFixtures);
        renderInsights(state.insights);
        renderAiInsights(state.aiInsights);
        renderStandings(state.standings);
        renderFixtureBrowser(state.allFixtures, { selectFirst: true });
    } catch (error) {
        console.error(error);
        elements.dashboardMessage.textContent = "Unable to load fixtures.";
        if (elements.fixtureBrowserMessage) {
            elements.fixtureBrowserMessage.textContent = "The fixture browser could not load match data.";
        }
        elements.fixturesContainer.innerHTML = `
            <div class="empty-state">
                The dashboard could not load fixture data. Please check that the API server is running.
            </div>
        `;
        setAiInsightsError("Unable to load structured AI insights.");
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
        setProviderLeadersError();
    }
}

document.addEventListener("DOMContentLoaded", initializeDashboard);
