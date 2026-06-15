from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from src.interfaces import IReservationView
from src.models import Cancha, Cliente, Reserva

class ConsoleView(IReservationView):
    def __init__(self):
        self.console = Console()

    def clear(self):
        self.console.clear()

    def mostrar_header(self):
        """Muestra el banner principal de la aplicación."""
        self.clear()
        banner = r"""
  ____                             ____
 / ___|  ___   ___  ___ ___ _ __  |  _ \ ___  ___  ___ _ ____   ____ _ ___
 \___ \ / _ \ / __|/ __/ _ \ '__| | |_) / _ \/ __|/ _ \ '__\ \ / / _` / __|
  ___) | (_) | (__| (_|  __/ |    |  _ <  __/\__ \  __/ |   \ V / (_| \__ \
 |____/ \___/ \___|\___\___|_|    |_| \_\___||___/\___|_|    \_/ \__,_|___/
        """
        self.console.print(
            Panel(
                Align.center(Text(banner, style="bold cyan")),
                subtitle="[bold yellow]Versión 2.0 (Aplicando SOLID y Limpio)[/bold yellow]",
                border_style="cyan"
            )
        )

    def mostrar_menu_principal(self):
        """Muestra el panel del menú principal."""
        menu_text = """[bold white]Seleccione una opción del menú:[/bold white]
[bold cyan]1.[/bold cyan] Ver Canchas y Disponibilidad
[bold cyan]2.[/bold cyan] Registrar Cliente
[bold cyan]3.[/bold cyan] Crear Reserva
[bold cyan]4.[/bold cyan] Ver Reservas Activas
[bold cyan]5.[/bold cyan] Cancelar Reserva
[bold cyan]6.[/bold cyan] Reporte de Ingresos y Estadísticas
[bold red]7. Salir[/bold red]"""
        self.console.print(Panel(menu_text, border_style="white", title="[bold blue]MENÚ PRINCIPAL[/bold blue]"))

    def mostrar_mensaje_exito(self, mensaje: str):
        """Muestra un mensaje de éxito en verde."""
        self.console.print(f"\n[bold green]✓ {mensaje}[/bold green]")

    def mostrar_mensaje_error(self, mensaje: str):
        """Muestra un mensaje de error en rojo."""
        self.console.print(f"\n[bold red]Error: {mensaje}[/bold red]")

    def mostrar_mensaje_info(self, mensaje: str):
        """Muestra un mensaje de información en amarillo."""
        self.console.print(f"\n[bold yellow]{mensaje}[/bold yellow]")

    def mostrar_canchas_disponibilidad(self, fecha: str, disponibilidad_canchas: List[Dict]):
        """Muestra la cuadrícula de disponibilidad horaria por cancha."""
        self.mostrar_header()
        self.console.print(f"[bold cyan]>>> DISPONIBILIDAD DE CANCHAS - FECHA: {fecha}[/bold cyan]\n")

        table = Table(border_style="cyan", show_lines=True)
        table.add_column("ID", justify="center", style="yellow")
        table.add_column("Cancha", style="bold white")
        table.add_column("Tipo", style="green")
        table.add_column("Precio/h", justify="right", style="magenta")

        # Columnas de horas (08:00 a 22:00)
        for h in range(8, 22):
            table.add_column(f"{h:02d}:00", justify="center", style="blue")

        for item in disponibilidad_canchas:
            cancha: Cancha = item["cancha"]
            disp: Dict[int, bool] = item["disponibilidad"]

            row = [
                str(cancha.id),
                cancha.nombre,
                cancha.tipo,
                f"${cancha.precio_hora:.2f}"
            ]

            for h in range(8, 22):
                if disp[h]:
                    # Libre (Verde)
                    row.append("[bold green]●[/bold green]")
                else:
                    # Ocupado (Rojo)
                    row.append("[bold red]✖[/bold red]")

            table.add_row(*row)

        self.console.print(table)
        self.console.print("\nLeyenda: [bold green]●[/bold green] Libre  |  [bold red]✖[/bold red] Ocupado")

    def mostrar_clientes(self, clientes: List[Cliente]):
        """Muestra la tabla de clientes."""
        table = Table(title="Clientes Registrados", border_style="yellow")
        table.add_column("ID", justify="center", style="yellow")
        table.add_column("Nombre", style="bold")
        table.add_column("Teléfono", style="white")
        table.add_column("Email", style="green")

        for cli in clientes:
            table.add_row(str(cli.id), cli.nombre, cli.telefono, cli.email)

        self.console.print(table)

    def mostrar_canchas(self, canchas: List[Cancha]):
        """Muestra la tabla de canchas."""
        table = Table(title="Canchas Disponibles", border_style="magenta")
        table.add_column("ID", justify="center", style="magenta")
        table.add_column("Nombre", style="bold")
        table.add_column("Tipo", style="green")
        table.add_column("Precio/Hora", style="yellow")

        for can in canchas:
            table.add_row(str(can.id), can.nombre, can.tipo, f"${can.precio_hora:.2f}")

        self.console.print(table)

    def mostrar_resumen_reserva(self, cliente_nombre: str, cancha_nombre: str, cancha_tipo: str, fecha: str, hora_inicio: int, hora_fin: int, duracion: int, precio_hora: float, total: float):
        """Muestra un panel con el resumen detallado de la reserva."""
        resumen_text = Text()
        resumen_text.append("Cliente: ", style="bold")
        resumen_text.append(f"{cliente_nombre}\n")
        resumen_text.append("Cancha: ", style="bold")
        resumen_text.append(f"{cancha_nombre} ({cancha_tipo})\n")
        resumen_text.append("Fecha: ", style="bold")
        resumen_text.append(f"{fecha}\n")
        resumen_text.append("Horario: ", style="bold")
        resumen_text.append(f"{hora_inicio:02d}:00 a {hora_fin:02d}:00 ({duracion} hora/s)\n")
        resumen_text.append("Costo por Hora: ", style="bold")
        resumen_text.append(f"${precio_hora:.2f}\n")
        resumen_text.append("TOTAL A PAGAR: ", style="bold yellow")
        resumen_text.append(f"${total:.2f}", style="bold green")

        self.console.print("\n")
        self.console.print(Panel(resumen_text, title="[bold cyan]Resumen de la Reserva[/bold cyan]", border_style="cyan"))

    def mostrar_reservas_activas(self, reservas: List[Reserva]):
        """Muestra la lista de reservas en formato de tabla."""
        self.mostrar_header()
        self.console.print("[bold cyan]>>> RESERVAS ACTIVAS[/bold cyan]\n")

        if not reservas:
            self.mostrar_mensaje_info("No hay reservas activas registradas.")
            return

        table = Table(title="Reservas Activas", border_style="green")
        table.add_column("ID", justify="center", style="yellow")
        table.add_column("Cliente", style="bold")
        table.add_column("Cancha", style="magenta")
        table.add_column("Fecha", justify="center", style="cyan")
        table.add_column("Horario", justify="center", style="blue")
        table.add_column("Total", justify="right", style="green")

        for r in reservas:
            horario = f"{r.hora_inicio:02d}:00 - {r.hora_fin:02d}:00"
            table.add_row(
                str(r.id),
                r.cliente_nombre or "N/A",
                r.cancha_nombre or "N/A",
                r.fecha,
                horario,
                f"${r.total:.2f}"
            )

        self.console.print(table)

    def mostrar_detalles_cancelacion(self, reserva: Reserva):
        """Muestra un panel con la reserva a punto de cancelar."""
        resumen_text = Text()
        resumen_text.append("ID Reserva: ", style="bold")
        resumen_text.append(f"{reserva.id}\n")
        resumen_text.append("Cliente: ", style="bold")
        resumen_text.append(f"{reserva.cliente_nombre}\n")
        resumen_text.append("Cancha: ", style="bold")
        resumen_text.append(f"{reserva.cancha_nombre}\n")
        resumen_text.append("Fecha: ", style="bold")
        resumen_text.append(f"{reserva.fecha}\n")
        resumen_text.append("Horario: ", style="bold")
        resumen_text.append(f"{reserva.hora_inicio:02d}:00 a {reserva.hora_fin:02d}:00\n")
        resumen_text.append("Total: ", style="bold")
        resumen_text.append(f"${reserva.total:.2f}\n")

        self.console.print(Panel(resumen_text, title="[bold red]Reserva a Cancelar[/bold red]", border_style="red"))

    def mostrar_reporte_estadisticas(self, stats: dict):
        """Muestra el panel de estadísticas financieras y métricas del negocio."""
        self.mostrar_header()
        self.console.print("[bold cyan]>>> REPORTE DE INGRESOS Y ESTADÍSTICAS[/bold cyan]\n")

        total_ingresos = stats["total_ingresos"]
        canchas_stats = stats["canchas_stats"]
        top_cliente = stats["top_cliente"]
        res_activas = stats["res_activas"]
        res_canceladas = stats["res_canceladas"]

        general_info = Text()
        general_info.append("INGRESOS TOTALES: ", style="bold")
        general_info.append(f"${total_ingresos:.2f}\n", style="bold green")
        general_info.append("Reservas Activas: ", style="bold")
        general_info.append(f"{res_activas}\n", style="green")
        general_info.append("Reservas Canceladas: ", style="bold")
        general_info.append(f"{res_canceladas}\n", style="red")

        panel_general = Panel(general_info, title="[bold cyan]Resumen Financiero[/bold cyan]", border_style="cyan")

        cliente_info = Text()
        if top_cliente:
            cliente_info.append("Cliente: ", style="bold")
            cliente_info.append(f"{top_cliente['nombre']}\n", style="white")
            cliente_info.append("Reservas: ", style="bold")
            cliente_info.append(f"{top_cliente['total_reservas']}\n", style="green")
            cliente_info.append("Total Invertido: ", style="bold")
            cliente_info.append(f"${top_cliente['total_gastado']:.2f}", style="green")
        else:
            cliente_info.append("No hay datos suficientes.")

        panel_cliente = Panel(cliente_info, title="[bold yellow]Cliente Estrella[/bold yellow]", border_style="yellow")

        self.console.print(Columns([panel_general, panel_cliente]))
        self.console.print("\n")

        table_canchas = Table(title="Rendimiento por Cancha", border_style="magenta")
        table_canchas.add_column("Cancha", style="bold")
        table_canchas.add_column("Reservas Realizadas", justify="center", style="blue")
        table_canchas.add_column("Ingresos Generados", justify="right", style="green")

        for c in canchas_stats:
            table_canchas.add_row(c["nombre"], str(c["total_reservas"]), f"${c['total_recaudado']:.2f}")

        self.console.print(table_canchas)
