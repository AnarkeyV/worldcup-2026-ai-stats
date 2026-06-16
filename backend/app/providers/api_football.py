from app.providers.base import FootballProvider


class ApiFootballProvider(FootballProvider):
    """
    API-Football provider implementation.

    For now, this class is only a placeholder.
    In the next step, we will add the real HTTP request logic.
    """

    def get_world_cup_fixtures(self) -> list[dict]:
        """
        Fetch and normalize World Cup fixtures from API-Football.

        Returns:
            list[dict]: A list of normalized fixture dictionaries.
        """
        return []