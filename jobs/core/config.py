from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    backfill_days: int = 90
    em_timeout: int = 30
    em_max_retry: int = 2
    em_page_size: int = 50
    em_concurrent: int = 5
    sync_delay: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
