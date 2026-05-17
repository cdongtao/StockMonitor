# jobs/tests/test_eastmoney.py
import pytest
from unittest.mock import AsyncMock, patch
from data_sources.base import EastMoneyBase


@pytest.mark.asyncio
async def test_fetch_all_pages_single_page():
    """单页数据直接返回"""
    mock_response = {
        "result": {"pages": 1, "count": 2, "data": [{"A": 1}, {"A": 2}]},
        "success": True,
        "code": 0,
    }
    base = EastMoneyBase()
    with patch.object(base, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_response
        result = await base.fetch_all_pages(
            report_name="RPT_TEST",
            columns="A",
            filter_str="(X=1)",
        )
    assert len(result) == 2
    assert result[0] == {"A": 1}


@pytest.mark.asyncio
async def test_fetch_all_pages_multi_page():
    """多页数据合并返回"""
    page1 = {"result": {"pages": 2, "count": 4, "data": [{"A": 1}, {"A": 2}]}, "success": True, "code": 0}
    page2 = {"result": {"pages": 2, "count": 4, "data": [{"A": 3}, {"A": 4}]}, "success": True, "code": 0}

    base = EastMoneyBase()
    with patch.object(base, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = [page1, page2]
        result = await base.fetch_all_pages(
            report_name="RPT_TEST",
            columns="A",
            filter_str="(X=1)",
        )
    assert len(result) == 4


@pytest.mark.asyncio
async def test_fetch_page_failure_returns_empty():
    """单页失败时返回空列表，不抛出异常"""
    base = EastMoneyBase()
    with patch.object(base, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = Exception("timeout")
        result = await base.fetch_all_pages(
            report_name="RPT_TEST",
            columns="A",
            filter_str="(X=1)",
        )
    assert result == []
