import httpx

from app.config import settings
from app.providers.base import FootballProvider


class ApiFootballProvider(FootballProvider):
    """
    API-Football provider implementation.

    This provider fetches FIFA World Cup 2026 fixtures from API-Football
    and converts the raw provider response into the app's normalized fixture format.
    """

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

        response = httpx.get(url, headers=headers, params=params, timeout=20.0)
        response.raise_for_status()

        payload = response.json()
        fixtures = payload.get("response", [])

        return [self._normalize_fixture(item) for item in fixtures]

    def _normalize_fixture(self, item: dict) -> dict:
        fixture = item.get("fixture", {})
        league = item.get("league", {})
        teams = item.get("teams", {})
        goals = item.get("goals", {})

        home_team = teams.get("home", {}) or {}
        away_team = teams.get("away", {}) or {}

        return {
            "external_id": str(fixture.get("id")),
            "competition": league.get("name", "FIFA World Cup 2026"),
            "stage": league.get("round"),
            "group_name": league.get("round"),
            "home_team": home_team.get("name"),
            "away_team": away_team.get("name"),
            "home_team_code": None,
            "away_team_code": None,
            "kickoff_time": fixture.get("date"),
            "venue": (fixture.get("venue") or {}).get("name"),
            "status": (fixture.get("status") or {}).get("short"),
            "home_score": goals.get("home"),
            "away_score": goals.get("away"),
        }