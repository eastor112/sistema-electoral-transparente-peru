from fastapi import APIRouter

from election_system.api.v1.routes import admin, auth, health, mesas, notifications, roles

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(mesas.router, prefix="/mesas", tags=["mesas"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(roles.router, tags=["roles"])
