from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post("/mesas")
async def create_mesa() -> None:
    # TODO: Implement mesa creation use case.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: create mesa",
    )


@router.post("/mesas/{mesa_id}/miembros")
async def assign_miembro(mesa_id: str) -> None:
    # TODO: Implement assignment for titulares and suplentes.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"TODO: assign miembro for mesa {mesa_id}",
    )
