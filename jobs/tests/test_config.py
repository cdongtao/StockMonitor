from core.config import Settings


def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/test")
    monkeypatch.setenv("BACKFILL_DAYS", "30")
    monkeypatch.setenv("EM_TIMEOUT", "10")
    monkeypatch.setenv("EM_MAX_RETRY", "1")
    monkeypatch.setenv("EM_PAGE_SIZE", "20")
    monkeypatch.setenv("EM_CONCURRENT", "3")
    monkeypatch.setenv("SYNC_DELAY", "2")

    s = Settings()
    assert s.database_url == "postgresql+asyncpg://u:p@localhost/test"
    assert s.backfill_days == 30
    assert s.em_timeout == 10
    assert s.em_max_retry == 1
    assert s.em_page_size == 20
    assert s.em_concurrent == 3
    assert s.sync_delay == 2


def test_settings_defaults():
    s = Settings(
        database_url="postgresql+asyncpg://u:p@localhost/test",
    )
    assert s.backfill_days == 90
    assert s.em_timeout == 30
    assert s.em_max_retry == 2
    assert s.em_page_size == 50
    assert s.em_concurrent == 5
    assert s.sync_delay == 1
