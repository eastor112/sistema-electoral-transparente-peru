"""cedula electoral: partidos, procesos, listas, candidatos

Revision ID: 20260504_0004
Revises: 20260502_0003
Create Date: 2026-05-04 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260504_0004"
down_revision: str | None = "20260502_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # partidos_politicos                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        "partidos_politicos",
        sa.Column("partido_id", sa.String(36), primary_key=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("simbolo_url", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_unique_constraint("uq_partidos_nombre", "partidos_politicos", ["nombre"])
    op.create_unique_constraint("uq_partidos_numero", "partidos_politicos", ["numero"])

    # ------------------------------------------------------------------ #
    # procesos_electorales                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "procesos_electorales",
        sa.Column("proceso_id", sa.String(36), primary_key=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("fecha_jornada", sa.Date(), nullable=False),
        sa.Column(
            "tipos_cargo",
            postgresql.ARRAY(sa.String(64)),
            nullable=False,
        ),
        sa.Column("estado", sa.String(32), nullable=False, server_default="CONFIGURACION"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ------------------------------------------------------------------ #
    # listas_electorales                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        "listas_electorales",
        sa.Column("lista_id", sa.String(36), primary_key=True),
        sa.Column(
            "proceso_id",
            sa.String(36),
            sa.ForeignKey("procesos_electorales.proceso_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "partido_id",
            sa.String(36),
            sa.ForeignKey("partidos_politicos.partido_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("tipo_cargo", sa.String(64), nullable=False),
        sa.Column(
            "tiene_voto_preferencial", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_listas_proceso_id", "listas_electorales", ["proceso_id"])
    op.create_index("ix_listas_partido_id", "listas_electorales", ["partido_id"])

    # ------------------------------------------------------------------ #
    # candidatos                                                           #
    # ------------------------------------------------------------------ #
    op.create_table(
        "candidatos",
        sa.Column("candidato_id", sa.String(36), primary_key=True),
        sa.Column(
            "lista_id",
            sa.String(36),
            sa.ForeignKey("listas_electorales.lista_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nombre_completo", sa.String(200), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("es_titular", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("foto_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_candidatos_lista_id", "candidatos", ["lista_id"])


def downgrade() -> None:
    op.drop_index("ix_candidatos_lista_id", table_name="candidatos")
    op.drop_table("candidatos")
    op.drop_index("ix_listas_partido_id", table_name="listas_electorales")
    op.drop_index("ix_listas_proceso_id", table_name="listas_electorales")
    op.drop_table("listas_electorales")
    op.drop_table("procesos_electorales")
    op.drop_constraint("uq_partidos_numero", "partidos_politicos", type_="unique")
    op.drop_constraint("uq_partidos_nombre", "partidos_politicos", type_="unique")
    op.drop_table("partidos_politicos")
