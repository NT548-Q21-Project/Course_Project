from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AIMatch API Gateway"
    APP_ENV: str = "development"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    IDENTITY_SERVICE_URL: str
    RECRUITMENT_SERVICE_URL: str
    AI_SERVICE_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
