from dataclasses import dataclass
from enum import StrEnum


class MesaEstado(StrEnum):
    CONFIGURADA = "CONFIGURADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"


@dataclass(frozen=True)
class Mesa:
    mesa_id: str
    local_id: str
    ubigeo: str
    estado: MesaEstado


@dataclass(frozen=True)
class FiabilidadMesa:
    mesa_id: str
    score: int
    nivel: str
