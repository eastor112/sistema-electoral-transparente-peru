"""Endpoint de vista de cédula electoral completa."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.application.services.cedula_service import CedulaService
from election_system.core.exceptions import NotFoundError
from election_system.domain.models import EstadoProceso, TipoCargo
from election_system.infrastructure.db.session import get_db_session
from election_system.infrastructure.repositories.proceso_repository import ProcesoRepository
from election_system.infrastructure.storage.r2_client import get_r2_adapter

router = APIRouter(prefix="/cedula")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class CandidatoSchema(BaseModel):
    candidato_id: str
    nombre_completo: str
    orden: int
    es_titular: bool
    foto_url: str | None


class ListaSchema(BaseModel):
    lista_id: str
    partido_id: str
    tipo_cargo: TipoCargo
    tiene_voto_preferencial: bool
    candidatos: list[CandidatoSchema]


class CedulaResponse(BaseModel):
    proceso_id: str
    nombre: str
    fecha_jornada: date
    estado: EstadoProceso
    tipos_cargo: list[TipoCargo]
    listas: list[ListaSchema]
    generated_at: datetime


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------


def _build_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CedulaService:
    return CedulaService(
        repository=ProcesoRepository(session),
        storage=get_r2_adapter(),
    )


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.get(
    "/{proceso_id}",
    response_model=CedulaResponse,
    summary="Vista completa de la cédula electoral para un proceso",
)
async def get_cedula(
    proceso_id: str,
    service: Annotated[CedulaService, Depends(_build_service)],
) -> CedulaResponse:
    try:
        view = await service.get_cedula(proceso_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    listas_out = [
        ListaSchema(
            lista_id=la.lista_id,
            partido_id=la.partido_id,
            tipo_cargo=la.tipo_cargo,
            tiene_voto_preferencial=la.tiene_voto_preferencial,
            candidatos=[
                CandidatoSchema(
                    candidato_id=c.candidato_id,
                    nombre_completo=c.nombre_completo,
                    orden=c.orden,
                    es_titular=c.es_titular,
                    foto_url=c.foto_url,
                )
                for c in la.candidatos
            ],
        )
        for la in view.listas
    ]

    from datetime import UTC
    from datetime import datetime as dt

    return CedulaResponse(
        proceso_id=view.proceso.proceso_id,
        nombre=view.proceso.nombre,
        fecha_jornada=view.proceso.fecha_jornada,
        estado=view.proceso.estado,
        tipos_cargo=view.proceso.tipos_cargo,
        listas=listas_out,
        generated_at=dt.now(UTC),
    )
