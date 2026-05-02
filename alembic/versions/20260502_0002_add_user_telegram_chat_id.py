"""add telegram chat id to users

Revision ID: 20260502_0002
Revises: 20260502_0001
Create Date: 2026-05-02 00:10:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260502_0002"
down_revision: str | None = "20260502_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("telegram_chat_id", sa.String(length=64), nullable=True))
    op.create_index("ix_users_telegram_chat_id", "users", ["telegram_chat_id"], unique=False)
    op.create_unique_constraint("uq_users_telegram_chat_id", "users", ["telegram_chat_id"])


def downgrade() -> None:
    op.drop_constraint("uq_users_telegram_chat_id", "users", type_="unique")
    op.drop_index("ix_users_telegram_chat_id", table_name="users")
    op.drop_column("users", "telegram_chat_id")
