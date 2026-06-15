#!/usr/bin/env python3
import os
from datetime import datetime
from src.repositories.sqlite_repos import (
    initialize_sqlite_db,
    SqliteCanchaRepository,
    SqliteClienteRepository,
    SqliteReservaRepository
)
from src.services.reserva_service import ReservaService
from src.ui.console_view import ConsoleView
from src.ui.menu_controller import MenuController
from src.models import Cancha, Cliente, Reserva

DB_FILE = "reservas.db"

def run_seeding(cancha_repo, cliente_repo, reserva_repo):
    """Carga los datos iniciales (semilla) si el repositorio está vacío."""
    # Canchas semilla
    canchas_semilla = [
        Cancha(id=None, nombre="Maracaná", tipo="Fútbol 5", precio_hora=30.0),
        Cancha(id=None, nombre="Camp Nou", tipo="Fútbol 7", precio_hora=50.0),
        Cancha(id=None, nombre="Wembley", tipo="Fútbol 11", precio_hora=80.0),
        Cancha(id=None, nombre="San Siro", tipo="Fútbol 5", precio_hora=35.0),
        Cancha(id=None, nombre="La Bombonera", tipo="Fútbol 7", precio_hora=55.0)
    ]
    cancha_repo.seed(canchas_semilla)

    # Clientes semilla
    clientes_semilla = [
        Cliente(id=None, nombre="Lionel Messi", telefono="123456789", email="messi@gmail.com"),
        Cliente(id=None, nombre="Cristiano Ronaldo", telefono="987654321", email="cr7@gmail.com"),
        Cliente(id=None, nombre="Neymar Jr", telefono="555666777", email="neymar@gmail.com")
    ]
    cliente_repo.seed(clientes_semilla)

    # Reservas semilla
    hoy = datetime.now().strftime("%Y-%m-%d")
    reservas_semilla = [
        Reserva(id=None, cancha_id=1, cliente_id=1, fecha=hoy, hora_inicio=9, hora_fin=10, total=30.0, estado="Confirmada"),
        Reserva(id=None, cancha_id=2, cliente_id=2, fecha=hoy, hora_inicio=14, hora_fin=16, total=100.0, estado="Confirmada"),
        Reserva(id=None, cancha_id=3, cliente_id=3, fecha=hoy, hora_inicio=18, hora_fin=20, total=160.0, estado="Confirmada")
    ]
    reserva_repo.seed(reservas_semilla)

def main():
    # 1. Inicializar base de datos
    initialize_sqlite_db(DB_FILE)

    # 2. Instanciar Repositorios (Detalles de persistencia)
    cancha_repo = SqliteCanchaRepository(DB_FILE)
    cliente_repo = SqliteClienteRepository(DB_FILE)
    reserva_repo = SqliteReservaRepository(DB_FILE)

    # 3. Correr semillas (seeding)
    run_seeding(cancha_repo, cliente_repo, reserva_repo)

    # 4. Instanciar el Servicio inyectando dependencias (Reglas de Negocio)
    reserva_service = ReservaService(
        cancha_repo=cancha_repo,
        cliente_repo=cliente_repo,
        reserva_repo=reserva_repo
    )

    # 5. Instanciar la capa de interfaz de usuario
    view = ConsoleView()

    # 6. Instanciar Controlador inyectando Servicio y Vista
    controller = MenuController(service=reserva_service, view=view)

    # 7. Ejecutar aplicación
    controller.run()

if __name__ == "__main__":
    main()
