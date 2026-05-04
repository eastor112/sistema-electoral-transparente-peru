"""Endpoint para cargar foto de candidato a Cloudflare R2."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.application.services.cedula_service import CedulaService
from election_system.core.exceptions import InvalidAssetError, NotFoundError, StorageError
from election_system.infrastructure.db.session import get_db_session
from election_system.infrastructure.repositories.partido_repository import PartidoRepository
from election_system.infrastructure.repositories.proceso_repository import ProcesoRepository
from election_system.infrastructure.storage.r2_client import MAX_UPLOAD_BYTES, get_r2_adapter

router = APIRouter(prefix="/candidatos")


class FotoUploadResponse(BaseModel):
    candidato_id: str
    foto_url: str


def _build_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CedulaService:
    return CedulaService(
        repository=ProcesoRepository(session),
        storage=get_r2_adapter(),
        partido_repository=PartidoRepository(session),
    )


@router.patch(
    "/{candidato_id}/foto",
    response_model=FotoUploadResponse,
    summary="Subir foto de candidato a Cloudflare R2",
)
async def upload_foto(
    candidato_id: str,
    service: Annotated[CedulaService, Depends(_build_service)],
    file: Annotated[UploadFile, File(description="Foto del candidato (JPEG/PNG/WebP, máx 5 MB)")],
) -> FotoUploadResponse:
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo de {MAX_UPLOAD_BYTES // 1024 // 1024} MB.",
        )
    content_type = file.content_type or "application/octet-stream"
    try:
        url = await service.upload_foto_candidato(
            candidato_id=candidato_id,
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
    return FotoUploadResponse(candidato_id=candidato_id, foto_url=url)
