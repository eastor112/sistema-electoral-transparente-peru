"""create user_roles table

Revision ID: 20260502_0003
Revises: 20260502_0002
Create Date: 2026-05-02 00:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260502_0003"
down_revision: str | None = "20260502_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_roles",
        sa.Column("user_role_id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role_type", sa.String(32), nullable=False),
        sa.Column("mesa_id", sa.String(50), nullable=True),
        sa.Column("ubigeo", sa.String(6), nullable=True),
        sa.Column("jornada_id", sa.String(36), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "assigned_by",
            sa.String(36),
            sa.ForeignKey("users.user_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role_type", "user_roles", ["role_type"])
    op.create_index("ix_user_roles_mesa_id", "user_roles", ["mesa_id"])
    op.create_index("ix_user_roles_ubigeo", "user_roles", ["ubigeo"])
    op.create_index("ix_user_roles_jornada_id", "user_roles", ["jornada_id"])


def downgrade() -> None:
    op.drop_index("ix_user_roles_jornada_id", table_name="user_roles")
    op.drop_index("ix_user_roles_ubigeo", table_name="user_roles")
    op.drop_index("ix_user_roles_mesa_id", table_name="user_roles")
    op.drop_index("ix_user_roles_role_type", table_name="user_roles")
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_table("user_roles")
