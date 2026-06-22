from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "World Cup 2026 AI Stats"
    app_env: str = "development"
    app_version: str = "1.11.0"

    database_url: str = "postgresql+psycopg://worldcup:worldcup@postgres:5432/worldcup"

    football_api_provider: str = "api_football"
    api_football_base_url: str = "https://v3.football.api-sports.io"
    api_football_key: str = ""
    api_football_world_cup_league_id: int = 1
    api_football_season: int = 2026

    zafronix_base_url: str = "https://api.zafronix.com/fifa/worldcup/v1"
    zafronix_api_key: str = ""
    zafronix_world_cup_year: int = 2026

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    public_dashboard_url: str = "http://localhost:8000/dashboard"

    llama_base_url: str = "http://127.0.0.1:11434"
    llama_model: str = "llama3.2:1b"
    llama_timeout_seconds: int = 60

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")


settings = Settings()
