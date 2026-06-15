import sys
from datetime import datetime
from rich.prompt import Prompt, IntPrompt, Confirm
from src.services.reserva_service import ReservaService
from src.interfaces import IReservationView
from src.models import Cliente, Cancha, Reserva

class MenuController:
    def __init__(self, service: ReservaService, view: IReservationView):
        self.service = service
        self.view = view

    def run(self):
        """Bucle principal de ejecución del menú."""
        while True:
            self.view.mostrar_header()
            self.view.mostrar_menu_principal()

            opcion = Prompt.ask("\nSeleccione una opción", choices=["1", "2", "3", "4", "5", "6", "7"])

            if opcion == "1":
                self.ejecutar_ver_canchas_y_disponibilidad()
            elif opcion == "2":
                self.ejecutar_registrar_cliente()
            elif opcion == "3":
                self.ejecutar_crear_reserva()
            elif opcion == "4":
                self.ejecutar_ver_reservas_activas()
            elif opcion == "5":
                self.ejecutar_cancelar_reserva()
            elif opcion == "6":
                self.ejecutar_reporte_ingresos()
            elif opcion == "7":
                self.view.mostrar_header()
                self.view.mostrar_mensaje_info("¡Gracias por utilizar el Sistema de Reservas! ¡Hasta luego!\n")
                sys.exit(0)

    def ejecutar_ver_canchas_y_disponibilidad(self):
        self.view.mostrar_header()
        self.view.console.print("[bold cyan]>>> VER CANCHAS Y DISPONIBILIDAD[/bold cyan]\n")

        hoy = datetime.now().strftime("%Y-%m-%d")
        fecha = Prompt.ask("Ingrese la fecha a consultar (YYYY-MM-DD)", default=hoy)

        try:
            disponibilidad = self.service.obtener_canchas_disponibilidad(fecha)
            self.view.mostrar_canchas_disponibilidad(fecha, disponibilidad)
        except ValueError as e:
            self.view.mostrar_mensaje_error(str(e))

        Prompt.ask("\nPresione Enter para continuar...")

    def ejecutar_registrar_cliente(self):
        self.view.mostrar_header()
        self.view.console.print("[bold cyan]>>> REGISTRAR NUEVO CLIENTE[/bold cyan]\n")

        nombre = Prompt.ask("Nombre completo")
        telefono = Prompt.ask("Teléfono")
        email = Prompt.ask("Correo electrónico (email)")

        try:
            cliente = self.service.registrar_cliente(nombre, telefono, email)
            self.view.mostrar_mensaje_exito(f"Cliente registrado con éxito (ID: {cliente.id})")
        except ValueError as e:
            self.view.mostrar_mensaje_error(str(e))

        Prompt.ask("\nPresione Enter para continuar...")

    def ejecutar_crear_reserva(self):
        self.view.mostrar_header()
        self.view.console.print("[bold cyan]>>> CREAR NUEVA RESERVA[/bold cyan]\n")

        # 1. Obtener y mostrar clientes para selección
        clientes = self.service.obtener_clientes()
        if not clientes:
            self.view.mostrar_mensaje_info("No hay clientes registrados en el sistema. Regístre uno primero.")
            Prompt.ask("\nPresione Enter para continuar...")
            return

        self.view.mostrar_clientes(clientes)
        cliente_id = IntPrompt.ask("\nIngrese el ID del cliente")

        # Validar existencia del cliente antes de continuar en UI
        cliente_valido = False
        for c in clientes:
            if c.id == cliente_id:
                cliente_valido = True
                nombre_cliente = c.nombre
                break
        if not cliente_valido:
            self.view.mostrar_mensaje_error("El ID de cliente ingresado no existe.")
            Prompt.ask("\nPresione Enter para continuar...")
            return

        # 2. Obtener y mostrar canchas para selección
        canchas = self.service.obtener_canchas()
        self.view.console.print("\n")
        self.view.mostrar_canchas(canchas)
        cancha_id = IntPrompt.ask("\nIngrese el ID de la cancha")

        cancha_valida = None
        for c in canchas:
            if c.id == cancha_id:
                cancha_valida = c
                break
        if not cancha_valida:
            self.view.mostrar_mensaje_error("El ID de cancha ingresado no existe.")
            Prompt.ask("\nPresione Enter para continuar...")
            return

        # 3. Datos del Horario
        hoy = datetime.now().strftime("%Y-%m-%d")
        fecha = Prompt.ask("\nIngrese la fecha de la reserva (YYYY-MM-DD)", default=hoy)

        self.view.console.print("\n[italic yellow]* Rango permitido: 08:00 a 22:00 (Hora inicio de 8 a 21)[/italic yellow]")
        hora_inicio = IntPrompt.ask("Ingrese la hora de inicio (Ej: 14 para las 14:00)")
        duracion = IntPrompt.ask("Ingrese la duración en horas (1 a 4)", default=1)

        hora_fin = hora_inicio + duracion
        total_pago = duracion * cancha_valida.precio_hora

        # Mostrar resumen previo a confirmación
        self.view.mostrar_resumen_reserva(
            cliente_nombre=nombre_cliente,
            cancha_nombre=cancha_valida.nombre,
            cancha_tipo=cancha_valida.tipo,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion=duracion,
            precio_hora=cancha_valida.precio_hora,
            total=total_pago
        )

        confirmar = Confirm.ask("¿Confirmar y guardar la reserva?", default=True)
        if confirmar:
            try:
                reserva = self.service.crear_reserva(
                    cliente_id=cliente_id,
                    cancha_id=cancha_id,
                    fecha=fecha,
                    hora_inicio=hora_inicio,
                    duracion=duracion
                )
                self.view.mostrar_mensaje_exito(f"Reserva #{reserva.id} guardada con éxito.")
            except ValueError as e:
                self.view.mostrar_mensaje_error(str(e))
        else:
            self.view.mostrar_mensaje_info("Reserva cancelada por el usuario.")

        Prompt.ask("\nPresione Enter para continuar...")

    def ejecutar_ver_reservas_activas(self):
        try:
            reservas = self.service.obtener_reservas_activas()
            self.view.mostrar_reservas_activas(reservas)
        except Exception as e:
            self.view.mostrar_mensaje_error(f"Error al obtener reservas: {str(e)}")

        Prompt.ask("\nPresione Enter para continuar...")

    def ejecutar_cancelar_reserva(self):
        self.view.mostrar_header()
        self.view.console.print("[bold cyan]>>> CANCELAR RESERVA[/bold cyan]\n")

        reserva_id = IntPrompt.ask("Ingrese el ID de la reserva a cancelar")

        # Buscar reserva para mostrar detalles de confirmación
        reservas = self.service.obtener_reservas_activas()
        reserva_a_cancelar = None
        for r in reservas:
            if r.id == reserva_id:
                reserva_a_cancelar = r
                break

        if not reserva_a_cancelar:
            self.view.mostrar_mensaje_error("No se encontró una reserva activa con ese ID.")
            Prompt.ask("\nPresione Enter para continuar...")
            return

        self.view.mostrar_detalles_cancelacion(reserva_a_cancelar)

        confirmar = Confirm.ask("¿Está seguro de que desea cancelar esta reserva?", default=False)
        if confirmar:
            try:
                self.service.cancelar_reserva(reserva_id)
                self.view.mostrar_mensaje_exito("La reserva ha sido cancelada exitosamente. El horario ahora está libre.")
            except ValueError as e:
                self.view.mostrar_mensaje_error(str(e))
        else:
            self.view.mostrar_mensaje_info("Operación cancelada.")

        Prompt.ask("\nPresione Enter para continuar...")

    def ejecutar_reporte_ingresos(self):
        try:
            stats = self.service.obtener_reporte_estadisticas()
            self.view.mostrar_reporte_estadisticas(stats)
        except Exception as e:
            self.view.mostrar_mensaje_error(f"Error al generar el reporte: {str(e)}")

        Prompt.ask("\nPresione Enter para continuar...")
