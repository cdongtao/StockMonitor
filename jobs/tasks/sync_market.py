# jobs/tasks/sync_market.py
import json
import logging
from datetime import date, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionFactory
from data_sources.eastmoney import EastMoneyClient

logger = logging.getLogger(__name__)


def _parse_trade_date(raw: str) -> date:
    return datetime.strptime(raw[:10], "%Y-%m-%d").date()


async def sync_market_stats(trade_date: date, session: AsyncSession | None = None) -> int:
    """同步 B1 市场统计数据，返回写入条数"""
    client = EastMoneyClient()
    try:
        rows = await client.fetch_market_stats(trade_date)
    finally:
        await client.close()

    if not rows:
        logger.warning(f"[B1] No data for {trade_date}")
        return 0

    upsert_sql = text("""
        INSERT INTO market_daily_stats (
            trade_date, limit_numbers, natural_limit, daily_limit, touch_limit,
            sealing_rate, limit_down_num, moneymaking_effect, position_suggestion, raw_data
        ) VALUES (
            :trade_date, :limit_numbers, :natural_limit, :daily_limit, :touch_limit,
            :sealing_rate, :limit_down_num, :moneymaking_effect, :position_suggestion, :raw_data::jsonb
        )
        ON CONFLICT (trade_date) DO UPDATE SET
            limit_numbers = EXCLUDED.limit_numbers,
            natural_limit = EXCLUDED.natural_limit,
            daily_limit = EXCLUDED.daily_limit,
            touch_limit = EXCLUDED.touch_limit,
            sealing_rate = EXCLUDED.sealing_rate,
            limit_down_num = EXCLUDED.limit_down_num,
            moneymaking_effect = EXCLUDED.moneymaking_effect,
            position_suggestion = EXCLUDED.position_suggestion,
            raw_data = EXCLUDED.raw_data
    """)

    params = []
    for row in rows:
        try:
            params.append({
                "trade_date": _parse_trade_date(row["TRADE_DATE"]),
                "limit_numbers": row.get("LIMIT_NUMBERS"),
                "natural_limit": row.get("NATURAL_LIMIT"),
                "daily_limit": row.get("DAILY_LIMIT"),
                "touch_limit": row.get("TOUCH_LIMIT"),
                "sealing_rate": row.get("SEALING_RATE"),
                "limit_down_num": row.get("LIMIT_DOWN_NUM"),
                "moneymaking_effect": row.get("MONEYMAKING_EFFECT"),
                "position_suggestion": row.get("POSITION_SUGGESTION"),
                "raw_data": json.dumps(row, ensure_ascii=False),
            })
        except Exception as e:
            logger.error(f"[B1] Failed to parse row {row}: {e}")

    if not params:
        return 0

    own_session = session is None
    if own_session:
        session = AsyncSessionFactory()

    try:
        await session.execute(upsert_sql, params)
        await session.commit()
        logger.info(f"[B1] Upserted {len(params)} rows for {trade_date}")
        return len(params)
    except Exception as e:
        await session.rollback()
        logger.error(f"[B1] DB error for {trade_date}: {e}")
        raise
    finally:
        if own_session:
            await session.close()
