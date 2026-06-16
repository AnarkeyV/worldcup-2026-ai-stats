from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "World Cup 2026 AI Stats"
    app_env: str = "development"
    app_version: str = "0.2.0"

    database_url: str = "postgresql+psycopg://worldcup:worldcup@postgres:5432/worldcup"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()