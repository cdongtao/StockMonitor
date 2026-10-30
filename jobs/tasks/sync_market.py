# jobs/tasks/sync_market.py
import json
from datetime import date, datetime

from data_sources.eastmoney import EastMoneyClient
from models.market_daily_stats import MarketDailyStats
from tasks.base_task import BaseSyncTask


class SyncMarketStats(BaseSyncTask):
    """B1/B3: 涨停市场每日统计 + 赚钱效应评分"""

    task_name = "B1"
    model = MarketDailyStats
    conflict_columns = ["trade_date"]

    def __init__(self, trade_date: date):
        self.trade_date = trade_date
        self._client = EastMoneyClient()

    async def fetch(self) -> list[dict]:
        try:
            return await self._client.fetch_market_stats(self.trade_date)
        finally:
            await self._client.close()

    def to_row(self, raw: dict) -> dict | None:
        trade_date_str = raw.get("TRADE_DATE")
        if not trade_date_str:
            return None
        return {
            "trade_date": datetime.strptime(trade_date_str[:10], "%Y-%m-%d").date(),
            "limit_numbers": raw.get("LIMIT_NUMBERS"),
            "natural_limit": raw.get("NATURAL_LIMIT"),
            "daily_limit": raw.get("DAILY_LIMIT"),
            "touch_limit": raw.get("TOUCH_LIMIT"),
            "sealing_rate": raw.get("SEALING_RATE"),
            "limit_down_num": raw.get("LIMIT_DOWN_NUM"),
            "moneymaking_effect": raw.get("MONEYMAKING_EFFECT"),
            "position_suggestion": raw.get("POSITION_SUGGESTION"),
            "raw_data": json.dumps(raw, ensure_ascii=False),
        }


async def sync_market_stats(trade_date: date, session=None) -> int:
    return await SyncMarketStats(trade_date).run(session=session)
