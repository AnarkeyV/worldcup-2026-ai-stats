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
    matchDataQuality: null,
    matchdayFixtures: [],
    aiAvailable: false,
    fixtureStatusScope: "completed",
    fixtureScope: "all",
    fixtureBrowserFixtures: [],
    selectedFixture: null,
    selectedFixtureDetail: null,
    selectedFixtureStory: null,
    selectedFixtureDetailError: false,
    selectedFixtureStoryError: false,
    selectedFixtureId: null,
    activeMatchDetailTab: "story",
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
    syncFreshnessContext: document.querySelector("#sync-freshness-context"),
    syncFreshnessSchedule: document.querySelector("#sync-freshness-schedule"),
    syncSchedulerMode: document.querySelector("#sync-scheduler-mode"),
    syncAlertPolicy: document.querySelector("#sync-alert-policy"),
    syncErrorMessage: document.querySelector("#sync-error-message"),
    matchDataQualityMessage: document.querySelector("#match-data-quality-message"),
    refreshMatchDataQuality: document.querySelector("#refresh-match-data-quality"),
    matchDataQualitySummary: document.querySelector("#match-data-quality-summary"),
    matchDataQualityEvents: document.querySelector("#match-data-quality-events"),
    missingDetailFixtures: document.querySelector("#missing-detail-fixtures"),
    matchdayHomeContent: document.querySelector("#matchday-home-content"),
    matchdayHomeMessage: document.querySelector("#matchday-home-message"),
    dataHealthBadge: document.querySelector("#data-health-badge"),
    mobileBottomNav: document.querySelector("#mobile-bottom-nav"),
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



function buildMatchDataQualityQueryString(filters = {}) {
    const params = new URLSearchParams();

    if (filters.group) {
        params.set("group_name", filters.group);
    }

    if (filters.team && filters.team.trim()) {
        params.set("team", filters.team.trim());
    }

    const queryString = params.toString();

    return queryString ? `?${queryString}` : "";
}

async function fetchMatchDataQuality(filters = {}) {
    const queryString = buildMatchDataQualityQueryString(filters);
    const possibleEndpoints = [
        `/api/fixtures/data-quality${queryString}`,
        `/fixtures/data-quality${queryString}`,
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            return await response.json();
        } catch (error) {
            console.warn(`Unable to fetch match data quality from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load stored match-detail coverage.");
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




function getDataHealthPresentation() {
    const summary = state.matchDataQuality?.summary || {};
    const coverage = Number(summary.coverage_percent);
    const stateName = summary.state || "unavailable";

    if (!Number.isFinite(coverage)) {
        return {
            className: "unavailable",
            value: "Unavailable",
            detail: "Stored match data",
        };
    }

    return {
        className: stateName,
        value: `${coverage.toFixed(1)}%`,
        detail: "Stored match data",
    };
}

function getMatchdayHeroFixtures(fixtures = []) {
    const safeFixtures = Array.isArray(fixtures) ? fixtures : [];
    const sortedByNewest = [...safeFixtures].sort((left, right) =>
        new Date(right?.kickoff_time || 0) - new Date(left?.kickoff_time || 0)
    );
    const sortedBySoonest = [...safeFixtures].sort((left, right) =>
        new Date(left?.kickoff_time || 0) - new Date(right?.kickoff_time || 0)
    );

    return {
        live: sortedByNewest.find((fixture) => getFixtureStatusCategory(fixture) === "live") || null,
        latestCompleted: sortedByNewest.find((fixture) => getFixtureStatusCategory(fixture) === "completed") || null,
        nextUpcoming: sortedBySoonest.find((fixture) => getFixtureStatusCategory(fixture) === "scheduled") || null,
    };
}

function renderMatchdayScoreCard(fixture, label, tone) {
    if (!fixture) {
        return "";
    }

    const matchLabel = `${fixture.home_team || "Home team"} vs ${fixture.away_team || "Away team"}`;
    const scoreLine = `${formatScore(fixture.home_score)} – ${formatScore(fixture.away_score)}`;
    const statusPresentation = getFixtureStatusPresentation(fixture);
    const timeLabel = statusPresentation.matchState === "scheduled"
        ? formatDateTime(fixture.kickoff_time)
        : formatStatus(fixture.status);
    const statusDetail = statusPresentation.detail
        ? ` · ${statusPresentation.detail}`
        : "";

    return `
        <button
            class="matchday-score-card ${escapeHtml(tone)}"
            type="button"
            data-matchday-fixture-id="${escapeHtml(fixture.id)}"
            aria-label="Open match detail for ${escapeHtml(matchLabel)}"
        >
            <span class="matchday-card-label">${escapeHtml(label)}</span>
            <span class="matchday-card-context">${escapeHtml(fixture.group_name || fixture.stage || "World Cup 2026")}</span>
            <span class="matchday-card-teams">
                <strong>${escapeHtml(fixture.home_team || "Home team")}</strong>
                <strong>${escapeHtml(fixture.away_team || "Away team")}</strong>
            </span>
            <strong class="matchday-card-score">${escapeHtml(scoreLine)}</strong>
            <span class="matchday-card-meta">${escapeHtml(`${timeLabel}${statusDetail}`)}</span>
            <span class="matchday-card-action">Open match</span>
        </button>
    `;
}

function renderMatchdayHome(fixtures = state.matchdayFixtures) {
    if (
        !elements.matchdayHomeContent
        || !elements.matchdayHomeMessage
        || !elements.dataHealthBadge
    ) {
        return;
    }

    const safeFixtures = Array.isArray(fixtures) ? fixtures : [];
    const health = getDataHealthPresentation();
    const heroes = getMatchdayHeroFixtures(safeFixtures);
    const cards = [
        heroes.live ? renderMatchdayScoreCard(heroes.live, "Live now", "live") : "",
        renderMatchdayScoreCard(heroes.latestCompleted, "Latest result", "completed"),
        renderMatchdayScoreCard(heroes.nextUpcoming, "Next up", "upcoming"),
    ].filter(Boolean);

    elements.dataHealthBadge.className = `data-health-badge ${health.className}`;
    elements.dataHealthBadge.innerHTML = `
        <span>Data health</span>
        <strong>${escapeHtml(health.value)}</strong>
        <small>${escapeHtml(health.detail)}</small>
    `;

    if (safeFixtures.length === 0 || cards.length === 0) {
        elements.matchdayHomeMessage.textContent =
            "No fixtures are available in the current view yet.";
        elements.matchdayHomeContent.innerHTML = `
            <div class="matchday-home-empty">
                Matchday cards will appear as stored fixture data becomes available.
            </div>
        `;
        return;
    }

    const liveMessage = heroes.live
        ? "A live match is available."
        : "Latest result and next fixture are ready.";
    elements.matchdayHomeMessage.textContent = `${liveMessage} ${safeFixtures.length} fixture${safeFixtures.length === 1 ? "" : "s"} in this view.`;
    elements.matchdayHomeContent.innerHTML = cards.join("");
}

async function refreshMatchDataQuality(filters = state.filters) {
    setMatchDataQualityLoading();

    try {
        const data = await fetchMatchDataQuality(filters);

        state.matchDataQuality = data;
        renderMatchDataQuality(data);
        renderMatchdayHome();
    } catch (error) {
        console.error(error);
        setMatchDataQualityError();
        renderMatchdayHome();
    }
}

function setMatchDataQualityLoading() {
    if (
        !elements.matchDataQualityMessage
        || !elements.matchDataQualitySummary
        || !elements.matchDataQualityEvents
        || !elements.missingDetailFixtures
    ) {
        return;
    }

    elements.matchDataQualityMessage.textContent =
        "Checking stored match-detail coverage for completed fixtures.";
    elements.matchDataQualitySummary.innerHTML = `
        <div class="match-data-quality-loading">
            Checking local stored match detail. No provider request was made by this panel.
        </div>
    `;
    elements.matchDataQualityEvents.innerHTML = "";
    elements.missingDetailFixtures.innerHTML = `
        <p>
            Completed fixtures without stored detail will appear here.
            No provider request was made by this panel.
        </p>
    `;
}

function setMatchDataQualityError() {
    if (
        !elements.matchDataQualityMessage
        || !elements.matchDataQualitySummary
        || !elements.matchDataQualityEvents
        || !elements.missingDetailFixtures
    ) {
        return;
    }

    elements.matchDataQualityMessage.textContent =
        "Stored match-detail coverage could not be loaded.";
    elements.matchDataQualitySummary.innerHTML = `
        <article class="match-data-quality-card">
            <span>Stored match-detail coverage</span>
            <strong>Unavailable</strong>
            <small>No provider request was made by this panel.</small>
        </article>
    `;
    elements.matchDataQualityEvents.innerHTML = "";
    elements.missingDetailFixtures.innerHTML = `
        <p>
            Missing-detail fixtures are unavailable until the local coverage response can be read.
            No provider request was made by this panel.
        </p>
    `;
}

function formatCoveragePercent(value) {
    if (value === null || value === undefined) {
        return "Not available";
    }

    const percentage = Number(value);

    return Number.isFinite(percentage)
        ? `${percentage.toFixed(1)}%`
        : "Not available";
}

function formatMatchDataQualityState(value) {
    const labels = {
        complete: "Complete",
        partial: "Partial",
        unavailable: "Unavailable",
    };

    return labels[value] || "Unavailable";
}

function renderMatchDataQuality(data) {
    if (
        !elements.matchDataQualityMessage
        || !elements.matchDataQualitySummary
        || !elements.matchDataQualityEvents
        || !elements.missingDetailFixtures
    ) {
        return;
    }

    const summary = data?.summary || {};
    const eventCoverage = data?.event_coverage || {};
    const missingFixtures = Array.isArray(data?.missing_detail_fixtures)
        ? data.missing_detail_fixtures
        : [];
    const missingCount = formatNumber(data?.missing_detail_fixture_count);
    const missingLimit = formatNumber(data?.missing_detail_limit);
    const state = summary.state || "unavailable";
    const message = data?.message || "Stored match-detail coverage is unavailable.";

    elements.matchDataQualityMessage.textContent =
        `${message} No provider request was made by this panel.`;

    elements.matchDataQualitySummary.innerHTML = `
        <article class="match-data-quality-card match-data-quality-coverage-card">
            <div class="match-data-quality-coverage-row">
                <div>
                    <span>Stored match-detail coverage</span>
                    <strong>${escapeHtml(formatCoveragePercent(summary.coverage_percent))}</strong>
                </div>
                <span
                    class="match-data-quality-donut"
                    style="--coverage: ${Math.max(0, Math.min(100, Number(summary.coverage_percent) || 0))}%;"
                    aria-label="${escapeHtml(formatCoveragePercent(summary.coverage_percent))} stored match-detail coverage"
                >
                    <span>${escapeHtml(formatCoveragePercent(summary.coverage_percent))}</span>
                </span>
            </div>
            <small>
                ${escapeHtml(`${formatNumber(summary.fixtures_with_stored_detail)} of ${formatNumber(summary.completed_fixture_count)} completed fixtures with stored detail`)}
            </small>
        </article>
        <article class="match-data-quality-card">
            <span>Coverage state</span>
            <strong><span class="match-data-quality-state ${escapeHtml(state)}">${escapeHtml(formatMatchDataQualityState(state))}</span></strong>
            <small>${escapeHtml(`${formatNumber(summary.scope_fixture_count)} fixtures in the current group/team scope`)}</small>
        </article>
        <article class="match-data-quality-card">
            <span>Missing detail</span>
            <strong>${escapeHtml(formatNumber(summary.fixtures_without_stored_detail))}</strong>
            <small>Completed fixtures without a locally stored provider detail payload.</small>
        </article>
        <article class="match-data-quality-card">
            <span>Latest stored refresh</span>
            <strong>${escapeHtml(formatStoredDetailRefresh(summary.latest_stored_detail_updated_at))}</strong>
            <small>Latest local detail timestamp, not a live provider request.</small>
        </article>
    `;

    const eventTypes = [
        ["Goals", eventCoverage.goals || {}],
        ["Cards", eventCoverage.cards || {}],
        ["Substitutions", eventCoverage.substitutions || {}],
    ];

    elements.matchDataQualityEvents.innerHTML = eventTypes.map(([label, coverage]) => `
        <article class="match-data-quality-event-card">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(`${formatNumber(coverage.total_stored_events)} stored`)}</strong>
            <div class="match-data-quality-event-stats">
                <span>${escapeHtml(`${formatNumber(coverage.fixtures_with_recorded_events)} fixture(s) with recorded events`)}</span>
                <span>${escapeHtml(`${formatNumber(coverage.fixtures_with_no_stored_events)} detailed fixture(s) with no stored events`)}</span>
                <span>${escapeHtml(`${formatNumber(coverage.fixtures_without_stored_detail)} fixture(s) without stored detail`)}</span>
            </div>
        </article>
    `).join("");

    if (missingCount === 0) {
        elements.missingDetailFixtures.innerHTML = `
            <div class="missing-detail-fixtures-heading">
                <div>
                    <h3>Completed fixtures without stored detail</h3>
                    <p>
                        No missing stored detail is currently recorded in this scope.
                        No provider request was made by this panel.
                    </p>
                </div>
            </div>
        `;
        return;
    }

    const fixtureButtons = missingFixtures.map((fixture) => {
        const fixtureId = fixture?.id;
        const label = `${fixture?.home_team || "Home team"} vs ${fixture?.away_team || "Away team"}`;
        const context = [
            fixture?.group_name || fixture?.stage || "Fixture",
            formatDateTime(fixture?.kickoff_time),
        ].filter(Boolean).join(" · ");

        return `
            <button
                class="missing-detail-fixture-button"
                type="button"
                data-missing-detail-fixture-id="${escapeHtml(fixtureId)}"
            >
                <span>
                    <strong>${escapeHtml(label)}</strong>
                    <small>${escapeHtml(context)}</small>
                </span>
                <span>Open match</span>
            </button>
        `;
    }).join("");

    const omittedCount = Math.max(0, missingCount - missingFixtures.length);
    const limitNote = omittedCount > 0
        ? ` Showing ${formatNumber(missingFixtures.length)} of ${missingCount} fixtures (limit ${missingLimit}).`
        : "";

    elements.missingDetailFixtures.innerHTML = `
        <div class="missing-detail-fixtures-heading">
            <div>
                <h3>Completed fixtures without stored detail</h3>
                <p>
                    ${escapeHtml(`${missingCount} completed fixture${missingCount === 1 ? "" : "s"} need stored provider detail in this scope.${limitNote}`)}
                    No provider request was made by this panel.
                </p>
            </div>
        </div>
        <div class="missing-detail-fixture-list">
            ${fixtureButtons}
        </div>
    `;
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
    elements.syncFreshnessContext.textContent = "Freshness context unavailable";
    elements.syncFreshnessSchedule.textContent = "The dashboard could not read schedule-aware freshness context.";
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
    const freshnessContext = data.freshness_context && typeof data.freshness_context === "object"
        ? data.freshness_context
        : {};
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
    elements.syncFreshnessContext.textContent = formatFreshnessContextDiagnostic(
        freshnessContext,
        freshnessState,
    );
    elements.syncFreshnessSchedule.textContent = formatFreshnessContextSchedule(freshnessContext);
    elements.syncSchedulerMode.textContent = formatSchedulerMode(scheduler);
    elements.syncAlertPolicy.textContent = data.completed_match_alerts_enabled
        ? "Completed-match Telegram alerts are explicitly enabled."
        : "Completed-match Telegram alerts are disabled by configuration.";

    const freshnessContextMessage = formatFreshnessContextMessage(
        freshnessContext,
        freshnessState,
    );

    if (status === "not_started") {
        elements.providerSyncMessage.textContent =
            "No fixture sync has been recorded yet. Automated provider sync is disabled unless explicitly enabled in configuration.";
    } else if (status === "success") {
        elements.providerSyncMessage.textContent =
            `Last ${triggerType} ${source} sync succeeded using ${provider}: ${totalFixtures} fetched, ${created} created, ${updated} updated. ${freshnessContextMessage}`;
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
]);

const SCHEDULED_FIXTURE_STATUSES = new Set([
    "scheduled",
    "not started",
    "ns",
]);

function normalizeFixtureStatus(fixture) {
    return String(fixture?.status || "")
        .trim()
        .toLowerCase()
        .replaceAll("_", " ")
        .replaceAll("-", " ")
        .replace(/\s+/g, " ");
}

const DISPLAY_STATE_SOURCE_STORED_STATUS = "stored_status";
const DISPLAY_STATE_SOURCE_STORED_KICKOFF = "stored_kickoff";
const DISPLAY_STATE_SOURCE_UNAVAILABLE = "unavailable";

function deriveFixtureDisplayState(fixture, now = new Date()) {
    const status = normalizeFixtureStatus(fixture);

    if (LIVE_FIXTURE_STATUSES.has(status)) {
        return {
            matchState: "live",
            stateSource: DISPLAY_STATE_SOURCE_STORED_STATUS,
        };
    }

    if (COMPLETED_FIXTURE_STATUSES.has(status)) {
        return {
            matchState: "completed",
            stateSource: DISPLAY_STATE_SOURCE_STORED_STATUS,
        };
    }

    if (SCHEDULED_FIXTURE_STATUSES.has(status)) {
        return {
            matchState: "scheduled",
            stateSource: DISPLAY_STATE_SOURCE_STORED_STATUS,
        };
    }

    if (status !== "unknown") {
        return {
            matchState: "unavailable",
            stateSource: DISPLAY_STATE_SOURCE_UNAVAILABLE,
        };
    }

    const kickoff = parseStoredUtcKickoff(fixture?.kickoff_time);
    const referenceTime = normalizeReferenceTime(now);
    const hasStoredScore = fixture?.home_score !== null
        && fixture?.home_score !== undefined
        || fixture?.away_score !== null
        && fixture?.away_score !== undefined;

    if (!kickoff || !referenceTime || kickoff <= referenceTime || hasStoredScore) {
        return {
            matchState: "unavailable",
            stateSource: DISPLAY_STATE_SOURCE_UNAVAILABLE,
        };
    }

    return {
        matchState: "scheduled",
        stateSource: DISPLAY_STATE_SOURCE_STORED_KICKOFF,
    };
}

function parseStoredUtcKickoff(value) {
    if (typeof value !== "string") {
        return null;
    }

    const candidate = value.trim();
    if (!candidate || !/(?:Z|[+-]\d{2}:\d{2})$/i.test(candidate)) {
        return null;
    }

    const parsed = new Date(candidate);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function normalizeReferenceTime(value) {
    const parsed = value instanceof Date
        ? new Date(value.getTime())
        : new Date(value);

    return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function getFixtureStatusCategory(fixture) {
    return deriveFixtureDisplayState(fixture).matchState;
}

function getFixtureStatusPresentation(fixture) {
    const displayState = deriveFixtureDisplayState(fixture);

    if (displayState.stateSource === DISPLAY_STATE_SOURCE_STORED_KICKOFF) {
        return {
            ...displayState,
            label: "Scheduled from stored kickoff",
            detail: "Provider match status unavailable",
        };
    }

    return {
        ...displayState,
        label: formatStatus(fixture?.status),
        detail: "",
    };
}

function getFixtureStatusCounts(fixtures) {
    return fixtures.reduce((counts, fixture) => {
        counts[getFixtureStatusCategory(fixture)] += 1;
        return counts;
    }, {
        completed: 0,
        live: 0,
        scheduled: 0,
        unavailable: 0,
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

    return ["completed", "live", "scheduled", "unavailable"].filter((scope) => counts[scope] > 0);
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
            description: "Matches explicitly stored as live",
        },
        {
            scope: "scheduled",
            label: "Upcoming",
            description: "Provider status or future stored kickoff",
        },
        ...(counts.unavailable > 0 ? [{
            scope: "unavailable",
            label: "Data unavailable",
            description: "Unknown or unsupported stored status",
        }] : []),
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

    const label = state.fixtureStatusScope === "scheduled"
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
    elements.scheduledFixtures.textContent = statusCounts.scheduled;
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

        state.matchdayFixtures = fixtures;
        state.standings = standings;
        state.insights = insights;
        state.aiInsights = aiInsights;

        renderMatchdayHome(state.matchdayFixtures);
        renderInsights(state.insights);
        renderAiInsights(state.aiInsights);
        void refreshProviderLeaders(state.filters);
        void refreshMatchDataQuality(state.filters);
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
        const leaderPoints = Math.max(
            1,
            ...teams.map((team) => Math.max(0, Number(team?.points) || 0)),
        );

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
                                <span class="group-race-points-track" aria-hidden="true">
                                    <span
                                        class="group-race-points-fill"
                                        style="width: ${Math.max(0, Math.min(100, ((Number(team.points) || 0) / leaderPoints) * 100)).toFixed(2)}%"
                                    ></span>
                                </span>
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

    const leaderMetric = Math.max(
        1,
        ...players.map((player) => Math.max(0, Number(player?.[metricKey]) || 0)),
    );

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
                            <span class="player-leader-bar" aria-hidden="true">
                                <span
                                    class="player-leader-bar-fill"
                                    style="width: ${Math.max(0, Math.min(100, ((Number(player?.[metricKey]) || 0) / leaderMetric) * 100)).toFixed(2)}%"
                                ></span>
                            </span>
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
    const statusPresentation = getFixtureStatusPresentation(fixture);

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
                <span
                    class="status-pill ${getStatusClass(fixture)}"
                    title="${escapeHtml(statusPresentation.detail || statusPresentation.label)}"
                    aria-label="${escapeHtml([statusPresentation.label, statusPresentation.detail].filter(Boolean).join(". "))}"
                >
                    ${escapeHtml(statusPresentation.label)}
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

    const activeLabel = state.fixtureStatusScope === "scheduled"
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

async function fetchFixtureStory(fixtureId) {
    const possibleEndpoints = [
        `/api/fixtures/${fixtureId}/story`,
        `/fixtures/${fixtureId}/story`,
    ];

    for (const endpoint of possibleEndpoints) {
        try {
            const response = await fetch(endpoint);

            if (!response.ok) {
                continue;
            }

            return await response.json();
        } catch (error) {
            console.warn(`Unable to fetch stored match story from ${endpoint}`, error);
        }
    }

    throw new Error("Unable to load stored match story.");
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
        { id: "story", label: "Story" },
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

function formatStoryStatistic(metric, value) {
    if (metric?.unit === "percent") {
        return `${value}%`;
    }

    if (metric?.unit === "decimal") {
        const numericValue = Number(value);
        return Number.isFinite(numericValue) ? numericValue.toFixed(2) : String(value);
    }

    return String(value);
}

function getStoryStatisticShare(homeValue, awayValue) {
    const total = Number(homeValue) + Number(awayValue);

    if (!Number.isFinite(total) || total <= 0) {
        return null;
    }

    return Math.max(0, Math.min(100, (Number(homeValue) / total) * 100));
}

function renderStoryStatisticComparison(metric) {
    const homeValue = metric?.home;
    const awayValue = metric?.away;
    const homeShare = getStoryStatisticShare(homeValue, awayValue);

    return `
        <article class="stat-comparison-row story-stat-comparison-row">
            <div class="stat-comparison-values">
                <strong>${escapeHtml(formatStoryStatistic(metric, homeValue))}</strong>
                <span>${escapeHtml(metric?.label || "Statistic")}</span>
                <strong>${escapeHtml(formatStoryStatistic(metric, awayValue))}</strong>
            </div>
            ${homeShare === null ? `
                <p class="story-stat-zero-note">Both teams recorded 0 for this provider metric.</p>
            ` : `
                <div class="stat-comparison-track" aria-label="${escapeHtml(metric?.label || "Statistic")} comparison">
                    <span class="stat-comparison-home" style="width: ${homeShare.toFixed(2)}%"></span>
                    <span class="stat-comparison-away" style="width: ${(100 - homeShare).toFixed(2)}%"></span>
                </div>
            `}
        </article>
    `;
}

function getStoryMetrics(story, limit = null) {
    const metrics = Array.isArray(story?.statistics?.metrics)
        ? story.statistics.metrics.filter((metric) => (
            metric
            && typeof metric.key === "string"
            && metric.home !== null
            && metric.home !== undefined
            && metric.away !== null
            && metric.away !== undefined
        ))
        : [];

    const priority = [
        "possessionPct",
        "shotsTotal",
        "shotsOnGoal",
        "expectedGoals",
        "corners",
        "passesAccurate",
        "fouls",
    ];

    const sortedMetrics = [...metrics].sort((left, right) => {
        const leftIndex = priority.indexOf(left.key);
        const rightIndex = priority.indexOf(right.key);
        const leftRank = leftIndex === -1 ? priority.length : leftIndex;
        const rightRank = rightIndex === -1 ? priority.length : rightIndex;

        return leftRank - rightRank;
    });

    return Number.isInteger(limit) ? sortedMetrics.slice(0, limit) : sortedMetrics;
}

function renderStoryUnavailable(title, reason) {
    return `
        <section class="match-story-section match-story-section-unavailable">
            <div class="match-story-section-heading">
                <h4>${escapeHtml(title)}</h4>
                <span class="match-story-state unavailable">Unavailable</span>
            </div>
            <p>${escapeHtml(reason || "Provider-backed data is not available for this part of the match story.")}</p>
        </section>
    `;
}

function renderScoreProgression(fixture, scoreProgression) {
    if (scoreProgression?.state !== "available") {
        return renderStoryUnavailable("Score progression", scoreProgression?.reason);
    }

    const events = Array.isArray(scoreProgression.events)
        ? scoreProgression.events
        : [];

    if (events.length === 0) {
        return renderStoryUnavailable(
            "Score progression",
            "No reconciled stored goal events are available for this fixture."
        );
    }

    return `
        <section class="match-story-section score-progression-section">
            <div class="match-story-section-heading">
                <div>
                    <span class="match-story-eyebrow">Provider-backed</span>
                    <h4>Score progression</h4>
                </div>
                <span class="match-story-state available">Reconciled</span>
            </div>
            <div class="score-progression" aria-label="Score progression">
                <div class="score-progression-start">
                    <strong>0–0</strong>
                    <span>Kick-off</span>
                </div>
                ${events.map((event) => {
                    const team = getTeamNameFromSide(event.team, fixture);
                    const scoreline = `${event.home_score}–${event.away_score}`;

                    return `
                        <article class="score-progression-step ${escapeHtml(event.team || "unknown")}">
                            <span class="score-progression-minute">${escapeHtml(formatDetailMinute(event.minute))}</span>
                            <div>
                                <strong>${escapeHtml(scoreline)}</strong>
                                <p>${escapeHtml(team)} · ${escapeHtml(event.scorer || "Scorer not supplied")}</p>
                            </div>
                        </article>
                    `;
                }).join("")}
            </div>
        </section>
    `;
}

function getStoryTimelineEventPresentation(event, fixture) {
    const team = getTeamNameFromSide(event?.team, fixture);

    if (event?.kind === "goal") {
        return {
            className: "goal",
            title: "Goal",
            actor: event.scorer || "Scorer not supplied",
            team,
        };
    }

    if (event?.kind === "card") {
        const redCard = String(event.color || "").includes("red")
            || String(event.color || "").includes("second");

        return {
            className: redCard ? "red-card" : "yellow-card",
            title: redCard ? "Red card" : "Yellow card",
            actor: event.player || "Player not supplied",
            team,
        };
    }

    return {
        className: "substitution",
        title: "Substitution",
        actor: `${event?.player_on || "Player on not supplied"} for ${event?.player_off || "player off not supplied"}`,
        team,
    };
}

function renderStoryEventTimeline(fixture, timeline) {
    if (timeline?.state !== "available") {
        return renderStoryUnavailable("Key events", timeline?.reason);
    }

    const events = Array.isArray(timeline.events) ? timeline.events : [];

    if (events.length === 0) {
        return renderStoryUnavailable(
            "Key events",
            "No stored provider event timeline is available for this fixture."
        );
    }

    const keyEvents = events.slice(0, 8);
    const omittedCount = Math.max(0, events.length - keyEvents.length);

    return `
        <section class="match-story-section story-key-events-section">
            <div class="match-story-section-heading">
                <div>
                    <span class="match-story-eyebrow">Goals, cards and substitutions</span>
                    <h4>Key events</h4>
                </div>
                <span class="match-story-state available">${escapeHtml(String(events.length))} stored</span>
            </div>
            <div class="story-event-list" aria-label="Key match events">
                ${keyEvents.map((event) => {
                    const presentation = getStoryTimelineEventPresentation(event, fixture);

                    return `
                        <article class="story-event ${presentation.className}">
                            <span class="story-event-minute">${escapeHtml(formatDetailMinute(event.minute))}</span>
                            <div>
                                <strong>${escapeHtml(presentation.title)} · ${escapeHtml(presentation.actor)}</strong>
                                <p>${escapeHtml(presentation.team)}</p>
                            </div>
                        </article>
                    `;
                }).join("")}
            </div>
            ${omittedCount > 0 ? `
                <p class="match-story-more-note">${escapeHtml(String(omittedCount))} more stored event${omittedCount === 1 ? "" : "s"} in the Timeline tab.</p>
            ` : ""}
        </section>
    `;
}

function renderStoryStatistics(fixture, story, options = {}) {
    const statistics = story?.statistics || {};

    if (statistics.state === "unavailable") {
        return renderStoryUnavailable("Match edge", statistics.reason);
    }

    const metrics = getStoryMetrics(story, options.limit ?? null);

    if (metrics.length === 0) {
        return renderStoryUnavailable(
            "Match edge",
            "No comparable provider statistics are available for both teams."
        );
    }

    return `
        <section class="match-story-section story-statistics-section">
            <div class="match-story-section-heading">
                <div>
                    <span class="match-story-eyebrow">Comparable provider values only</span>
                    <h4>Match edge</h4>
                </div>
                <span class="match-story-state ${statistics.state === "partial" ? "partial" : "available"}">
                    ${statistics.state === "partial" ? "Partial" : "Available"}
                </span>
            </div>
            <div class="match-stats-heading story-match-stats-heading">
                <span>${escapeHtml(fixture.home_team || "Home")}</span>
                <strong>Match statistics</strong>
                <span>${escapeHtml(fixture.away_team || "Away")}</span>
            </div>
            <div class="match-stats-comparison">
                ${metrics.map(renderStoryStatisticComparison).join("")}
            </div>
            <p class="match-stats-note">
                ${escapeHtml(statistics.reason || "Only values supplied for both teams are visualised.")}
            </p>
        </section>
    `;
}

function formatOfficialWatchState(value) {
    const labels = {
        available: "Available",
        region_dependent: "Region dependent",
        not_available_yet: "Not available yet",
    };

    return labels[value] || "Not available yet";
}

function isSafeOfficialOutboundUrl(value) {
    try {
        const url = new URL(String(value || ""));
        return url.protocol === "https:";
    } catch (error) {
        return false;
    }
}

function renderOfficialWatchLink(link, fallback = false) {
    if (!isSafeOfficialOutboundUrl(link?.url)) {
        return "";
    }

    const contentLabel = fallback
        ? "Official coverage hub"
        : String(link.content_type || "official video").replaceAll("_", " ");

    return `
        <article class="official-watch-card ${fallback ? "is-fallback" : ""}">
            <div>
                <span class="official-watch-source">${escapeHtml(link.source_name || "Official source")}</span>
                <h5>${escapeHtml(link.title || "Official match video")}</h5>
                <p>${escapeHtml(contentLabel)} · ${escapeHtml(link.territory || "Availability may vary")}</p>
                ${link.territory_note ? `<small>${escapeHtml(link.territory_note)}</small>` : ""}
            </div>
            <a
                class="official-watch-link"
                href="${escapeHtml(link.url)}"
                target="_blank"
                rel="noopener noreferrer"
            >
                Open official source <span aria-hidden="true">↗</span>
            </a>
        </article>
    `;
}

function renderOfficialWatch(story, options = {}) {
    if (options.isLoading) {
        return `
            <section class="official-watch official-watch-loading">
                <div class="official-watch-heading">
                    <div>
                        <span class="match-story-eyebrow">Trusted outbound links only</span>
                        <h4>Official Highlights / Watch</h4>
                    </div>
                    <span class="official-watch-status">Checking</span>
                </div>
                <p>Loading the local official-watch record. No video-site search is performed.</p>
            </section>
        `;
    }

    const watch = story?.official_watch;

    if (!watch || options.error) {
        return `
            <section class="official-watch official-watch-unavailable">
                <div class="official-watch-heading">
                    <div>
                        <span class="match-story-eyebrow">Trusted outbound links only</span>
                        <h4>Official Highlights / Watch</h4>
                    </div>
                    <span class="official-watch-status">Unavailable</span>
                </div>
                <p>The local official-watch record could not be loaded. No third-party search, scrape, or embed is used.</p>
            </section>
        `;
    }

    const links = Array.isArray(watch.links) ? watch.links : [];
    const fallbackLinks = Array.isArray(watch.fallback_links) ? watch.fallback_links : [];
    const renderedLinks = links.map((link) => renderOfficialWatchLink(link)).filter(Boolean).join("");
    const renderedFallbackLinks = fallbackLinks
        .map((link) => renderOfficialWatchLink(link, true))
        .filter(Boolean)
        .join("");

    return `
        <section class="official-watch ${watch.state === "available" ? "is-available" : ""}">
            <div class="official-watch-heading">
                <div>
                    <span class="match-story-eyebrow">Trusted outbound links only</span>
                    <h4>Official Highlights / Watch</h4>
                </div>
                <span class="official-watch-status ${escapeHtml(watch.state || "not_available_yet")}">
                    ${escapeHtml(formatOfficialWatchState(watch.state))}
                </span>
            </div>
            <p>${escapeHtml(watch.message || watch.reason || "Official video availability may be delayed or region-dependent.")}</p>
            ${renderedLinks ? `
                <div class="official-watch-links">
                    ${renderedLinks}
                </div>
            ` : ""}
            ${!renderedLinks && renderedFallbackLinks ? `
                <div class="official-watch-hubs">
                    <span>Official coverage hubs</span>
                    <div class="official-watch-links">
                        ${renderedFallbackLinks}
                    </div>
                </div>
            ` : ""}
            <small class="official-watch-disclosure">
                Links open in a new tab. Availability may vary by territory. No video is embedded, downloaded, or rehosted here.
            </small>
        </section>
    `;
}

function renderStoryProvenance(story) {
    const source = story?.source || {};
    const provider = source.provider || "Provider not supplied";
    const refresh = formatStoredDetailRefresh(source.stored_detail_updated_at);

    return `
        <div class="story-provenance">
            <span><strong>Provider:</strong> ${escapeHtml(provider)}</span>
            <span><strong>Stored detail refresh:</strong> ${escapeHtml(refresh)}</span>
            <small>Stored provider payload; not a live detail request.</small>
        </div>
    `;
}

function renderMatchStoryTab(fixture, story, options = {}) {
    const savedSummary = state.fixtureSummaries[fixture.id];

    if (options.isLoading) {
        return `
            <div class="match-detail-loading">
                Loading the locally stored match story, provider event timeline, and official-watch record...
            </div>
        `;
    }

    if (!story) {
        return `
            <div class="match-detail-note ${options.error ? "error" : ""}">
                <strong>Match story status:</strong>
                ${escapeHtml(options.error
                    ? "The stored match story could not be loaded right now."
                    : "No stored match story is available for this fixture yet.")}
            </div>
            ${renderOfficialWatch(null, { error: options.error })}
        `;
    }

    return `
        <div class="match-story-grid">
            ${renderScoreProgression(fixture, story.score_progression)}
            ${renderStoryEventTimeline(fixture, story.timeline)}
        </div>
        ${renderStoryStatistics(fixture, story, { limit: 4 })}
        ${renderOfficialWatch(story)}
        ${renderStoryProvenance(story)}
        ${savedSummary ? `
            <div class="match-detail-context match-story-ai-summary">
                <h4>AI match summary</h4>
                <p>${escapeHtml(savedSummary)}</p>
            </div>
        ` : ""}
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

function renderMatchStatsTab(fixture, story) {
    if (!story) {
        return `
            <div class="match-detail-empty">
                Comparable provider statistics could not be loaded for this fixture.
            </div>
        `;
    }

    return renderStoryStatistics(fixture, story);
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

function renderMatchDetailContent(fixture, detail, story, options = {}) {
    if (state.activeMatchDetailTab === "timeline") {
        return renderMatchTimelineTab(fixture, detail);
    }

    if (state.activeMatchDetailTab === "stats") {
        return renderMatchStatsTab(fixture, story);
    }

    if (state.activeMatchDetailTab === "lineups") {
        return renderMatchLineupsTab(fixture, detail);
    }

    return renderMatchStoryTab(fixture, story, options);
}

function renderFixtureDetail(fixture, detail = null, story = null, options = {}) {
    const matchDetail = getMatchDetailElements();

    if (!matchDetail.panel || !matchDetail.title || !matchDetail.status || !matchDetail.detail) {
        return;
    }

    const homeTeam = fixture.home_team || "Home team";
    const awayTeam = fixture.away_team || "Away team";
    const statusPresentation = getFixtureStatusPresentation(fixture);

    matchDetail.title.textContent = `${homeTeam} vs ${awayTeam}`;
    matchDetail.status.className = `status-pill ${getStatusClass(fixture)}`;
    matchDetail.status.textContent = statusPresentation.label;
    matchDetail.status.setAttribute(
        "aria-label",
        [statusPresentation.label, statusPresentation.detail].filter(Boolean).join(". ")
    );
    if (statusPresentation.detail) {
        matchDetail.status.setAttribute("title", statusPresentation.detail);
    } else {
        matchDetail.status.removeAttribute("title");
    }

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
            ${statusPresentation.detail ? `
                <div>
                    <span>Status source</span>
                    <strong>${escapeHtml(statusPresentation.detail)}</strong>
                </div>
            ` : ""}
        </div>

        ${renderMatchDetailTabs()}

        <div class="match-detail-tab-panel" role="tabpanel">
            ${renderMatchDetailContent(fixture, detail, story, options)}
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
    state.selectedFixtureStory = null;
    state.selectedFixtureDetailError = false;
    state.selectedFixtureStoryError = false;
    state.activeMatchDetailTab = "story";
    syncSelectedFixtureCard();

    renderFixtureDetail(fixtureFromState, null, null, {
        isLoading: true,
        scroll: options.scroll === true,
    });

    const [detailResult, storyResult] = await Promise.allSettled([
        fetchFixtureDetail(fixtureId),
        fetchFixtureStory(fixtureId),
    ]);

    if (String(state.selectedFixtureId) !== String(fixtureId)) {
        return;
    }

    const detailPayload = detailResult.status === "fulfilled" ? detailResult.value : null;
    const storyPayload = storyResult.status === "fulfilled" ? storyResult.value : null;
    const fixture = detailPayload?.fixture || storyPayload?.fixture || fixtureFromState;
    const detail = detailPayload?.detail_available ? detailPayload.detail : null;
    const story = storyPayload?.story || null;

    if (detailResult.status === "rejected") {
        console.error(detailResult.reason);
    }

    if (storyResult.status === "rejected") {
        console.error(storyResult.reason);
    }

    state.selectedFixture = fixture;
    state.selectedFixtureDetail = detail;
    state.selectedFixtureStory = story;
    state.selectedFixtureDetailError = detailResult.status === "rejected";
    state.selectedFixtureStoryError = storyResult.status === "rejected";

    renderFixtureDetail(fixture, detail, story, {
        detailError: state.selectedFixtureDetailError,
        error: state.selectedFixtureStoryError,
    });
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
                state.selectedFixtureStory,
                { error: state.selectedFixtureStoryError, scroll: false },
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

function getStatusClass(fixture) {
    const category = getFixtureStatusCategory(fixture);

    if (category === "completed") {
        return "status-complete";
    }

    if (category === "scheduled") {
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

function formatFreshnessContextMessage(context, freshnessState) {
    const message = context && typeof context.message === "string"
        ? context.message.trim()
        : "";

    if (message) {
        return message;
    }

    const fallback = {
        fresh: "The stored snapshot is within its current freshness window.",
        aging: "The stored snapshot is aging and may be delayed.",
        stale: "The latest provider refresh succeeded, but its stored snapshot is stale.",
        last_sync_failed: "The latest provider refresh failed; displayed data is from the last successful stored snapshot.",
        not_started: "No successful provider snapshot has been stored yet.",
    };

    return fallback[freshnessState] || "Stored provider freshness is unavailable.";
}

function formatFreshnessContextDiagnostic(context, freshnessState) {
    const diagnostic = context && typeof context.diagnostic === "string"
        ? context.diagnostic
        : "";

    const labels = {
        snapshot_stale_before_next_scheduled_refresh: "Stale before next refresh",
        snapshot_will_be_stale_before_next_scheduled_refresh: "Will be stale before next refresh",
        latest_sync_failed: "Latest refresh failed",
        no_successful_snapshot: "No successful snapshot",
        last_success_timestamp_unavailable: "Last-success time unavailable",
        stale_without_next_scheduled_refresh: "Stale; next refresh unavailable",
        stale_snapshot: "Stored snapshot stale",
        no_next_scheduled_refresh: "Next refresh unavailable",
        snapshot_within_freshness_window: "Within freshness window",
    };

    return labels[diagnostic] || formatSyncFreshness(freshnessState);
}

function formatFreshnessContextSchedule(context) {
    const details = context && typeof context === "object" ? context : {};
    const timezone = String(details.schedule_timezone || "").trim();
    const timezoneLabel = formatScheduleTimezoneLabel(timezone);
    const parts = [];

    if (details.last_success_at_local || details.last_success_at) {
        parts.push(
            `Last success: ${formatFreshnessContextDateTime(
                details.last_success_at_local || details.last_success_at,
                timezone,
            )}`,
        );
    }

    if (details.next_scheduled_run_at) {
        parts.push(
            `Next scheduled: ${formatFreshnessContextDateTime(
                details.next_scheduled_run_at,
                timezone,
            )}`,
        );
    }

    if (details.snapshot_becomes_stale_at_local || details.snapshot_becomes_stale_at) {
        parts.push(
            `Snapshot stale after: ${formatFreshnessContextDateTime(
                details.snapshot_becomes_stale_at_local || details.snapshot_becomes_stale_at,
                timezone,
            )}`,
        );
    }

    if (parts.length === 0) {
        return "No successful provider snapshot or next scheduled refresh is recorded.";
    }

    return `${parts.join(" · ")} (${timezoneLabel})`;
}

function formatFreshnessContextDateTime(value, timezone) {
    const parsed = new Date(value);

    if (Number.isNaN(parsed.getTime())) {
        return String(value);
    }

    try {
        return new Intl.DateTimeFormat("en-SG", {
            timeZone: timezone || "Asia/Singapore",
            year: "numeric",
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            hourCycle: "h23",
        }).format(parsed);
    } catch (error) {
        return formatDateTime(value);
    }
}

function formatScheduleTimezoneLabel(timezone) {
    if (timezone === "Asia/Singapore") {
        return "Singapore time";
    }

    return timezone || "configured schedule time";
}

function formatSchedulerMode(scheduler) {
    if (!scheduler || !scheduler.enabled) {
        return "Manual only";
    }

    const mode = String(scheduler.mode || "").trim();
    const scheduledTimes = Array.isArray(scheduler.scheduled_times)
        ? scheduler.scheduled_times
            .filter((value) => typeof value === "string" && value.trim())
            .map((value) => value.trim())
        : [];

    if (mode === "fixed_daily_times") {
        if (scheduledTimes.length === 0) {
            return "Fixed daily times";
        }

        const timezoneLabel = formatScheduleTimezoneLabel(scheduler.timezone);

        return `Fixed daily: ${scheduledTimes.join(" · ")} (${timezoneLabel})`;
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

    if (elements.refreshMatchDataQuality) {
        elements.refreshMatchDataQuality.addEventListener("click", () => {
            void refreshMatchDataQuality(state.filters);
        });
    }

    if (elements.matchdayHomeContent) {
        elements.matchdayHomeContent.addEventListener("click", (event) => {
            const card = event.target.closest("[data-matchday-fixture-id]");

            if (!card) {
                return;
            }

            selectFixture(card.dataset.matchdayFixtureId, {
                scroll: true,
            });
        });
    }

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

    if (elements.missingDetailFixtures) {
        elements.missingDetailFixtures.addEventListener("click", (event) => {
            const button = event.target.closest("[data-missing-detail-fixture-id]");

            if (!button) {
                return;
            }

            selectFixture(button.dataset.missingDetailFixtureId, {
                scroll: true,
            });
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
                state.selectedFixtureStory,
                { error: state.selectedFixtureStoryError, scroll: false },
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
    void refreshMatchDataQuality();
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
        state.matchdayFixtures = fixtures;
        state.standings = standings;
        state.insights = insights;
        state.aiInsights = aiInsights;

        renderMatchdayHome(state.matchdayFixtures);
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

window.addEventListener("live-match-centre:open-fixture", (event) => {
    const fixtureId = event?.detail?.fixtureId;
    if (fixtureId === null || fixtureId === undefined || fixtureId === "") {
        return;
    }

    selectFixture(fixtureId, { scroll: true });
});


/*
 * v1.20.0 Matchday Home & Compact Sync UX
 *
 * Presentation only: all status decisions remain based on stored fixture and
 * sync data already loaded by the dashboard. No provider request is introduced.
 */
function v120FreshnessState() {
    return String(state.fixtureSyncStatus?.freshness?.state || "checking");
}

function v120IsFreshEnoughForCurrentStoredState() {
    return ["fresh", "aging"].includes(v120FreshnessState());
}

function v120FormatTrustPresentation() {
    const sync = state.fixtureSyncStatus;

    if (!sync) {
        return {
            className: "checking",
            value: "Checking",
            detail: "Reading stored provider freshness.",
        };
    }

    const freshnessState = v120FreshnessState();
    const lastSuccess = sync.last_success_at
        ? `Last successful provider refresh: ${formatDateTime(sync.last_success_at)}.`
        : "No successful provider refresh is recorded.";

    if (freshnessState === "stale") {
        return {
            className: "stale",
            value: "Stale",
            detail: `${lastSuccess} The provider snapshot is stale; current match status is not inferred.`,
        };
    }

    if (freshnessState === "last_sync_failed") {
        return {
            className: "last-sync-failed",
            value: "Last refresh failed",
            detail: `${lastSuccess} Current match status is not inferred.`,
        };
    }

    if (freshnessState === "fresh" || freshnessState === "aging") {
        return {
            className: freshnessState,
            value: freshnessState === "fresh" ? "Fresh" : "Aging",
            detail: lastSuccess,
        };
    }

    return {
        className: "unavailable",
        value: "Unavailable",
        detail: `${lastSuccess} Current match status is not inferred.`,
    };
}

function renderMatchdayDataTrust() {
    const trust = document.querySelector("#matchday-data-trust");

    if (!trust) {
        return;
    }

    const presentation = v120FormatTrustPresentation();

    trust.className = `matchday-data-trust ${presentation.className}`;
    trust.innerHTML = `
        <span>Data trust</span>
        <strong>${escapeHtml(presentation.value)}</strong>
        <small>${escapeHtml(presentation.detail)}</small>
        <a href="#sync-runtime">View Sync details</a>
    `;
}

function v120IsFutureStoredKickoff(fixture) {
    const kickoffTime = Date.parse(fixture?.kickoff_time || "");

    return Number.isFinite(kickoffTime) && kickoffTime > Date.now();
}

getMatchdayHeroFixtures = function getMatchdayHeroFixturesV120(fixtures = []) {
    const safeFixtures = Array.isArray(fixtures) ? fixtures : [];
    const sortedByNewest = [...safeFixtures].sort(
        (left, right) => new Date(right?.kickoff_time || 0) - new Date(left?.kickoff_time || 0),
    );
    const sortedBySoonest = [...safeFixtures].sort(
        (left, right) => new Date(left?.kickoff_time || 0) - new Date(right?.kickoff_time || 0),
    );

    return {
        live: sortedByNewest.find(
            (fixture) => getFixtureStatusCategory(fixture) === "live",
        ) || null,
        latestCompleted: sortedByNewest.find(
            (fixture) => getFixtureStatusCategory(fixture) === "completed",
        ) || null,
        nextUpcoming: sortedBySoonest.find(
            (fixture) => getFixtureStatusCategory(fixture) === "scheduled",
        ) || null,
    };
};

renderMatchdayScoreCard = function renderMatchdayScoreCardV120(fixture, label, tone) {
    if (!fixture) {
        return "";
    }

    const matchLabel = `${fixture.home_team || "Home team"} vs ${fixture.away_team || "Away team"}`;
    const statusPresentation = getFixtureStatusPresentation(fixture);
    const isUpcoming = statusPresentation.matchState === "scheduled";
    const isRecordedLive = statusPresentation.matchState === "live";
    const isCurrentStoredLive = isRecordedLive && v120IsFreshEnoughForCurrentStoredState();
    const isStoredKickoffUpcoming = isUpcoming
        && statusPresentation.stateSource === DISPLAY_STATE_SOURCE_STORED_KICKOFF;
    const cardLabel = isRecordedLive
        ? (isCurrentStoredLive ? "Live in latest stored refresh" : "Last recorded live")
        : (isStoredKickoffUpcoming ? "Upcoming from stored kickoff" : label);
    const scoreLine = isUpcoming
        ? "Upcoming"
        : `${formatScore(fixture.home_score)} – ${formatScore(fixture.away_score)}`;
    const timeLabel = isUpcoming
        ? formatDateTime(fixture.kickoff_time)
        : formatStatus(fixture.status);
    const statusDetail = isRecordedLive && !isCurrentStoredLive
        ? " · Stored snapshot is stale; current status is not inferred."
        : (isStoredKickoffUpcoming
            ? " · Provider match status unavailable; shown from future stored kickoff."
            : "");

    return `
        <button
            class="matchday-score-card ${escapeHtml(tone)}"
            type="button"
            data-matchday-fixture-id="${escapeHtml(fixture.id)}"
            aria-label="Open match detail for ${escapeHtml(matchLabel)}"
        >
            <span class="matchday-card-label">${escapeHtml(cardLabel)}</span>
            <span class="matchday-card-context">${escapeHtml(fixture.group_name || fixture.stage || "World Cup 2026")}</span>
            <span class="matchday-card-teams">
                <strong>${escapeHtml(fixture.home_team || "Home team")}</strong>
                <strong>${escapeHtml(fixture.away_team || "Away team")}</strong>
            </span>
            <strong class="matchday-card-score">${escapeHtml(scoreLine)}</strong>
            <span class="matchday-card-meta">${escapeHtml(`${timeLabel}${statusDetail}`)}</span>
            <span class="matchday-card-action">Open match</span>
        </button>
    `;
};

renderMatchdayHome = function renderMatchdayHomeV120(fixtures = state.matchdayFixtures) {
    if (
        !elements.matchdayHomeContent
        || !elements.matchdayHomeMessage
        || !elements.dataHealthBadge
    ) {
        return;
    }

    const safeFixtures = Array.isArray(fixtures) ? fixtures : [];
    const health = getDataHealthPresentation();
    const heroes = getMatchdayHeroFixtures(safeFixtures);
    const cards = [
        heroes.live ? renderMatchdayScoreCard(heroes.live, "Now", "live") : "",
        renderMatchdayScoreCard(heroes.nextUpcoming, "Next", "upcoming"),
        renderMatchdayScoreCard(heroes.latestCompleted, "Latest", "completed"),
    ].filter(Boolean);

    elements.dataHealthBadge.className = `data-health-badge ${health.className}`;
    elements.dataHealthBadge.innerHTML = `
        <span>Match detail coverage</span>
        <strong>${escapeHtml(health.value)}</strong>
        <small>${escapeHtml(health.detail)}</small>
    `;
    renderMatchdayDataTrust();

    if (safeFixtures.length === 0 || cards.length === 0) {
        elements.matchdayHomeMessage.textContent =
            "No stored fixture cards are available in the current view yet.";
        elements.matchdayHomeContent.innerHTML = `
            <div class="matchday-home-empty">
                Matchday cards will appear as stored fixture data becomes available.
            </div>
        `;
        return;
    }

    const liveMessage = heroes.live
        ? (v120IsFreshEnoughForCurrentStoredState()
            ? "A fixture is marked live in the latest stored snapshot."
            : "A fixture was last recorded live, but the provider snapshot is stale.")
        : "Next stored kickoff and latest result are ready.";

    elements.matchdayHomeMessage.textContent =
        `${liveMessage} ${safeFixtures.length} fixture${safeFixtures.length === 1 ? "" : "s"} in this view.`;
    elements.matchdayHomeContent.innerHTML = cards.join("");
};

const v120RenderFixtureSyncStatus = renderFixtureSyncStatus;
renderFixtureSyncStatus = function renderFixtureSyncStatusWithMatchdayTrust(data) {
    v120RenderFixtureSyncStatus(data);
    renderMatchdayDataTrust();
};

const v120SetSyncStatusLoading = setSyncStatusLoading;
setSyncStatusLoading = function setSyncStatusLoadingWithMatchdayTrust() {
    v120SetSyncStatusLoading();
    renderMatchdayDataTrust();
};

const v120SetSyncStatusError = setSyncStatusError;
setSyncStatusError = function setSyncStatusErrorWithMatchdayTrust(message) {
    v120SetSyncStatusError(message);
    renderMatchdayDataTrust();
};

function v120CloseMoreMenuAfterNavigation(event) {
    event.currentTarget.closest("details")?.removeAttribute("open");
}

function initializeV120CompactNavigation() {
    document
        .querySelectorAll(".dashboard-more-menu a, .mobile-more-menu a")
        .forEach((link) => {
            link.addEventListener("click", v120CloseMoreMenuAfterNavigation);
        });
}

document.addEventListener("DOMContentLoaded", () => {
    initializeV120CompactNavigation();
    renderMatchdayDataTrust();
});

document.addEventListener("DOMContentLoaded", initializeDashboard);
