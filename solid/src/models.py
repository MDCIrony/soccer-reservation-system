from dataclasses import dataclass
from typing import Optional

@dataclass
class Cancha:
    id: Optional[int]
    nombre: str
    tipo: str
    precio_hora: float

@dataclass
class Cliente:
    id: Optional[int]
    nombre: str
    telefono: str
    email: str

@dataclass
class Reserva:
    id: Optional[int]
    cancha_id: int
    cliente_id: int
    fecha: str  # YYYY-MM-DD
    hora_inicio: int
    hora_fin: int
    total: float
    estado: str = "Confirmada"  # 'Confirmada' o 'Cancelada'

    # Propiedades adicionales para facilitar el renderizado si se hace JOIN
    cancha_nombre: Optional[str] = None
    cliente_nombre: Optional[str] = None
