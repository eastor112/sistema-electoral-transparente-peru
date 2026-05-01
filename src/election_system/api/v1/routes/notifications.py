from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/notificaciones")


@router.get("")
async def list_notifications() -> None:
    # TODO: Return notification feed filtered by actor scope.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: list notifications",
    )


@router.post("/broadcast")
async def broadcast_notification() -> None:
    # TODO: Publish notification to bus/channels (admin/internal/public).
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: broadcast notification",
    )
