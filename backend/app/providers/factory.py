from app.config import settings
from app.providers.api_football import ApiFootballProvider
from app.providers.base import FootballProvider
from app.providers.zafronix import ZafronixProvider


def get_configured_football_provider() -> tuple[str, FootballProvider]:
    provider_name = (settings.football_api_provider or "api_football").strip().lower()

    if provider_name == "api_football":
        return "api_football", ApiFootballProvider()

    if provider_name == "zafronix":
        return "zafronix", ZafronixProvider()

    raise ValueError(
        "Unsupported FOOTBALL_API_PROVIDER. "
        "Use 'api_football' or 'zafronix'."
    )
