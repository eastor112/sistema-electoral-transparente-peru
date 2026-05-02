import jwt
from fastapi import Header, HTTPException, status

from election_system.core.security import decode_token


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

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, expected_type="access")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    return {"actor_id": subject, "role": "ACTOR"}
