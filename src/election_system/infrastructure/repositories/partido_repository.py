"""SQLAlchemy repository for partidos políticos."""

from uuid import uuid4

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.domain.models import PartidoPolitico
from election_system.infrastructure.db.models import PartidoPoliticoORM


class PartidoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, nombre: str, numero: int) -> PartidoPolitico:
        orm = PartidoPoliticoORM(
            partido_id=str(uuid4()),
            nombre=nombre,
            numero=numero,
            simbolo_url=None,
            activo=True,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _map(orm)

    async def get_by_id(self, partido_id: str) -> PartidoPolitico | None:
        stmt: Select[tuple[PartidoPoliticoORM]] = select(PartidoPoliticoORM).where(
            PartidoPoliticoORM.partido_id == partido_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _map(orm) if orm else None

    async def list_all(self, *, only_active: bool) -> list[PartidoPolitico]:
        stmt: Select[tuple[PartidoPoliticoORM]] = select(PartidoPoliticoORM).order_by(
            PartidoPoliticoORM.numero
        )
        if only_active:
            stmt = stmt.where(PartidoPoliticoORM.activo.is_(True))
        result = await self._session.execute(stmt)
        return [_map(row) for row in result.scalars()]

    async def update_simbolo_url(self, *, partido_id: str, simbolo_url: str) -> None:
        stmt = (
            update(PartidoPoliticoORM)
            .where(PartidoPoliticoORM.partido_id == partido_id)
            .values(simbolo_url=simbolo_url)
        )
        await self._session.execute(stmt)
        await self._session.commit()


def _map(orm: PartidoPoliticoORM) -> PartidoPolitico:
    return PartidoPolitico(
        partido_id=orm.partido_id,
        nombre=orm.nombre,
        numero=orm.numero,
        simbolo_url=orm.simbolo_url,
        activo=orm.activo,
        created_at=orm.created_at,
    )
