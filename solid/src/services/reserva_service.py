from datetime import datetime
from typing import List, Optional, Dict, Tuple
from src.interfaces import ICanchaRepository, IClienteRepository, IReservaRepository
from src.models import Cancha, Cliente, Reserva

class ReservaService:
    def __init__(
        self,
        cancha_repo: ICanchaRepository,
        cliente_repo: IClienteRepository,
        reserva_repo: IReservaRepository
    ):
        self.cancha_repo = cancha_repo
        self.cliente_repo = cliente_repo
        self.reserva_repo = reserva_repo

    def _validar_fecha(self, fecha_str: str) -> bool:
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def obtener_canchas_disponibilidad(self, fecha: str) -> List[Dict]:
        """
        Obtiene la lista de canchas con su disponibilidad horaria (8:00 a 22:00) para una fecha dada.
        Retorna una lista de diccionarios con información formateada.
        """
        if not self._validar_fecha(fecha):
            raise ValueError("Formato de fecha inválido. Debe ser YYYY-MM-DD.")

        canchas = self.cancha_repo.get_all()
        reservas = self.reserva_repo.get_by_date(fecha)

        # Agrupar rangos ocupados por ID de cancha
        ocupacion_por_cancha = {c.id: [] for c in canchas}
        for r in reservas:
            ocupacion_por_cancha[r.cancha_id].append((r.hora_inicio, r.hora_fin))

        resultado = []
        for cancha in canchas:
            disponibilidad = {}
            for h in range(8, 22):
                # Determinar si la hora h está ocupada
                ocupado = False
                for inicio, fin in ocupacion_por_cancha[cancha.id]:
                    if inicio <= h < fin:
                        ocupado = True
                        break
                disponibilidad[h] = not ocupado

            resultado.append({
                "cancha": cancha,
                "disponibilidad": disponibilidad
            })

        return resultado

    def registrar_cliente(self, nombre: str, telefono: str, email: str) -> Cliente:
        """Registra un nuevo cliente validando que el email sea único."""
        nombre = nombre.strip()
        telefono = telefono.strip()
        email = email.strip().lower()

        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")
        if not telefono:
            raise ValueError("El teléfono no puede estar vacío.")
        if not email or "@" not in email:
            raise ValueError("El correo electrónico no es válido.")

        # Verificar duplicados
        existente = self.cliente_repo.get_by_email(email)
        if existente:
            raise ValueError(f"El correo electrónico '{email}' ya se encuentra registrado.")

        cliente = Cliente(id=None, nombre=nombre, telefono=telefono, email=email)
        cliente_id = self.cliente_repo.save(cliente)
        cliente.id = cliente_id
        return cliente

    def obtener_clientes(self) -> List[Cliente]:
        """Obtiene la lista de todos los clientes."""
        return self.cliente_repo.get_all()

    def obtener_canchas(self) -> List[Cancha]:
        """Obtiene la lista de todas las canchas."""
        return self.cancha_repo.get_all()

    def crear_reserva(
        self,
        cliente_id: int,
        cancha_id: int,
        fecha: str,
        hora_inicio: int,
        duracion: int
    ) -> Reserva:
        """
        Crea una reserva para un cliente y cancha en una fecha y hora específicas.
        Aplica y valida todas las reglas de negocio.
        """
        # 1. Validaciones de existencia de Entidades
        cliente = self.cliente_repo.get_by_id(cliente_id)
        if not cliente:
            raise ValueError(f"El cliente con ID {cliente_id} no existe.")

        cancha = self.cancha_repo.get_by_id(cancha_id)
        if not cancha:
            raise ValueError(f"La cancha con ID {cancha_id} no existe.")

        # 2. Validaciones de negocio del horario (Delegadas al Modelo de Dominio Rico)
        if not self._validar_fecha(fecha):
            raise ValueError("Formato de fecha inválido. Debe ser YYYY-MM-DD.")

        hora_fin = hora_inicio + duracion
        reserva = Reserva(
            id=None,
            cancha_id=cancha_id,
            cliente_id=cliente_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            total=0.0,
            estado="Confirmada"
        )

        if not reserva.es_horario_valido():
            raise ValueError("La hora de inicio debe estar en el rango de 8 (08:00) a 21 (21:00), y no exceder las 22:00.")

        if not reserva.es_duracion_valida():
            raise ValueError("La duración de la reserva debe ser de entre 1 y 4 horas.")

        # Calcular costo (Regla del Modelo de Dominio Rico)
        reserva.calcular_total(cancha.precio_hora)

        # 3. Validar disponibilidad de cancha (Traslapes)
        conflictos = self.reserva_repo.check_overlap(cancha_id, fecha, hora_inicio, hora_fin)
        if conflictos:
            detalles = ", ".join([f"Reserva #{c.id} ({c.cliente_nombre}) de {c.hora_inicio:02d}:00 a {c.hora_fin:02d}:00" for c in conflictos])
            raise ValueError(f"La cancha '{cancha.nombre}' ya está ocupada en ese horario. Conflictos: {detalles}")

        # 4. Guardar la reserva
        reserva_id = self.reserva_repo.save(reserva)
        reserva.id = reserva_id
        reserva.cancha_nombre = cancha.nombre
        reserva.cliente_nombre = cliente.nombre
        return reserva

    def obtener_reservas_activas(self) -> List[Reserva]:
        """Retorna la lista de todas las reservas activas (confirmadas)."""
        return self.reserva_repo.get_all_active()

    def cancelar_reserva(self, reserva_id: int) -> Reserva:
        """Cancela una reserva activa."""
        reserva = self.reserva_repo.get_by_id(reserva_id)
        if not reserva:
            raise ValueError(f"La reserva con ID {reserva_id} no existe.")

        if reserva.estado == "Cancelada":
            raise ValueError("La reserva ya se encuentra cancelada.")

        self.reserva_repo.cancel(reserva_id)
        reserva.estado = "Cancelada"
        return reserva

    def obtener_reporte_estadisticas(self) -> dict:
        """Obtiene las estadísticas agregadas financieras y del negocio."""
        return self.reserva_repo.get_financial_stats()
