"""API 验证脚本：每完成一个 B 系列任务后运行，打印结构和样本数据。不依赖 DB 和 .env"""
import asyncio
import json
import time
from datetime import date

import httpx

BASE_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"


def _ts() -> str:
    return str(int(time.time() * 1000))


# ─── 基础请求 ────────────────────────────────────────────────────────────────

async def em_get(
    client: httpx.AsyncClient,
    report_name: str,
    columns: str,
    filter_str: str = "",
    page_size: int = 5,
    sort_columns: str = "",
    sort_types: str = "",
    extra: dict | None = None,
) -> dict:
    params = {
        "source": "SECURITIES",
        "client": "APP",
        "reportName": report_name,
        "columns": columns,
        "filter": filter_str,
        "pageNumber": "1",
        "pageSize": str(page_size),
        "em_timestamp": _ts(),
    }
    if sort_columns:
        params["sortColumns"] = sort_columns
    if sort_types:
        params["sortTypes"] = sort_types
    if extra:
        params.update(extra)

    resp = await client.get(BASE_URL, params=params)
    resp.raise_for_status()
    return resp.json()


def print_section(title: str):
    print(f"\n{'=' * 65}")
    print(f"  {title}")
    print(f"{'=' * 65}")


def print_result(raw: dict, sample_rows: int = 3):
    success = raw.get("success")
    code = raw.get("code")
    result = raw.get("result") or {}
    total_count = result.get("count", "?")
    total_pages = result.get("pages", "?")
    data = result.get("data") or []

    print(f"  success={success}  code={code}  总条数={total_count}  总页数={total_pages}")

    if not data:
        print("  [无数据]")
        return

    keys = list(data[0].keys())
    print(f"\n  字段({len(keys)}个): {', '.join(keys)}")
    print(f"\n  前 {min(sample_rows, len(data))} 条:")
    for row in data[:sample_rows]:
        print(f"  {json.dumps(row, ensure_ascii=False)}")


# ─── 获取最新交易日 ──────────────────────────────────────────────────────────

async def get_latest_trade_date(client: httpx.AsyncClient) -> date:
    raw = await em_get(
        client,
        "RPT_INTSELECTION_DATELIST",
        "TRADE_DATE,IS_NEW",
        sort_columns="TRADE_DATE",
        sort_types="-1",
        page_size=10,
    )
    rows = (raw.get("result") or {}).get("data") or []
    latest = rows[0]["TRADE_DATE"] if rows else str(date.today())
    return date.fromisoformat(latest[:10])


# ─── B1: 涨停市场每日统计 ─────────────────────────────────────────────────────

async def check_b1(client: httpx.AsyncClient, trade_date: date):
    print_section(f"B1 — 涨停市场每日统计  ({trade_date})")
    raw = await em_get(
        client,
        report_name="RPT_INTSELECTION_LIMITHIS",
        columns=(
            "TRADE_DATE,LIMIT_NUMBERS,NATURAL_LIMIT,DAILY_LIMIT,TOUCH_LIMIT,"
            "SEALING_RATE,NATURAL_LIMIT_YES,LIMIT_PER_YES,POSITION_SUGGESTION,"
            "MONEYMAKING_EFFECT,SEALING_RATE_YES,LIMIT_DOWN_NUM,CJDT_NUM,DT_FBL"
        ),
        filter_str=f"(TRADE_DATE<='{trade_date.strftime('%Y-%m-%d')}')",
        sort_columns="TRADE_DATE",
        sort_types="-1",
        page_size=10,
    )
    print_result(raw)


# ─── main ────────────────────────────────────────────────────────────────────

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        trade_date = date(2026, 5, 18)
        print(f"\n测试日期: {trade_date}")

        await check_b1(client, trade_date)


asyncio.run(main())