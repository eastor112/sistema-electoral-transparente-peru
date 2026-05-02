"""add users and email otp challenges

Revision ID: 20260502_0001
Revises:
Create Date: 2026-05-02 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260502_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "email_otp_challenges",
        sa.Column("challenge_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("challenge_id"),
    )
    op.create_index("ix_email_otp_challenges_user_id", "email_otp_challenges", ["user_id"], unique=False)
    op.create_index("ix_email_otp_challenges_purpose", "email_otp_challenges", ["purpose"], unique=False)
    op.create_index("ix_email_otp_challenges_expires_at", "email_otp_challenges", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_email_otp_challenges_expires_at", table_name="email_otp_challenges")
    op.drop_index("ix_email_otp_challenges_purpose", table_name="email_otp_challenges")
    op.drop_index("ix_email_otp_challenges_user_id", table_name="email_otp_challenges")
    op.drop_table("email_otp_challenges")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
