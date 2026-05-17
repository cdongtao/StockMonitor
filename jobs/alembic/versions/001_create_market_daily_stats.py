"""create market_daily_stats

Revision ID: 001
Revises:
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'market_daily_stats',
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('limit_numbers', sa.Integer(), nullable=True),
        sa.Column('natural_limit', sa.Integer(), nullable=True),
        sa.Column('daily_limit', sa.Integer(), nullable=True),
        sa.Column('touch_limit', sa.Integer(), nullable=True),
        sa.Column('sealing_rate', sa.Numeric(), nullable=True),
        sa.Column('limit_down_num', sa.Integer(), nullable=True),
        sa.Column('moneymaking_effect', sa.Integer(), nullable=True),
        sa.Column('position_suggestion', sa.Integer(), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('trade_date')
    )


def downgrade() -> None:
    op.drop_table('market_daily_stats')
