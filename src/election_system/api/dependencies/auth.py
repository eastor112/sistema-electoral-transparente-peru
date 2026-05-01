from fastapi import Header, HTTPException, status


async def get_current_actor(authorization: str | None = Header(default=None)) -> dict[str, str]:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
        )

    # TODO: Validate JWT, load actor identity and permissions.
    return {"actor_id": "TODO", "role": "TODO"}
