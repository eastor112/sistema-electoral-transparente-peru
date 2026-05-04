from fastapi import APIRouter

from election_system.api.v1.routes import (
    admin,
    auth,
    candidatos,
    cedula,
    health,
    mesas,
    notifications,
    partidos,
    procesos,
    roles,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(mesas.router, prefix="/mesas", tags=["mesas"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(roles.router, tags=["roles"])
api_router.include_router(partidos.router, tags=["cédula/partidos"])
api_router.include_router(procesos.router, tags=["cédula/procesos"])
api_router.include_router(candidatos.router, tags=["cédula/candidatos"])
api_router.include_router(cedula.router, tags=["cédula"])
