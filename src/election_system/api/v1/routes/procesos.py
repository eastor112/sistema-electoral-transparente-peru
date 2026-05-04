"""Endpoints para procesos electorales y listas electorales."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.application.services.cedula_service import CedulaService
from election_system.core.exceptions import ConflictError, NotFoundError
from election_system.domain.models import (
    Candidato,
    EstadoProceso,
    ListaElectoral,
    ProcesoElectoral,
    TipoCargo,
)
from election_system.infrastructure.db.session import get_db_session
from election_system.infrastructure.repositories.partido_repository import PartidoRepository
from election_system.infrastructure.repositories.proceso_repository import ProcesoRepository
from election_system.infrastructure.storage.r2_client import get_r2_adapter

router = APIRouter(prefix="/procesos")

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class CreateProcesoRequest(BaseModel):
    nombre: str = Field(min_length=3, max_length=200)
    fecha_jornada: date
    tipos_cargo: list[TipoCargo] = Field(min_length=1)


class ProcesoResponse(BaseModel):
    proceso_id: str
    nombre: str
    fecha_jornada: date
    tipos_cargo: list[TipoCargo]
    estado: EstadoProceso
    created_at: datetime


class UpdateEstadoRequest(BaseModel):
    estado: EstadoProceso


class CreateListaRequest(BaseModel):
    partido_id: str = Field(min_length=36, max_length=36)
    tipo_cargo: TipoCargo


class ListaResponse(BaseModel):
    lista_id: str
    proceso_id: str
    partido_id: str
    tipo_cargo: TipoCargo
    tiene_voto_preferencial: bool


class AddCandidatoRequest(BaseModel):
    nombre_completo: str = Field(min_length=2, max_length=200)
    orden: int = Field(ge=1)
    es_titular: bool = True


class CandidatoResponse(BaseModel):
    candidato_id: str
    lista_id: str
    nombre_completo: str
    orden: int
    es_titular: bool
    foto_url: str | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------


def _build_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CedulaService:
    return CedulaService(
        repository=ProcesoRepository(session),
        storage=get_r2_adapter(),
        partido_repository=PartidoRepository(session),
    )


# ---------------------------------------------------------------------------
# Proceso routes
# ---------------------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProcesoResponse)
async def create_proceso(
    body: CreateProcesoRequest,
    service: Annotated[CedulaService, Depends(_build_service)],
) -> ProcesoResponse:
    proceso = await service.create_proceso(
        nombre=body.nombre,
        fecha_jornada=body.fecha_jornada.isoformat(),
        tipos_cargo=body.tipos_cargo,
    )
    return _to_proceso_response(proceso)


@router.get("", response_model=list[ProcesoResponse])
async def list_procesos(
    service: Annotated[CedulaService, Depends(_build_service)],
) -> list[ProcesoResponse]:
    procesos = await service.list_procesos()
    return [_to_proceso_response(p) for p in procesos]


@router.get("/{proceso_id}", response_model=ProcesoResponse)
async def get_proceso(
    proceso_id: str,
    service: Annotated[CedulaService, Depends(_build_service)],
) -> ProcesoResponse:
    try:
        proceso = await service.get_proceso(proceso_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_proceso_response(proceso)


@router.patch("/{proceso_id}/estado", status_code=status.HTTP_204_NO_CONTENT)
async def update_estado(
    proceso_id: str,
    body: UpdateEstadoRequest,
    service: Annotated[CedulaService, Depends(_build_service)],
) -> None:
    try:
        await service.update_estado(proceso_id=proceso_id, estado=body.estado)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Lista electoral routes
# ---------------------------------------------------------------------------


@router.post(
    "/{proceso_id}/listas",
    status_code=status.HTTP_201_CREATED,
    response_model=ListaResponse,
)
async def create_lista(
    proceso_id: str,
    body: CreateListaRequest,
    service: Annotated[CedulaService, Depends(_build_service)],
) -> ListaResponse:
    try:
        lista = await service.create_lista(
            proceso_id=proceso_id,
            partido_id=body.partido_id,
            tipo_cargo=body.tipo_cargo,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_lista_response(lista)


@router.get("/{proceso_id}/listas", response_model=list[ListaResponse])
async def list_listas(
    proceso_id: str,
    service: Annotated[CedulaService, Depends(_build_service)],
) -> list[ListaResponse]:
    try:
        listas = await service.list_listas(proceso_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [_to_lista_response(la) for la in listas]


# ---------------------------------------------------------------------------
# Candidato routes (nested under lista)
# ---------------------------------------------------------------------------


@router.post(
    "/{proceso_id}/listas/{lista_id}/candidatos",
    status_code=status.HTTP_201_CREATED,
    response_model=CandidatoResponse,
)
async def add_candidato(
    proceso_id: str,
    lista_id: str,
    body: AddCandidatoRequest,
    service: Annotated[CedulaService, Depends(_build_service)],
) -> CandidatoResponse:
    try:
        candidato = await service.add_candidato(
            proceso_id=proceso_id,
            lista_id=lista_id,
            nombre_completo=body.nombre_completo,
            orden=body.orden,
            es_titular=body.es_titular,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_candidato_response(candidato)


@router.get(
    "/{proceso_id}/listas/{lista_id}/candidatos",
    response_model=list[CandidatoResponse],
)
async def list_candidatos(
    proceso_id: str,
    lista_id: str,
    service: Annotated[CedulaService, Depends(_build_service)],
) -> list[CandidatoResponse]:
    try:
        candidatos = await service.list_candidatos(lista_id=lista_id, proceso_id=proceso_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [_to_candidato_response(c) for c in candidatos]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_proceso_response(proceso: ProcesoElectoral) -> ProcesoResponse:
    return ProcesoResponse(
        proceso_id=proceso.proceso_id,
        nombre=proceso.nombre,
        fecha_jornada=proceso.fecha_jornada,
        tipos_cargo=proceso.tipos_cargo,
        estado=proceso.estado,
        created_at=proceso.created_at,
    )


def _to_lista_response(lista: ListaElectoral) -> ListaResponse:
    return ListaResponse(
        lista_id=lista.lista_id,
        proceso_id=lista.proceso_id,
        partido_id=lista.partido_id,
        tipo_cargo=lista.tipo_cargo,
        tiene_voto_preferencial=lista.tiene_voto_preferencial,
    )


def _to_candidato_response(candidato: Candidato) -> CandidatoResponse:
    return CandidatoResponse(
        candidato_id=candidato.candidato_id,
        lista_id=candidato.lista_id,
        nombre_completo=candidato.nombre_completo,
        orden=candidato.orden,
        es_titular=candidato.es_titular,
        foto_url=candidato.foto_url,
        created_at=candidato.created_at,
    )
