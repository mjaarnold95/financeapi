from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "dev"
    API_V1_STR: str = "/api/v1"

    # SQLAlchemy URL, e.g. postgresql+psycopg://user:pass@host:5432/db
    DATABASE_URL: str

settings = Settings()
