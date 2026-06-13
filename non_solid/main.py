#!/usr/bin/env python3
import sqlite3
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

DB_FILE = "reservas.db"
console = Console()

def get_db_connection():
    """Retorna una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos con tablas y datos semilla si no existen."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Crear tablas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canchas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        precio_hora REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cancha_id INTEGER NOT NULL,
        cliente_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        hora_inicio INTEGER NOT NULL,
        hora_fin INTEGER NOT NULL,
        total REAL NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Confirmada',
        FOREIGN KEY(cancha_id) REFERENCES canchas(id),
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    );
    """)

    # Datos semilla para canchas si está vacía
    cursor.execute("SELECT COUNT(*) FROM canchas")
    if cursor.fetchone()[0] == 0:
        canchas_semilla = [
            ("Maracaná", "Fútbol 5", 30.0),
            ("Camp Nou", "Fútbol 7", 50.0),
            ("Wembley", "Fútbol 11", 80.0),
            ("San Siro", "Fútbol 5", 35.0),
            ("La Bombonera", "Fútbol 7", 55.0)
        ]
        cursor.executemany(
            "INSERT INTO canchas (nombre, tipo, precio_hora) VALUES (?, ?, ?)",
            canchas_semilla
        )

    # Datos semilla para clientes si está vacía
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        clientes_semilla = [
            ("Lionel Messi", "123456789", "messi@gmail.com"),
            ("Cristiano Ronaldo", "987654321", "cr7@gmail.com"),
            ("Neymar Jr", "555666777", "neymar@gmail.com")
        ]
        cursor.executemany(
            "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
            clientes_semilla
        )

    # Datos semilla para reservas para pruebas
    cursor.execute("SELECT COUNT(*) FROM reservas")
    if cursor.fetchone()[0] == 0:
        hoy = datetime.now().strftime("%Y-%m-%d")
        reservas_semilla = [
            (1, 1, hoy, 9, 10, 30.0, 'Confirmada'),
            (2, 2, hoy, 14, 16, 100.0, 'Confirmada'),
            (3, 3, hoy, 18, 20, 160.0, 'Confirmada')
        ]
        cursor.executemany(
            "INSERT INTO reservas (cancha_id, cliente_id, fecha, hora_inicio, hora_fin, total, estado) VALUES (?, ?, ?, ?, ?, ?, ?)",
            reservas_semilla
        )

    conn.commit()
    conn.close()

def mostrar_header():
    """Muestra el banner de la aplicación."""
    console.clear()
    banner = r"""
  ____                             ____
 / ___|  ___   ___  ___ ___ _ __  |  _ \ ___  ___  ___ _ ____   ____ _ ___
 \___ \ / _ \ / __|/ __/ _ \ '__| | |_) / _ \/ __|/ _ \ '__\ \ / / _` / __|
  ___) | (_) | (__| (_|  __/ |    |  _ <  __/\__ \  __/ |   \ V / (_| \__ \
 |____/ \___/ \___|\___\___|_|    |_| \_\___||___/\___|_|    \_/ \__,_|___/
    """
    console.print(Panel(Align.center(Text(banner, style="bold green")), subtitle="[bold yellow]Versión 1.0 (NO SOLID)[/bold yellow]", border_style="green"))

def validar_fecha(fecha_str):
    """Valida que la fecha tenga el formato YYYY-MM-DD y sea válida."""
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def ver_canchas_y_disponibilidad():
    """Consulta la disponibilidad de las canchas para una fecha dada."""
    mostrar_header()
    console.print("[bold cyan]>>> VER CANCHAS Y DISPONIBILIDAD[/bold cyan]\n")

    hoy = datetime.now().strftime("%Y-%m-%d")
    fecha = Prompt.ask("Ingrese la fecha a consultar (YYYY-MM-DD)", default=hoy)

    if not validar_fecha(fecha):
        console.print("[bold red]Error: Formato de fecha inválido. Use YYYY-MM-DD.[/bold red]")
        Prompt.ask("\nPresione Enter para continuar...")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener todas las canchas
    canchas = cursor.execute("SELECT * FROM canchas").fetchall()

    # Obtener reservas activas para la fecha seleccionada
    reservas = cursor.execute(
        "SELECT cancha_id, hora_inicio, hora_fin FROM reservas WHERE fecha = ? AND estado = 'Confirmada'",
        (fecha,)
    ).fetchall()

    conn.close()

    # Mapear reservas por cancha
    reservas_por_cancha = {cancha["id"]: [] for cancha in canchas}
    for r in reservas:
        reservas_por_cancha[r["cancha_id"]].append((r["hora_inicio"], r["hora_fin"]))

    # Crear tabla de disponibilidad
    table = Table(title=f"Disponibilidad de Canchas para el {fecha}", border_style="cyan", show_lines=True)
    table.add_column("ID", justify="center", style="yellow")
    table.add_column("Cancha", style="bold white")
    table.add_column("Tipo", style="green")
    table.add_column("Precio/h", justify="right", style="magenta")

    # Columnas de horas (08:00 a 22:00)
    for h in range(8, 22):
        table.add_column(f"{h:02d}:00", justify="center", style="blue")

    for cancha in canchas:
        cancha_id = cancha["id"]
        row = [
            str(cancha_id),
            cancha["nombre"],
            cancha["tipo"],
            f"${cancha['precio_hora']:.2f}"
        ]

        # Ocupación para esta cancha
        cancha_res = reservas_por_cancha[cancha_id]

        # Para cada hora entre 8 y 21
        for h in range(8, 22):
            ocupada = False
            for inicio, fin in cancha_res:
                if inicio <= h < fin:
                    ocupada = True
                    break

            if ocupada:
                # Ocupado (Rojo)
                row.append("[bold red]✖[/bold red]")
            else:
                # Libre (Verde)
                row.append("[bold green]●[/bold green]")

        table.add_row(*row)

    console.print(table)
    console.print("\nLeyenda: [bold green]●[/bold green] Libre  |  [bold red]✖[/bold red] Ocupado")
    Prompt.ask("\nPresione Enter para continuar...")

def registrar_cliente():
    """Registra un nuevo cliente en el sistema."""
    mostrar_header()
    console.print("[bold cyan]>>> REGISTRAR NUEVO CLIENTE[/bold cyan]\n")

    nombre = Prompt.ask("Nombre completo")
    if not nombre.strip():
        console.print("[bold red]Error: El nombre no puede estar vacío.[/bold red]")
        Prompt.ask("\nPresione Enter para continuar...")
        return

    telefono = Prompt.ask("Teléfono")
    if not telefono.strip():
        console.print("[bold red]Error: El teléfono no puede estar vacío.[/bold red]")
        Prompt.ask("\nPresione Enter para continuar...")
        return

    email = Prompt.ask("Correo electrónico (email)")
    if not email.strip() or "@" not in email:
        console.print("[bold red]Error: Correo electrónico inválido.[/bold red]")
        Prompt.ask("\nPresione Enter para continuar...")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
            (nombre.strip(), telefono.strip(), email.strip().lower())
        )
        conn.commit()
        cliente_id = cursor.lastrowid
        console.print(f"\n[bold green]✓ Cliente registrado con éxito (ID: {cliente_id})[/bold green]")
    except sqlite3.IntegrityError:
        console.print(f"\n[bold red]Error: El correo electrónico '{email}' ya está registrado.[/bold red]")
    finally:
        conn.close()

    Prompt.ask("\nPresione Enter para continuar...")

def crear_reserva():
    """Crea una reserva de cancha en el sistema."""
    mostrar_header()
    console.print("[bold cyan]>>> CREAR NUEVA RESERVA[/bold cyan]\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Seleccionar Cliente
    clientes = cursor.execute("SELECT * FROM clientes").fetchall()
    if not clientes:
        console.print("[bold yellow]No hay clientes registrados en el sistema. Regístre uno primero.[/bold yellow]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    table_cli = Table(title="Clientes Registrados", border_style="yellow")
    table_cli.add_column("ID", justify="center", style="yellow")
    table_cli.add_column("Nombre", style="bold")
    table_cli.add_column("Email", style="green")

    for cli in clientes:
        table_cli.add_row(str(cli["id"]), cli["nombre"], cli["email"])

    console.print(table_cli)

    cliente_id = IntPrompt.ask("\nIngrese el ID del cliente")
    cliente = cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    if not cliente:
        console.print("[bold red]Error: ID de cliente no existe.[/bold red]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    # 2. Seleccionar Cancha
    canchas = cursor.execute("SELECT * FROM canchas").fetchall()
    table_can = Table(title="Canchas Disponibles", border_style="magenta")
    table_can.add_column("ID", justify="center", style="magenta")
    table_can.add_column("Nombre", style="bold")
    table_can.add_column("Tipo", style="green")
    table_can.add_column("Precio/Hora", style="yellow")

    for can in canchas:
        table_can.add_row(str(can["id"]), can["nombre"], can["tipo"], f"${can['precio_hora']:.2f}")

    console.print("\n")
    console.print(table_can)

    cancha_id = IntPrompt.ask("\nIngrese el ID de la cancha")
    cancha = cursor.execute("SELECT * FROM canchas WHERE id = ?", (cancha_id,)).fetchone()
    if not cancha:
        console.print("[bold red]Error: ID de cancha no existe.[/bold red]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    # 3. Ingresar Detalles del Horario
    hoy = datetime.now().strftime("%Y-%m-%d")
    fecha = Prompt.ask("\nIngrese la fecha de la reserva (YYYY-MM-DD)", default=hoy)
    if not validar_fecha(fecha):
        console.print("[bold red]Error: Formato de fecha inválido.[/bold red]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    console.print("\n[italic yellow]* Rango permitido: 08:00 a 22:00 (Hora inicio de 8 a 21)[/italic yellow]")
    hora_inicio = IntPrompt.ask("Ingrese la hora de inicio (Ej: 14 para las 14:00)")
    if hora_inicio < 8 or hora_inicio > 21:
        console.print("[bold red]Error: La hora de inicio debe estar entre 8 y 21.[/bold red]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    duracion = IntPrompt.ask("Ingrese la duración en horas (1 a 4)", default=1)
    if duracion < 1 or duracion > 4:
        console.print("[bold red]Error: La duración de la reserva debe ser de entre 1 y 4 horas.[/bold red]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    hora_fin = hora_inicio + duracion
    if hora_fin > 22:
        console.print(f"[bold red]Error: La reserva excede el horario límite (22:00). Finalizaría a las {hora_fin}:00.[/bold red]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    # 4. Validar disponibilidad (Traslapes)
    # Buscamos reservas activas de la misma cancha el mismo día donde:
    # hora_inicio < r.hora_fin Y hora_fin > r.hora_inicio
    conflictos = cursor.execute("""
        SELECT r.*, c.nombre as cliente_nombre FROM reservas r
        JOIN clientes c ON r.cliente_id = c.id
        WHERE r.cancha_id = ?
          AND r.fecha = ?
          AND r.estado = 'Confirmada'
          AND r.hora_inicio < ?
          AND r.hora_fin > ?
    """, (cancha_id, fecha, hora_fin, hora_inicio)).fetchall()

    if conflictos:
        console.print(f"\n[bold red]Error: La cancha ya está reservada en ese horario.[/bold red]")
        for c in conflictos:
            console.print(f"  - Conflicto: Reserva #{c['id']} ({c['cliente_nombre']}) de {c['hora_inicio']:02d}:00 a {c['hora_fin']:02d}:00")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    # 5. Confirmar y Registrar
    total = duracion * cancha["precio_hora"]

    resumen_text = Text()
    resumen_text.append("Cliente: ", style="bold")
    resumen_text.append(f"{cliente['nombre']}\n")
    resumen_text.append("Cancha: ", style="bold")
    resumen_text.append(f"{cancha['nombre']} ({cancha['tipo']})\n")
    resumen_text.append("Fecha: ", style="bold")
    resumen_text.append(f"{fecha}\n")
    resumen_text.append("Horario: ", style="bold")
    resumen_text.append(f"{hora_inicio:02d}:00 a {hora_fin:02d}:00 ({duracion} hora/s)\n")
    resumen_text.append("Costo por Hora: ", style="bold")
    resumen_text.append(f"${cancha['precio_hora']:.2f}\n")
    resumen_text.append("TOTAL A PAGAR: ", style="bold yellow")
    resumen_text.append(f"${total:.2f}", style="bold green")

    console.print("\n")
    console.print(Panel(resumen_text, title="[bold cyan]Resumen de la Reserva[/bold cyan]", border_style="cyan"))

    confirmar = Confirm.ask("¿Confirmar y guardar la reserva?", default=True)
    if confirmar:
        cursor.execute("""
            INSERT INTO reservas (cancha_id, cliente_id, fecha, hora_inicio, hora_fin, total, estado)
            VALUES (?, ?, ?, ?, ?, ?, 'Confirmada')
        """, (cancha_id, cliente_id, fecha, hora_inicio, hora_fin, total))
        conn.commit()
        reserva_id = cursor.lastrowid
        console.print(f"\n[bold green]✓ Reserva #{reserva_id} guardada con éxito.[/bold green]")
    else:
        console.print("\n[bold yellow]Reserva cancelada por el usuario.[/bold yellow]")

    conn.close()
    Prompt.ask("\nPresione Enter para continuar...")

def ver_reservas_activas():
    """Muestra todas las reservas confirmadas (activas)."""
    mostrar_header()
    console.print("[bold cyan]>>> VER RESERVAS ACTIVAS[/bold cyan]\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    reservas = cursor.execute("""
        SELECT r.id, c.nombre as cancha_nombre, cl.nombre as cliente_nombre,
               r.fecha, r.hora_inicio, r.hora_fin, r.total
        FROM reservas r
        JOIN canchas c ON r.cancha_id = c.id
        JOIN clientes cl ON r.cliente_id = cl.id
        WHERE r.estado = 'Confirmada'
        ORDER BY r.fecha ASC, r.hora_inicio ASC
    """).fetchall()

    conn.close()

    if not reservas:
        console.print("[bold yellow]No hay reservas activas registradas.[/bold yellow]")
        Prompt.ask("\nPresione Enter para continuar...")
        return

    table = Table(title="Reservas Activas", border_style="green")
    table.add_column("ID", justify="center", style="yellow")
    table.add_column("Cliente", style="bold")
    table.add_column("Cancha", style="magenta")
    table.add_column("Fecha", justify="center", style="cyan")
    table.add_column("Horario", justify="center", style="blue")
    table.add_column("Total", justify="right", style="green")

    for r in reservas:
        horario = f"{r['hora_inicio']:02d}:00 - {r['hora_fin']:02d}:00"
        table.add_row(
            str(r["id"]),
            r["cliente_nombre"],
            r["cancha_nombre"],
            r["fecha"],
            horario,
            f"${r['total']:.2f}"
        )

    console.print(table)
    Prompt.ask("\nPresione Enter para continuar...")

def cancelar_reserva():
    """Cancela una reserva cambiando su estado a 'Cancelada'."""
    mostrar_header()
    console.print("[bold cyan]>>> CANCELAR RESERVA[/bold cyan]\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Pedir ID de reserva
    reserva_id = IntPrompt.ask("Ingrese el ID de la reserva a cancelar")

    reserva = cursor.execute("""
        SELECT r.*, c.nombre as cancha_nombre, cl.nombre as cliente_nombre
        FROM reservas r
        JOIN canchas c ON r.cancha_id = c.id
        JOIN clientes cl ON r.cliente_id = cl.id
        WHERE r.id = ?
    """, (reserva_id,)).fetchone()

    if not reserva:
        console.print("[bold red]Error: No se encontró la reserva con ese ID.[/bold red]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    if reserva["estado"] == 'Cancelada':
        console.print("[bold yellow]La reserva ya se encuentra cancelada.[/bold yellow]")
        conn.close()
        Prompt.ask("\nPresione Enter para continuar...")
        return

    # Mostrar detalles de la reserva a cancelar
    resumen_text = Text()
    resumen_text.append("ID Reserva: ", style="bold")
    resumen_text.append(f"{reserva['id']}\n")
    resumen_text.append("Cliente: ", style="bold")
    resumen_text.append(f"{reserva['cliente_nombre']}\n")
    resumen_text.append("Cancha: ", style="bold")
    resumen_text.append(f"{reserva['cancha_nombre']}\n")
    resumen_text.append("Fecha: ", style="bold")
    resumen_text.append(f"{reserva['fecha']}\n")
    resumen_text.append("Horario: ", style="bold")
    resumen_text.append(f"{reserva['hora_inicio']:02d}:00 a {reserva['hora_fin']:02d}:00\n")
    resumen_text.append("Total: ", style="bold")
    resumen_text.append(f"${reserva['total']:.2f}\n")

    console.print(Panel(resumen_text, title="[bold red]Reserva a Cancelar[/bold red]", border_style="red"))

    confirmar = Confirm.ask("¿Está seguro de que desea cancelar esta reserva?", default=False)
    if confirmar:
        cursor.execute("UPDATE reservas SET estado = 'Cancelada' WHERE id = ?", (reserva_id,))
        conn.commit()
        console.print("\n[bold green]✓ La reserva ha sido cancelada exitosamente. El horario ahora está libre.[/bold green]")
    else:
        console.print("\n[bold yellow]Operación cancelada.[/bold yellow]")

    conn.close()
    Prompt.ask("\nPresione Enter para continuar...")

def reporte_ingresos():
    """Genera reportes de ingresos y estadísticas del negocio."""
    mostrar_header()
    console.print("[bold cyan]>>> REPORTE DE INGRESOS Y ESTADÍSTICAS[/bold cyan]\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Ingresos Totales (Solo confirmadas)
    total_ingresos = cursor.execute(
        "SELECT SUM(total) FROM reservas WHERE estado = 'Confirmada'"
    ).fetchone()[0] or 0.0

    # 2. Reservas por cancha
    canchas_stats = cursor.execute("""
        SELECT c.nombre, COUNT(r.id) as total_reservas, SUM(r.total) as total_recaudado
        FROM canchas c
        LEFT JOIN reservas r ON c.id = r.cancha_id AND r.estado = 'Confirmada'
        GROUP BY c.id
        ORDER BY total_reservas DESC
    """).fetchall()

    # 3. Cliente con más reservas
    top_cliente = cursor.execute("""
        SELECT cl.nombre, COUNT(r.id) as total_reservas, SUM(r.total) as total_gastado
        FROM clientes cl
        JOIN reservas r ON cl.id = r.cliente_id
        WHERE r.estado = 'Confirmada'
        GROUP BY cl.id
        ORDER BY total_reservas DESC
        LIMIT 1
    """).fetchone()

    # 4. Total de reservas por estado
    res_activas = cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'Confirmada'").fetchone()[0]
    res_canceladas = cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'Cancelada'").fetchone()[0]

    conn.close()

    # Construcción de la interfaz de reporte
    general_info = Text()
    general_info.append("INGRESOS TOTALES: ", style="bold")
    general_info.append(f"${total_ingresos:.2f}\n", style="bold green")
    general_info.append("Reservas Activas: ", style="bold")
    general_info.append(f"{res_activas}\n", style="green")
    general_info.append("Reservas Canceladas: ", style="bold")
    general_info.append(f"{res_canceladas}\n", style="red")

    panel_general = Panel(general_info, title="[bold cyan]Resumen Financiero[/bold cyan]", border_style="cyan")

    # Cliente top
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

    # Mostrar fila superior
    console.print(Columns([panel_general, panel_cliente]))
    console.print("\n")

    # Tabla de Canchas
    table_canchas = Table(title="Rendimiento por Cancha", border_style="magenta")
    table_canchas.add_column("Cancha", style="bold")
    table_canchas.add_column("Reservas Realizadas", justify="center", style="blue")
    table_canchas.add_column("Ingresos Generados", justify="right", style="green")

    for c in canchas_stats:
        recaudado = c["total_recaudado"] or 0.0
        table_canchas.add_row(c["nombre"], str(c["total_reservas"]), f"${recaudado:.2f}")

    console.print(table_canchas)
    Prompt.ask("\nPresione Enter para continuar...")

def main():
    init_db()

    while True:
        mostrar_header()

        menu_text = """[bold white]Seleccione una opción del menú:[/bold white]
[bold green]1.[/bold green] Ver Canchas y Disponibilidad
[bold green]2.[/bold green] Registrar Cliente
[bold green]3.[/bold green] Crear Reserva
[bold green]4.[/bold green] Ver Reservas Activas
[bold green]5.[/bold green] Cancelar Reserva
[bold green]6.[/bold green] Reporte de Ingresos y Estadísticas
[bold red]7. Salir[/bold red]"""

        console.print(Panel(menu_text, border_style="white", title="[bold blue]MENÚ PRINCIPAL[/bold blue]"))

        opcion = Prompt.ask("\nOpción", choices=["1", "2", "3", "4", "5", "6", "7"])

        if opcion == "1":
            ver_canchas_y_disponibilidad()
        elif opcion == "2":
            registrar_cliente()
        elif opcion == "3":
            crear_reserva()
        elif opcion == "4":
            ver_reservas_activas()
        elif opcion == "5":
            cancelar_reserva()
        elif opcion == "6":
            reporte_ingresos()
        elif opcion == "7":
            mostrar_header()
            console.print("\n[bold yellow]¡Gracias por usar el Sistema de Reservas! ¡Hasta luego![/bold yellow]\n")
            sys.exit(0)

if __name__ == "__main__":
    main()
