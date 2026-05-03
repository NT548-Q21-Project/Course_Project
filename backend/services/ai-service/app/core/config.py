from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AIMatch AI Service"
    APP_ENV: str = "development"

    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/aimatch_db"
    )

    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "openrouter/free"
    LLM_TIMEOUT_SECONDS: float = 120.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
