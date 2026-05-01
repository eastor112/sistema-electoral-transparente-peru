from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post("/{mesa_id}/apertura")
async def abrir_mesa(mesa_id: str) -> None:
    # TODO: Implement apertura flow with attendance/quorum checks.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"TODO: apertura mesa {mesa_id}",
    )


@router.post("/{mesa_id}/incidencias")
async def reportar_incidencia(mesa_id: str) -> None:
    # TODO: Implement incidence intake with photo and description requirements.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"TODO: incidencia mesa {mesa_id}",
    )


@router.get("/{mesa_id}/fiabilidad")
async def obtener_fiabilidad(mesa_id: str) -> None:
    # TODO: Implement reliability score read model endpoint.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"TODO: fiabilidad mesa {mesa_id}",
    )
