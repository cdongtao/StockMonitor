# jobs/tasks/base_task.py
import logging
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from core.database import AsyncSessionFactory

logger = logging.getLogger(__name__)


class BaseSyncTask:
    """
    所有盘后数据同步任务的基类。

    子类只需实现：
      - task_name: str           任务名，用于日志
      - model: type              SQLAlchemy ORM 模型类
      - conflict_columns: list   upsert 冲突约束列名
      - fetch(): list[dict]      从 API 拉取原始数据
      - to_row(raw): dict        原始数据 → ORM 字段字典
    """

    task_name: str = "unnamed"
    model: type[DeclarativeBase]
    conflict_columns: list[str]

    async def fetch(self) -> list[dict]:
        raise NotImplementedError

    def to_row(self, raw: dict) -> dict | None:
        raise NotImplementedError

    async def run(self, session: AsyncSession | None = None) -> int:
        """拉取数据并 upsert 到 DB，返回写入条数"""
        try:
            raw_rows = await self.fetch()
        except Exception as e:
            logger.error(f"[{self.task_name}] fetch failed: {e}")
            return 0

        if not raw_rows:
            logger.warning(f"[{self.task_name}] no data returned")
            return 0

        rows: list[dict] = []
        for raw in raw_rows:
            try:
                row = self.to_row(raw)
                if row is not None:
                    rows.append(row)
            except Exception as e:
                logger.error(f"[{self.task_name}] to_row failed for {raw}: {e}")

        if not rows:
            return 0

        own_session = session is None
        if own_session:
            session = AsyncSessionFactory()

        try:
            stmt = insert(self.model).values(rows)
            update_cols = {
                col.key: col
                for col in stmt.excluded
                if col.key not in self.conflict_columns
            }
            stmt = stmt.on_conflict_do_update(
                index_elements=self.conflict_columns,
                set_=update_cols,
            )
            await session.execute(stmt)
            await session.commit()
            logger.info(f"[{self.task_name}] upserted {len(rows)} rows")
            return len(rows)
        except Exception as e:
            await session.rollback()
            logger.error(f"[{self.task_name}] DB error: {e}")
            raise
        finally:
            if own_session:
                await session.close()
