import re
from typing import Any

import httpx

from app.config import settings
from app.providers.base import FootballProvider


class ApiFootballProviderError(RuntimeError):
    """
    Raised when API-Football cannot return usable fixture data.
    """


class ApiFootballProvider(FootballProvider):
    """
    API-Football provider implementation.

    This provider fetches FIFA World Cup 2026 fixtures from API-Football
    and converts the raw provider response into the app's normalized fixture format.
    """

    STATUS_MAP = {
        "TBD": "scheduled",
        "NS": "scheduled",
        "1H": "live",
        "HT": "live",
        "2H": "live",
        "ET": "live",
        "BT": "live",
        "P": "live",
        "SUSP": "live",
        "INT": "live",
        "FT": "complete",
        "AET": "complete",
        "PEN": "complete",
        "PST": "postponed",
        "CANC": "cancelled",
        "ABD": "abandoned",
        "AWD": "complete",
        "WO": "complete",
    }

    TEAM_CODE_OVERRIDES = {
        "Algeria": "DZA",
        "Argentina": "ARG",
        "France": "FRA",
        "Mexico": "MEX",
        "Paraguay": "PAR",
        "Senegal": "SEN",
        "South Africa": "RSA",
        "United States": "USA",
        "United States of America": "USA",
    }

    def __init__(self) -> None:
        self.base_url = settings.api_football_base_url.rstrip("/")
        self.api_key = settings.api_football_key
        self.league_id = settings.api_football_world_cup_league_id
        self.season = settings.api_football_season

    def get_world_cup_fixtures(self) -> list[dict]:
        """
        Fetch and normalize World Cup fixtures from API-Football.

        Returns:
            list[dict]: A list of normalized fixture dictionaries.
        """
        if not self.api_key or self.api_key == "replace_me":
            raise ValueError("API_FOOTBALL_KEY is not configured.")

        url = f"{self.base_url}/fixtures"
        headers = {
            "x-apisports-key": self.api_key,
        }
        params = {
            "league": self.league_id,
            "season": self.season,
        }

        try:
            response = httpx.get(
                url,
                headers=headers,
                params=params,
                timeout=20.0,
            )
            response.raise_for_status()
            payload = response.json()

        except httpx.HTTPStatusError as error:
            status_code = getattr(error.response, "status_code", "unknown")
            raise ApiFootballProviderError(
                f"API-Football request failed with status {status_code}."
            ) from error

        except httpx.RequestError as error:
            raise ApiFootballProviderError(
                f"API-Football request failed: {error}"
            ) from error

        except ValueError as error:
            raise ApiFootballProviderError(
                "API-Football returned invalid JSON."
            ) from error

        fixtures = self._extract_fixture_items(payload)

        normalized_fixtures = []

        for item in fixtures:
            normalized_fixture = self._normalize_fixture(item)

            if normalized_fixture is not None:
                normalized_fixtures.append(normalized_fixture)

        return normalized_fixtures

    def _extract_fixture_items(self, payload: Any) -> list[dict]:
        if not isinstance(payload, dict):
            raise ApiFootballProviderError(
                "API-Football returned an invalid payload."
            )

        fixtures = payload.get("response", [])

        if not isinstance(fixtures, list):
            raise ApiFootballProviderError(
                "API-Football returned an invalid fixture list."
            )

        return fixtures

    def _normalize_fixture(self, item: dict) -> dict | None:
        if not isinstance(item, dict):
            return None

        fixture = item.get("fixture") or {}
        league = item.get("league") or {}
        teams = item.get("teams") or {}
        goals = item.get("goals") or {}

        home_team = teams.get("home") or {}
        away_team = teams.get("away") or {}

        fixture_id = fixture.get("id")
        kickoff_time = fixture.get("date")
        home_team_name = self._clean_text(home_team.get("name"))
        away_team_name = self._clean_text(away_team.get("name"))

        if not fixture_id or not kickoff_time or not home_team_name or not away_team_name:
            return None

        stage = self._clean_text(league.get("round")) or "Group Stage"
        group_name = stage
        raw_status = (fixture.get("status") or {}).get("short")

        return {
            "external_id": str(fixture_id),
            "competition": self._clean_text(league.get("name"))
            or "FIFA World Cup 2026",
            "stage": stage,
            "group_name": group_name,
            "home_team": home_team_name,
            "away_team": away_team_name,
            "home_team_code": self._normalize_team_code(home_team),
            "away_team_code": self._normalize_team_code(away_team),
            "kickoff_time": kickoff_time,
            "venue": self._clean_text((fixture.get("venue") or {}).get("name")),
            "status": self._normalize_status(raw_status),
            "home_score": goals.get("home"),
            "away_score": goals.get("away"),
        }

    def _normalize_status(self, status: str | None) -> str:
        if status is None:
            return "unknown"

        normalized_status = str(status).strip().upper()

        if not normalized_status:
            return "unknown"

        return self.STATUS_MAP.get(normalized_status, normalized_status.lower())

    def _normalize_team_code(self, team: dict) -> str:
        provider_code = self._clean_text(team.get("code"))

        if provider_code:
            return provider_code.upper()[:10]

        team_name = self._clean_text(team.get("name"))

        if not team_name:
            return "UNK"

        override_code = self.TEAM_CODE_OVERRIDES.get(team_name)

        if override_code:
            return override_code

        return self._derive_team_code(team_name)

    def _derive_team_code(self, team_name: str) -> str:
        words = re.findall(r"[A-Za-z0-9]+", team_name)

        if not words:
            return "UNK"

        if len(words) == 1:
            return words[0].upper()[:3]

        initials = "".join(word[0] for word in words).upper()

        if len(initials) >= 2:
            return initials[:3]

        return team_name.upper()[:3]

    def _clean_text(self, value: Any) -> str | None:
        if value is None:
            return None

        cleaned_value = str(value).strip()

        if not cleaned_value:
            return None

        return cleaned_value