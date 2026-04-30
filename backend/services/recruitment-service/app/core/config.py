from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AIMatch Recruitment Service"
    APP_ENV: str = "development"

    DATABASE_URL: str 

    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    model_config = SettingsConfigDict(env_file="app/.env", env_file_encoding="utf-8")


settings = Settings()
