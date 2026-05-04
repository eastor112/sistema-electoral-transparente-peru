"""Endpoints para gestión de partidos políticos y carga de símbolos a R2."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.application.services.partido_service import PartidoService
from election_system.core.exceptions import (
    ConflictError,
    InvalidAssetError,
    NotFoundError,
    StorageError,
)
from election_system.domain.models import PartidoPolitico
from election_system.infrastructure.db.session import get_db_session
from election_system.infrastructure.repositories.partido_repository import PartidoRepository
from election_system.infrastructure.storage.r2_client import MAX_UPLOAD_BYTES, get_r2_adapter

router = APIRouter(prefix="/partidos")

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class CreatePartidoRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    numero: int = Field(ge=1, le=999)


class PartidoResponse(BaseModel):
    partido_id: str
    nombre: str
    numero: int
    simbolo_url: str | None
    activo: bool
    created_at: datetime


class SimboloUploadResponse(BaseModel):
    partido_id: str
    simbolo_url: str


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------


def _build_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PartidoService:
    return PartidoService(
        repository=PartidoRepository(session),
        storage=get_r2_adapter(),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PartidoResponse)
async def create_partido(
    body: CreatePartidoRequest,
    service: Annotated[PartidoService, Depends(_build_service)],
) -> PartidoResponse:
    try:
        partido = await service.create_partido(nombre=body.nombre, numero=body.numero)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_response(partido)


@router.get("", response_model=list[PartidoResponse])
async def list_partidos(
    service: Annotated[PartidoService, Depends(_build_service)],
    only_active: bool = True,
) -> list[PartidoResponse]:
    partidos = await service.list_partidos(only_active=only_active)
    return [_to_response(p) for p in partidos]


@router.get("/{partido_id}", response_model=PartidoResponse)
async def get_partido(
    partido_id: str,
    service: Annotated[PartidoService, Depends(_build_service)],
) -> PartidoResponse:
    try:
        partido = await service.get_partido(partido_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(partido)


@router.patch(
    "/{partido_id}/simbolo",
    response_model=SimboloUploadResponse,
    summary="Subir símbolo del partido a Cloudflare R2",
)
async def upload_simbolo(
    partido_id: str,
    service: Annotated[PartidoService, Depends(_build_service)],
    file: Annotated[UploadFile, File(description="Imagen del símbolo (JPEG/PNG/WebP/SVG, máx 5 MB)")],
) -> SimboloUploadResponse:
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo de {MAX_UPLOAD_BYTES // 1024 // 1024} MB.",
        )
    content_type = file.content_type or "application/octet-stream"
    try:
        url = await service.upload_simbolo(
            partido_id=partido_id,
            data=data,
            content_type=content_type,
            original_filename=file.filename or "",
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidAssetError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al subir imagen: {exc}",
        ) from exc
    return SimboloUploadResponse(partido_id=partido_id, simbolo_url=url)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_response(partido: PartidoPolitico) -> PartidoResponse:
    return PartidoResponse(
        partido_id=partido.partido_id,
        nombre=partido.nombre,
        numero=partido.numero,
        simbolo_url=partido.simbolo_url,
        activo=partido.activo,
        created_at=partido.created_at,
    )
