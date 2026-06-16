from abc import ABC, abstractmethod


class FootballProvider(ABC):
    """
    Base interface for football data providers.

    This allows the app to support different providers later,
    such as API-Football, Sportmonks, or another football data API.
    """

    @abstractmethod
    def get_world_cup_fixtures(self) -> list[dict]:
        """
        Fetch World Cup fixtures from the provider.

        Returns:
            list[dict]: A list of normalized fixture dictionaries.
        """
        pass