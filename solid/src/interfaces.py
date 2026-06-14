from abc import ABC, abstractmethod
from typing import List, Optional
from src.models import Cancha, Cliente, Reserva

class ICanchaRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Cancha]:
        """Obtiene todas las canchas registradas."""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Cancha]:
        """Obtiene una cancha por su ID."""
        pass

    @abstractmethod
    def seed(self, canchas: List[Cancha]) -> None:
        """Puebla las canchas si la base de datos está vacía."""
        pass


class IClienteRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Cliente]:
        """Obtiene todos los clientes registrados."""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Cliente]:
        """Obtiene un cliente por su correo electrónico."""
        pass

    @abstractmethod
    def save(self, cliente: Cliente) -> int:
        """Guarda un nuevo cliente y retorna su ID asignado."""
        pass

    @abstractmethod
    def seed(self, clientes: List[Cliente]) -> None:
        """Puebla los clientes si la base de datos está vacía."""
        pass


class IReservaRepository(ABC):
    @abstractmethod
    def get_all_active(self) -> List[Reserva]:
        """Obtiene todas las reservas con estado 'Confirmada'."""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Reserva]:
        """Obtiene una reserva por su ID."""
        pass

    @abstractmethod
    def get_by_date(self, fecha: str) -> List[Reserva]:
        """Obtiene todas las reservas (activas) para una fecha específica."""
        pass

    @abstractmethod
    def check_overlap(self, cancha_id: int, fecha: str, hora_inicio: int, hora_fin: int) -> List[Reserva]:
        """Verifica si existen reservas activas que se traslapen con el horario solicitado."""
        pass

    @abstractmethod
    def save(self, reserva: Reserva) -> int:
        """Guarda una nueva reserva y retorna su ID asignado."""
        pass

    @abstractmethod
    def cancel(self, id: int) -> None:
        """Cambia el estado de una reserva a 'Cancelada'."""
        pass

    @abstractmethod
    def get_financial_stats(self) -> dict:
        """Obtiene estadísticas agregadas financieras del sistema."""
        pass

    @abstractmethod
    def seed(self, reservas: List[Reserva]) -> None:
        """Puebla las reservas si la base de datos está vacía."""
        pass
