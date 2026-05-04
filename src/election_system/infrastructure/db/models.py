from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from election_system.infrastructure.db.base import Base


class MesaORM(Base):
    __tablename__ = "mesas"

    mesa_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    local_id: Mapped[str] = mapped_column(String(50), nullable=False)
    ubigeo: Mapped[str] = mapped_column(String(6), nullable=False)
    estado: Mapped[str] = mapped_column(String(32), nullable=False)


class FiabilidadMesaORM(Base):
    __tablename__ = "fiabilidad_mesa"

    mesa_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel: Mapped[str] = mapped_column(String(16), nullable=False)


class UserORM(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EmailOTPChallengeORM(Base):
    __tablename__ = "email_otp_challenges"

    challenge_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class UserRoleORM(Base):
    """Asignación de rol a un usuario del sistema con ámbito opcional (ABAC)."""

    __tablename__ = "user_roles"

    user_role_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    # Atributos de ámbito ABAC — NULL significa ámbito global
    mesa_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    ubigeo: Mapped[str | None] = mapped_column(String(6), nullable=True, index=True)
    jornada_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    assigned_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# Cédula Electoral — partidos, procesos y listas
# ---------------------------------------------------------------------------


class PartidoPoliticoORM(Base):
    __tablename__ = "partidos_politicos"

    partido_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    simbolo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ProcesoElectoralORM(Base):
    __tablename__ = "procesos_electorales"

    proceso_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    fecha_jornada: Mapped[date] = mapped_column(Date, nullable=False)
    tipos_cargo: Mapped[list[str]] = mapped_column(ARRAY(String(64)), nullable=False)
    estado: Mapped[str] = mapped_column(String(32), nullable=False, default="CONFIGURACION")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ListaElectoralORM(Base):
    __tablename__ = "listas_electorales"

    lista_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    proceso_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("procesos_electorales.proceso_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    partido_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("partidos_politicos.partido_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    tipo_cargo: Mapped[str] = mapped_column(String(64), nullable=False)
    tiene_voto_preferencial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class CandidatoORM(Base):
    __tablename__ = "candidatos"

    candidato_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    lista_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("listas_electorales.lista_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    es_titular: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    foto_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
