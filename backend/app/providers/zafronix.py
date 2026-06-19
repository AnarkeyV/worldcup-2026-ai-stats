import re
from typing import Any

import httpx

from app.config import settings
from app.providers.base import FootballProvider


class ZafronixProviderError(RuntimeError):
    """
    Raised when Zafronix cannot return usable World Cup fixture data.
    """


class ZafronixProvider(FootballProvider):
    """
    Zafronix World Cup provider implementation.

    This provider fetches FIFA World Cup 2026 matches from Zafronix and
    converts the raw provider response into the app's normalized fixture format.
    """

    STATUS_MAP = {
        "finished": "complete",
        "complete": "complete",
        "completed": "complete",
        "final": "complete",
        "scheduled": "scheduled",
        "not_started": "scheduled",
        "not started": "scheduled",
        "upcoming": "scheduled",
        "live": "live",
        "in_progress": "live",
        "in progress": "live",
        "halftime": "live",
        "half_time": "live",
        "postponed": "postponed",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "abandoned": "abandoned",
    }

    TEAM_CODE_OVERRIDES = {
        "Algeria": "DZA",
        "Argentina": "ARG",
        "Australia": "AUS",
        "Austria": "AUT",
        "Belgium": "BEL",
        "Bosnia and Herzegovina": "BIH",
        "Brazil": "BRA",
        "Canada": "CAN",
        "Cape Verde": "CPV",
        "Colombia": "COL",
        "Croatia": "CRO",
        "Curacao": "CUW",
        "Curaçao": "CUW",
        "Czechia": "CZE",
        "DR Congo": "COD",
        "Ecuador": "ECU",
        "Egypt": "EGY",
        "England": "ENG",
        "France": "FRA",
        "Germany": "GER",
        "Ghana": "GHA",
        "Haiti": "HAI",
        "Iran": "IRN",
        "Iraq": "IRQ",
        "Ivory Coast": "CIV",
        "Japan": "JPN",
        "Jordan": "JOR",
        "Korea Republic": "KOR",
        "Mexico": "MEX",
        "Morocco": "MAR",
        "Netherlands": "NED",
        "New Zealand": "NZL",
        "Norway": "NOR",
        "Panama": "PAN",
        "Paraguay": "PAR",
        "Portugal": "POR",
        "Qatar": "QAT",
        "Saudi Arabia": "KSA",
        "Scotland": "SCO",
        "Senegal": "SEN",
        "South Africa": "RSA",
        "Spain": "ESP",
        "Sweden": "SWE",
        "Switzerland": "SUI",
        "Tunisia": "TUN",
        "Turkey": "TUR",
        "United States": "USA",
        "Uruguay": "URU",
        "Uzbekistan": "UZB",
    }

    def __init__(self) -> None:
        self.base_url = settings.zafronix_base_url.rstrip("/")
        self.api_key = settings.zafronix_api_key
        self.year = settings.zafronix_world_cup_year

    def get_world_cup_fixtures(self) -> list[dict]:
        if not self.api_key or self.api_key == "replace_me":
            raise ValueError("ZAFRONIX_API_KEY is not configured.")

        url = f"{self.base_url}/matches"
        headers = {
            "X-API-Key": self.api_key,
        }
        params = {
            "year": self.year,
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
            raise ZafronixProviderError(
                f"Zafronix request failed with status {status_code}."
            ) from error

        except httpx.RequestError as error:
            raise ZafronixProviderError(
                f"Zafronix request failed: {error}"
            ) from error

        except ValueError as error:
            raise ZafronixProviderError("Zafronix returned invalid JSON.") from error

        fixtures = self._extract_fixture_items(payload)

        normalized_fixtures = []

        for item in fixtures:
            normalized_fixture = self._normalize_fixture(item)

            if normalized_fixture is not None:
                normalized_fixtures.append(normalized_fixture)

        return normalized_fixtures

    def _extract_fixture_items(self, payload: Any) -> list[dict]:
        if isinstance(payload, list):
            return payload

        if not isinstance(payload, dict):
            raise ZafronixProviderError("Zafronix returned an invalid payload.")

        if isinstance(payload.get("data"), list):
            return payload["data"]

        if isinstance(payload.get("matches"), list):
            return payload["matches"]

        raise ZafronixProviderError("Zafronix returned an invalid fixture list.")

    def _normalize_fixture(self, item: dict) -> dict | None:
        if not isinstance(item, dict):
            return None

        fixture_id = self._clean_text(item.get("id"))
        kickoff_time = self._clean_text(item.get("kickoffUtc"))
        home_team_name = self._clean_text(item.get("homeTeam"))
        away_team_name = self._clean_text(item.get("awayTeam"))

        if not fixture_id or not kickoff_time or not home_team_name or not away_team_name:
            return None

        stage_raw = self._clean_text(item.get("stageNormalized")) or self._clean_text(
            item.get("stage")
        )
        stage = self._normalize_stage(stage_raw)
        group_name = self._normalize_group_name(stage_raw)

        venue = self._build_venue(item)

        return {
            "external_id": f"zafronix-{fixture_id}",
            "competition": f"FIFA World Cup {self.year}",
            "stage": stage,
            "group_name": group_name,
            "home_team": home_team_name,
            "away_team": away_team_name,
            "home_team_code": self._normalize_team_code(home_team_name),
            "away_team_code": self._normalize_team_code(away_team_name),
            "kickoff_time": kickoff_time,
            "venue": venue,
            "status": self._normalize_status(item.get("status")),
            "home_score": item.get("homeScore"),
            "away_score": item.get("awayScore"),
        }

    def _normalize_status(self, status: Any) -> str:
        cleaned_status = self._clean_text(status)

        if not cleaned_status:
            return "unknown"

        normalized_status = cleaned_status.strip().lower()

        return self.STATUS_MAP.get(normalized_status, normalized_status)

    def _normalize_stage(self, stage: str | None) -> str:
        if not stage:
            return "Unknown Stage"

        normalized_stage = stage.strip().lower().replace("-", "_").replace(" ", "_")

        if re.fullmatch(r"group_[a-l]", normalized_stage):
            return "Group Stage"

        stage_name_map = {
            "round_of_32": "Round of 32",
            "round_of_16": "Round of 16",
            "quarter_final": "Quarter-finals",
            "quarter_finals": "Quarter-finals",
            "semi_final": "Semi-finals",
            "semi_finals": "Semi-finals",
            "third_place": "Third-place Playoff",
            "final": "Final",
        }

        if normalized_stage in stage_name_map:
            return stage_name_map[normalized_stage]

        return stage.replace("_", " ").replace("-", " ").title()

    def _normalize_group_name(self, stage: str | None) -> str | None:
        if not stage:
            return None

        normalized_stage = stage.strip().lower().replace("-", "_").replace(" ", "_")

        match = re.fullmatch(r"group_([a-l])", normalized_stage)

        if match:
            return f"Group {match.group(1).upper()}"

        return None

    def _build_venue(self, item: dict) -> str | None:
        venue_parts = [
            self._clean_text(item.get("stadium")),
            self._clean_text(item.get("city")),
            self._clean_text(item.get("country")),
        ]

        venue_parts = [part for part in venue_parts if part]

        if not venue_parts:
            return None

        return ", ".join(venue_parts)

    def _normalize_team_code(self, team_name: str) -> str:
        override_code = self.TEAM_CODE_OVERRIDES.get(team_name)

        if override_code:
            return override_code

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
