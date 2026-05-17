# jobs/tests/test_sync_market.py
import pytest
from datetime import date
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.sync_market import sync_market_stats


@pytest.mark.asyncio
async def test_sync_market_stats_inserts_data():
    """正常数据时，upsert 被调用一次"""
    mock_data = [
        {
            "TRADE_DATE": "2025-12-26 00:00:00",
            "LIMIT_NUMBERS": 81,
            "NATURAL_LIMIT": 60,
            "DAILY_LIMIT": 21,
            "TOUCH_LIMIT": 120,
            "SEALING_RATE": 0.72,
            "LIMIT_DOWN_NUM": 5,
            "MONEYMAKING_EFFECT": 3,
            "POSITION_SUGGESTION": 2,
        }
    ]
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()

    with patch("tasks.sync_market.EastMoneyClient") as MockClient:
        instance = MockClient.return_value
        instance.fetch_market_stats = AsyncMock(return_value=mock_data)
        instance.close = AsyncMock()

        await sync_market_stats(date(2025, 12, 26), session=mock_session)

    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_sync_market_stats_empty_data():
    """API 返回空数据时，不调用 execute，不报错"""
    mock_session = AsyncMock(spec=AsyncSession)

    with patch("tasks.sync_market.EastMoneyClient") as MockClient:
        instance = MockClient.return_value
        instance.fetch_market_stats = AsyncMock(return_value=[])
        instance.close = AsyncMock()

        await sync_market_stats(date(2025, 12, 26), session=mock_session)

    mock_session.execute.assert_not_called()
