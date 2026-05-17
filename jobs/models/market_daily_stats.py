# jobs/models/market_daily_stats.py
from datetime import date

from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class MarketDailyStats(Base):
    __tablename__ = "market_daily_stats"

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    limit_numbers: Mapped[int | None] = mapped_column(Integer)
    natural_limit: Mapped[int | None] = mapped_column(Integer)
    daily_limit: Mapped[int | None] = mapped_column(Integer)
    touch_limit: Mapped[int | None] = mapped_column(Integer)
    sealing_rate: Mapped[float | None] = mapped_column(Numeric)
    limit_down_num: Mapped[int | None] = mapped_column(Integer)
    moneymaking_effect: Mapped[int | None] = mapped_column(Integer)
    position_suggestion: Mapped[int | None] = mapped_column(Integer)
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
