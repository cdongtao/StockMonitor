# jobs/data_sources/base.py
import asyncio
import logging
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
EM_TIMESTAMP = "1770038173236"


class EastMoneyBase:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.em_timeout)

    async def _fetch_page(
        self,
        report_name: str,
        columns: str,
        filter_str: str,
        page_number: int = 1,
    ) -> dict:
        params = {
            "source": "SECURITIES",
            "client": "APP",
            "reportName": report_name,
            "columns": columns,
            "filter": filter_str,
            "pageNumber": str(page_number),
            "pageSize": str(settings.em_page_size),
            "em_timestamp": EM_TIMESTAMP,
        }
        for attempt in range(settings.em_max_retry + 1):
            try:
                resp = await self.client.get(BASE_URL, params=params)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt == settings.em_max_retry:
                    raise
                logger.warning(f"Retry {attempt + 1} for {report_name} page {page_number}: {e}")
                await asyncio.sleep(1)

    async def fetch_all_pages(
        self,
        report_name: str,
        columns: str,
        filter_str: str,
        **kwargs: Any,
    ) -> list[dict]:
        try:
            first = await self._fetch_page(report_name, columns, filter_str, page_number=1)
        except Exception as e:
            logger.error(f"Failed to fetch first page of {report_name}: {e}")
            return []

        result = first.get("result") or {}
        data = result.get("data") or []
        total_pages = result.get("pages", 1)

        if total_pages <= 1:
            return data

        semaphore = asyncio.Semaphore(settings.em_concurrent)

        async def fetch_page_safe(page: int) -> list[dict]:
            async with semaphore:
                try:
                    resp = await self._fetch_page(report_name, columns, filter_str, page_number=page)
                    return (resp.get("result") or {}).get("data") or []
                except Exception as e:
                    logger.error(f"Failed page {page} of {report_name}: {e}")
                    return []

        tasks = [fetch_page_safe(p) for p in range(2, total_pages + 1)]
        pages_data = await asyncio.gather(*tasks)

        for page_data in pages_data:
            data.extend(page_data)

        return data

    async def close(self):
        await self.client.aclose()
