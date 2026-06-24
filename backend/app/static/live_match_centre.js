(() => {
    "use strict";

    const LIVE_MATCH_CENTRE_ENDPOINTS = [
        "/api/live-match-centre",
        "/live-match-centre",
    ];
    const CHANGE_LIMIT = 8;

    const elements = {
        panel: document.querySelector("#live-match-centre"),
        message: document.querySelector("#live-match-centre-message"),
        freshness: document.querySelector("#live-match-centre-freshness"),
        matches: document.querySelector("#live-match-centre-matches"),
        refresh: document.querySelector("#refresh-live-match-centre"),
        syncPanel: document.querySelector("#sync-runtime"),
    };

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function formatDateTime(value) {
        if (!value) {
            return "Not recorded";
        }

        const parsed = new Date(value);
        if (Number.isNaN(parsed.getTime())) {
            return String(value);
        }

        return parsed.toLocaleString();
    }

    function formatScore(value) {
        return Number.isFinite(Number(value)) ? String(value) : "–";
    }

    function formatStatus(value) {
        const cleaned = String(value || "").trim();
        if (!cleaned) {
            return "Unavailable";
        }

        return cleaned
            .replaceAll("_", " ")
            .replace(/\b\w/g, (letter) => letter.toUpperCase());
    }

    function formatCoverageState(value) {
        const labels = {
            available: "Available",
            not_provided: "Not provided by stored payload",
            coverage_unknown: "Coverage unknown for stored detail",
            detail_not_available: "Stored match detail unavailable",
        };
        return labels[value] || "Unavailable";
    }

    function formatFreshness(data) {
        const freshness = data && typeof data === "object" ? data : {};
        const state = String(freshness.state || "unavailable");
        const fallback = {
            fresh: "Stored provider snapshot is fresh.",
            aging: "Stored provider snapshot is aging and may be delayed.",
            stale: "Stored provider snapshot is stale and may be delayed.",
            last_sync_failed: "The latest provider refresh failed; displayed data is from the last successful stored snapshot.",
            not_started: "No successful provider snapshot has been stored yet.",
            unavailable: "Stored provider freshness is unavailable.",
        };
        return {
            state,
            message: freshness.message || fallback[state] || fallback.unavailable,
        };
    }

    async function fetchLiveMatchCentre() {
        for (const endpoint of LIVE_MATCH_CENTRE_ENDPOINTS) {
            try {
                const response = await fetch(endpoint);
                if (!response.ok) {
                    continue;
                }
                return await response.json();
            } catch (error) {
                console.warn(`Unable to load Live Match Centre from ${endpoint}`, error);
            }
        }

        throw new Error("Unable to load the stored Live Match Centre snapshot.");
    }

    function setLoadingState() {
        if (elements.message) {
            elements.message.textContent = "Reading the latest stored live-match snapshot…";
        }
        if (elements.freshness) {
            elements.freshness.className = "live-match-centre-freshness checking";
            elements.freshness.textContent = "Checking stored freshness";
        }
        if (elements.matches) {
            elements.matches.innerHTML = `
                <div class="live-match-centre-empty">
                    Reading stored live-match data. No provider request is made by this panel.
                </div>
            `;
        }
    }

    function renderEventAvailability(eventData) {
        const details = eventData && typeof eventData === "object" ? eventData : {};
        const coverage = details.event_coverage && typeof details.event_coverage === "object"
            ? details.event_coverage
            : {};
        const labels = [
            ["Goals", coverage.goals],
            ["Cards", coverage.cards],
            ["Substitutions", coverage.substitutions],
        ];
        const provider = details.provider
            ? `Stored provider detail: ${details.provider}.`
            : "No stored provider detail is available for this fixture.";
        const updated = details.stored_detail_updated_at
            ? `Last stored detail update: ${formatDateTime(details.stored_detail_updated_at)}.`
            : "No stored detail timestamp is available.";

        return `
            <div class="live-match-event-availability">
                <p>${escapeHtml(provider)} ${escapeHtml(updated)}</p>
                <ul>
                    ${labels.map(([label, value]) => `
                        <li><strong>${escapeHtml(label)}:</strong> ${escapeHtml(formatCoverageState(value))}</li>
                    `).join("")}
                </ul>
            </div>
        `;
    }

    function renderLiveMatch(match) {
        const home = match?.home_team || "Home team";
        const away = match?.away_team || "Away team";
        const fixtureId = match?.fixture_id;
        const context = match?.group_name || match?.stage || "World Cup 2026";
        const storedUpdate = match?.stored_fixture_updated_at
            ? `Last stored fixture update: ${formatDateTime(match.stored_fixture_updated_at)}.`
            : "No local fixture update timestamp is available.";
        const openButton = fixtureId === null || fixtureId === undefined
            ? ""
            : `
                <button
                    class="live-match-centre-open-button"
                    type="button"
                    data-live-match-centre-fixture-id="${escapeHtml(fixtureId)}"
                >
                    Open match
                </button>
            `;

        return `
            <article class="live-match-card">
                <div class="live-match-card-heading">
                    <div>
                        <span class="live-match-state">Live from stored status</span>
                        <h3>${escapeHtml(home)} <span>vs</span> ${escapeHtml(away)}</h3>
                        <p>${escapeHtml(context)}</p>
                    </div>
                    <span class="live-match-score" aria-label="Stored score">
                        ${escapeHtml(formatScore(match?.home_score))} – ${escapeHtml(formatScore(match?.away_score))}
                    </span>
                </div>
                <p class="live-match-meta">
                    <strong>Stored status:</strong> ${escapeHtml(formatStatus(match?.status))}
                    · ${escapeHtml(storedUpdate)}
                </p>
                ${renderEventAvailability(match?.event_data)}
                <div class="live-match-card-actions">${openButton}</div>
            </article>
        `;
    }

    function renderMatches(data) {
        const matches = Array.isArray(data?.matches) ? data.matches : [];
        const freshness = formatFreshness(data?.data_freshness);

        if (elements.freshness) {
            elements.freshness.className = `live-match-centre-freshness ${escapeHtml(freshness.state)}`;
            elements.freshness.textContent = freshness.message;
        }

        if (elements.message) {
            const count = matches.length;
            const suffix = count === 1 ? "fixture is" : "fixtures are";
            elements.message.textContent = count > 0
                ? `${count} ${suffix} explicitly marked live in the latest stored snapshot.`
                : "No fixture is marked live in the latest stored snapshot.";
        }

        if (!elements.matches) {
            return;
        }

        if (matches.length === 0) {
            elements.matches.innerHTML = `
                <div class="live-match-centre-empty">
                    No fixture is marked live in the latest stored snapshot. ${escapeHtml(freshness.message)}
                    No provider request is made by this panel.
                </div>
            `;
            return;
        }

        elements.matches.innerHTML = matches.map(renderLiveMatch).join("");
    }

    function describeChange(change) {
        const type = String(change?.type || "");
        if (type === "score_changed") {
            const before = change?.before || {};
            const after = change?.after || {};
            return `Score changed: ${formatScore(before.home)}–${formatScore(before.away)} to ${formatScore(after.home)}–${formatScore(after.away)}.`;
        }
        if (type === "status_changed") {
            return `Status changed: ${formatStatus(change?.before)} to ${formatStatus(change?.after)}.`;
        }
        if (type === "match_completed") {
            return "Match status changed to complete.";
        }
        if (type === "goal_added") {
            return "A provider-backed goal record was added.";
        }
        if (type === "card_added") {
            return "A provider-backed card record was added.";
        }
        if (type === "substitution_added") {
            return "A provider-backed substitution record was added.";
        }
        if (type === "provider_event_record_revised") {
            const eventType = String(change?.event_type || "event").replaceAll("_", " ");
            return `A provider ${eventType} record was revised.`;
        }
        return "A provider-backed match record changed.";
    }

    function flattenChanges(refresh) {
        const fixtures = Array.isArray(refresh?.changes) ? refresh.changes : [];
        return fixtures.flatMap((fixtureChange) => {
            const fixtureLabel = fixtureChange?.external_id
                ? `Fixture ${fixtureChange.external_id}`
                : "Fixture";
            const changes = Array.isArray(fixtureChange?.changes) ? fixtureChange.changes : [];
            return changes.map((change) => ({ fixtureLabel, change }));
        });
    }

    function renderLatestChanges(data) {
        if (!elements.syncPanel) {
            return;
        }

        let container = elements.syncPanel.querySelector("#live-match-centre-changes");
        if (!container) {
            container = document.createElement("section");
            container.id = "live-match-centre-changes";
            container.className = "live-match-centre-changes";
            container.setAttribute("aria-live", "polite");
            const insertionPoint = elements.syncPanel.querySelector("#sync-error-message");
            if (insertionPoint) {
                insertionPoint.insertAdjacentElement("afterend", container);
            } else {
                elements.syncPanel.appendChild(container);
            }
        }

        const refresh = data?.latest_successful_refresh || {};
        const availability = String(refresh.availability || "not_started");
        if (availability === "not_started") {
            container.innerHTML = `
                <h3>What changed?</h3>
                <p>No successful provider refresh has been stored yet.</p>
            `;
            return;
        }
        if (availability === "not_recorded_before_v1_18") {
            container.innerHTML = `
                <h3>What changed?</h3>
                <p>Changes were not captured for this historical successful refresh.</p>
            `;
            return;
        }
        if (availability !== "recorded") {
            container.innerHTML = `
                <h3>What changed?</h3>
                <p>Provider-backed change data is unavailable for the latest successful refresh.</p>
            `;
            return;
        }

        const changes = flattenChanges(refresh);
        if (changes.length === 0) {
            container.innerHTML = `
                <h3>What changed?</h3>
                <p>No provider-backed change was recorded in this refresh.</p>
            `;
            return;
        }

        const visibleChanges = changes.slice(0, CHANGE_LIMIT);
        const remaining = Math.max(0, changes.length - visibleChanges.length);
        container.innerHTML = `
            <h3>What changed?</h3>
            <p>${escapeHtml(`${refresh.change_count ?? changes.length} provider-backed change${Number(refresh.change_count ?? changes.length) === 1 ? "" : "s"} recorded in the latest successful refresh.`)}</p>
            <ul>
                ${visibleChanges.map(({ fixtureLabel, change }) => `
                    <li><strong>${escapeHtml(fixtureLabel)}:</strong> ${escapeHtml(describeChange(change))}</li>
                `).join("")}
            </ul>
            ${remaining > 0 ? `<p class="live-match-centre-more">${escapeHtml(`${remaining} additional provider-backed change${remaining === 1 ? "" : "s"} not shown.`)}</p>` : ""}
        `;
    }

    async function refreshLiveMatchCentre() {
        setLoadingState();
        try {
            const data = await fetchLiveMatchCentre();
            renderMatches(data);
            renderLatestChanges(data);
        } catch (error) {
            console.error(error);
            if (elements.message) {
                elements.message.textContent = "Stored live-match data could not be loaded.";
            }
            if (elements.freshness) {
                elements.freshness.className = "live-match-centre-freshness unavailable";
                elements.freshness.textContent = "Stored provider freshness is unavailable.";
            }
            if (elements.matches) {
                elements.matches.innerHTML = `
                    <div class="live-match-centre-empty">
                        The dashboard could not read the stored Live Match Centre snapshot. No provider request was made by this panel.
                    </div>
                `;
            }
            renderLatestChanges({
                latest_successful_refresh: { availability: "not_started" },
            });
        }
    }

    function bindEvents() {
        if (elements.refresh) {
            elements.refresh.addEventListener("click", refreshLiveMatchCentre);
        }
        if (elements.matches) {
            elements.matches.addEventListener("click", (event) => {
                const button = event.target.closest("[data-live-match-centre-fixture-id]");
                if (!button) {
                    return;
                }
                window.dispatchEvent(new CustomEvent("live-match-centre:open-fixture", {
                    detail: { fixtureId: button.dataset.liveMatchCentreFixtureId },
                }));
            });
        }
    }

    function initializeLiveMatchCentre() {
        if (!elements.panel) {
            return;
        }
        bindEvents();
        void refreshLiveMatchCentre();
    }

    document.addEventListener("DOMContentLoaded", initializeLiveMatchCentre);
})();
