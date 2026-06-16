from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "World Cup 2026 AI Stats"
    app_env: str = "development"
    app_version: str = "0.4.0"

    database_url: str = "postgresql+psycopg://worldcup:worldcup@postgres:5432/worldcup"

    football_api_provider: str = "api_football"
    api_football_base_url: str = "https://v3.football.api-sports.io"
    api_football_key: str = ""
    api_football_world_cup_league_id: int = 1
    api_football_season: int = 2026

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")


settings = Settings()
