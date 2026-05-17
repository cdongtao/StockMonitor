# jobs/main.py
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings
from core.database import AsyncSessionFactory
from data_sources.eastmoney import EastMoneyClient
from tasks.sync_market import sync_market_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def get_trade_dates(days: int) -> list[str]:
    """获取最近 days 天内的交易日列表"""
    client = EastMoneyClient()
    try:
        dates = await client.fetch_trade_dates(limit=days + 20)
        return dates[:days]
    finally:
        await client.close()


async def check_and_backfill() -> None:
    """启动时检查是否需要回填历史数据"""
    from sqlalchemy import text

    async with AsyncSessionFactory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM market_daily_stats"))
        count = result.scalar()

    if count and count > 0:
        logger.info(f"DB already has {count} records, skipping backfill")
        return

    logger.info(f"DB empty, starting backfill for {settings.backfill_days} days...")
    trade_dates = await get_trade_dates(settings.backfill_days)

    for date_str in reversed(trade_dates):  # 从旧到新
        try:
            trade_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
            count = await sync_market_stats(trade_date)
            logger.info(f"Backfill {trade_date}: {count} rows")
        except Exception as e:
            logger.error(f"Backfill failed for {date_str}: {e}")
        await asyncio.sleep(settings.sync_delay)

    logger.info("Backfill complete")


async def run_daily_sync() -> None:
    """每日定时任务：同步今日数据"""
    today = datetime.now().date()
    logger.info(f"Daily sync started for {today}")
    try:
        count = await sync_market_stats(today)
        logger.info(f"Daily sync done: {count} rows")
    except Exception as e:
        logger.error(f"Daily sync failed: {e}")


async def main() -> None:
    await check_and_backfill()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_daily_sync, "cron", hour=15, minute=35)
    # 后续阶段逐步添加：
    # scheduler.add_job(sync_limit_stocks_task, "cron", hour=15, minute=40)  # B2
    # scheduler.add_job(sync_monitor_pool_task, "cron", hour=15, minute=45)  # B4

    scheduler.start()
    logger.info("Scheduler started. Waiting for jobs...")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
