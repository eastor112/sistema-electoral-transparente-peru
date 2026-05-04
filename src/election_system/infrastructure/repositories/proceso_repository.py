"""SQLAlchemy repository for procesos electorales, listas and candidatos."""

from datetime import date
from uuid import uuid4

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.domain.models import (
    Candidato,
    EstadoProceso,
    ListaElectoral,
    ProcesoElectoral,
    TipoCargo,
    cargo_tiene_voto_preferencial,
)
from election_system.infrastructure.db.models import (
    CandidatoORM,
    ListaElectoralORM,
    ProcesoElectoralORM,
)


class ProcesoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Procesos
    # ------------------------------------------------------------------

    async def create(
        self,
        *,
        nombre: str,
        fecha_jornada: str,
        tipos_cargo: list[TipoCargo],
    ) -> ProcesoElectoral:
        orm = ProcesoElectoralORM(
            proceso_id=str(uuid4()),
            nombre=nombre,
            fecha_jornada=date.fromisoformat(fecha_jornada),
            tipos_cargo=[t.value for t in tipos_cargo],
            estado=EstadoProceso.CONFIGURACION.value,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _map_proceso(orm)

    async def get_by_id(self, proceso_id: str) -> ProcesoElectoral | None:
        stmt: Select[tuple[ProcesoElectoralORM]] = select(ProcesoElectoralORM).where(
            ProcesoElectoralORM.proceso_id == proceso_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _map_proceso(orm) if orm else None

    async def list_all(self) -> list[ProcesoElectoral]:
        stmt: Select[tuple[ProcesoElectoralORM]] = select(ProcesoElectoralORM).order_by(
            ProcesoElectoralORM.fecha_jornada.desc()
        )
        result = await self._session.execute(stmt)
        return [_map_proceso(row) for row in result.scalars()]

    async def update_estado(self, *, proceso_id: str, estado: EstadoProceso) -> None:
        stmt = (
            update(ProcesoElectoralORM)
            .where(ProcesoElectoralORM.proceso_id == proceso_id)
            .values(estado=estado.value)
        )
        await self._session.execute(stmt)
        await self._session.commit()

    # ------------------------------------------------------------------
    # Listas
    # ------------------------------------------------------------------

    async def create_lista(
        self,
        *,
        proceso_id: str,
        partido_id: str,
        tipo_cargo: TipoCargo,
    ) -> ListaElectoral:
        orm = ListaElectoralORM(
            lista_id=str(uuid4()),
            proceso_id=proceso_id,
            partido_id=partido_id,
            tipo_cargo=tipo_cargo.value,
            tiene_voto_preferencial=cargo_tiene_voto_preferencial(tipo_cargo),
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _map_lista(orm)

    async def get_lista(self, lista_id: str) -> ListaElectoral | None:
        stmt: Select[tuple[ListaElectoralORM]] = select(ListaElectoralORM).where(
            ListaElectoralORM.lista_id == lista_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _map_lista(orm) if orm else None

    async def list_listas(self, proceso_id: str) -> list[ListaElectoral]:
        stmt: Select[tuple[ListaElectoralORM]] = select(ListaElectoralORM).where(
            ListaElectoralORM.proceso_id == proceso_id
        )
        result = await self._session.execute(stmt)
        return [_map_lista(row) for row in result.scalars()]

    # ------------------------------------------------------------------
    # Candidatos
    # ------------------------------------------------------------------

    async def add_candidato(
        self,
        *,
        lista_id: str,
        nombre_completo: str,
        orden: int,
        es_titular: bool,
    ) -> Candidato:
        orm = CandidatoORM(
            candidato_id=str(uuid4()),
            lista_id=lista_id,
            nombre_completo=nombre_completo,
            orden=orden,
            es_titular=es_titular,
            foto_url=None,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _map_candidato(orm)

    async def get_candidato(self, candidato_id: str) -> Candidato | None:
        stmt: Select[tuple[CandidatoORM]] = select(CandidatoORM).where(
            CandidatoORM.candidato_id == candidato_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _map_candidato(orm) if orm else None

    async def list_candidatos(self, lista_id: str) -> list[Candidato]:
        stmt: Select[tuple[CandidatoORM]] = (
            select(CandidatoORM)
            .where(CandidatoORM.lista_id == lista_id)
            .order_by(CandidatoORM.es_titular.desc(), CandidatoORM.orden)
        )
        result = await self._session.execute(stmt)
        return [_map_candidato(row) for row in result.scalars()]

    async def update_candidato_foto_url(self, *, candidato_id: str, foto_url: str) -> None:
        stmt = (
            update(CandidatoORM)
            .where(CandidatoORM.candidato_id == candidato_id)
            .values(foto_url=foto_url)
        )
        await self._session.execute(stmt)
        await self._session.commit()


# ---------------------------------------------------------------------------
# Mappers
# ---------------------------------------------------------------------------


def _map_proceso(orm: ProcesoElectoralORM) -> ProcesoElectoral:
    return ProcesoElectoral(
        proceso_id=orm.proceso_id,
        nombre=orm.nombre,
        fecha_jornada=orm.fecha_jornada
        if isinstance(orm.fecha_jornada, date)
        else date.fromisoformat(str(orm.fecha_jornada)),
        tipos_cargo=[TipoCargo(t) for t in orm.tipos_cargo],
        estado=EstadoProceso(orm.estado),
        created_at=orm.created_at,
    )


def _map_lista(orm: ListaElectoralORM) -> ListaElectoral:
    return ListaElectoral(
        lista_id=orm.lista_id,
        proceso_id=orm.proceso_id,
        partido_id=orm.partido_id,
        tipo_cargo=TipoCargo(orm.tipo_cargo),
        tiene_voto_preferencial=orm.tiene_voto_preferencial,
    )


def _map_candidato(orm: CandidatoORM) -> Candidato:
    return Candidato(
        candidato_id=orm.candidato_id,
        lista_id=orm.lista_id,
        nombre_completo=orm.nombre_completo,
        orden=orm.orden,
        es_titular=orm.es_titular,
        foto_url=orm.foto_url,
        created_at=orm.created_at,
    )
