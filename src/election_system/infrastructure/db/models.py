from sqlalchemy import Integer, String
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
