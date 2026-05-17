# jobs/data_sources/eastmoney.py
from datetime import date

from data_sources.base import EastMoneyBase


class EastMoneyClient(EastMoneyBase):
    async def fetch_market_stats(self, trade_date: date) -> list[dict]:
        """B1: 涨停市场每日统计 — RPT_INTSELECTION_LIMITHIS"""
        columns = (
            "TRADE_DATE,LIMIT_NUMBERS,NATURAL_LIMIT,DAILY_LIMIT,TOUCH_LIMIT,"
            "SEALING_RATE,NATURAL_LIMIT_YES,LIMIT_PER_YES,POSITION_SUGGESTION,"
            "MONEYMAKING_EFFECT,SEALING_RATE_YES,LIMIT_DOWN_NUM,CJDT_NUM,DT_FBL"
        )
        filter_str = f"(TRADE_DATE='{trade_date.strftime('%Y-%m-%d')}')"
        return await self.fetch_all_pages(
            report_name="RPT_INTSELECTION_LIMITHIS",
            columns=columns,
            filter_str=filter_str,
        )

    async def fetch_trade_dates(self, limit: int = 100) -> list[str]:
        """获取最近交易日列表，用于回填判断"""
        data = await self.fetch_all_pages(
            report_name="RPT_INTSELECTION_DATELIST",
            columns="TRADE_DATE,IS_NEW",
            filter_str="",
        )
        return [row["TRADE_DATE"] for row in data[:limit] if row.get("TRADE_DATE")]
