from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str
    database_url: str
    gemini_model_name: str
    crisis_hotline_number: str

    # JWT / Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    @property
    def checkpointer_db_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
