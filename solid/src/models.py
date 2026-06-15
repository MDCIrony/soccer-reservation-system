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

    def obtener_duracion(self) -> int:
        """Retorna la duración en horas de la reserva."""
        return self.hora_fin - self.hora_inicio

    def calcular_total(self, precio_hora: float) -> float:
        """Calcula y actualiza el total de la reserva según la tarifa por hora de la cancha."""
        self.total = self.obtener_duracion() * precio_hora
        return self.total

    def es_horario_valido(self) -> bool:
        """Regla de Negocio: Rango de operación es de 08:00 a 22:00."""
        return 8 <= self.hora_inicio < 22 and 8 < self.hora_fin <= 22

    def es_duracion_valida(self) -> bool:
        """Regla de Negocio: Duración de reserva debe estar entre 1 y 4 horas."""
        duracion = self.obtener_duracion()
        return 1 <= duracion <= 4

