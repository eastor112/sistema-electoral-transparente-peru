from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth")


@router.post("/login")
async def login() -> None:
    # TODO: Implement actor authentication (DNI/biometric integration flow).
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: auth login",
    )


@router.post("/refresh")
async def refresh_token() -> None:
    # TODO: Implement refresh token rotation flow.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: auth refresh",
    )


@router.get("/me")
async def me() -> None:
    # TODO: Implement actor profile and effective permissions response.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: auth me",
    )
