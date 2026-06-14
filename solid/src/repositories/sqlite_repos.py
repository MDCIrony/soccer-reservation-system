import sqlite3
from typing import List, Optional
from src.interfaces import ICanchaRepository, IClienteRepository, IReservaRepository
from src.models import Cancha, Cliente, Reserva

def initialize_sqlite_db(db_path: str):
    """Crea las tablas en la base de datos si no existen."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()


class SqliteCanchaRepository(ICanchaRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all(self) -> List[Cancha]:
        conn = self._get_connection()
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM canchas").fetchall()
        conn.close()
        return [Cancha(id=r["id"], nombre=r["nombre"], tipo=r["tipo"], precio_hora=r["precio_hora"]) for r in rows]

    def get_by_id(self, id: int) -> Optional[Cancha]:
        conn = self._get_connection()
        cursor = conn.cursor()
        row = cursor.execute("SELECT * FROM canchas WHERE id = ?", (id,)).fetchone()
        conn.close()
        if row:
            return Cancha(id=row["id"], nombre=row["nombre"], tipo=row["tipo"], precio_hora=row["precio_hora"])
        return None

    def seed(self, canchas: List[Cancha]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        count = cursor.execute("SELECT COUNT(*) FROM canchas").fetchone()[0]
        if count == 0:
            cursor.executemany(
                "INSERT INTO canchas (nombre, tipo, precio_hora) VALUES (?, ?, ?)",
                [(c.nombre, c.tipo, c.precio_hora) for c in canchas]
            )
            conn.commit()
        conn.close()


class SqliteClienteRepository(IClienteRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all(self) -> List[Cliente]:
        conn = self._get_connection()
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM clientes").fetchall()
        conn.close()
        return [Cliente(id=r["id"], nombre=r["nombre"], telefono=r["telefono"], email=r["email"]) for r in rows]

    def get_by_id(self, id: int) -> Optional[Cliente]:
        conn = self._get_connection()
        cursor = conn.cursor()
        row = cursor.execute("SELECT * FROM clientes WHERE id = ?", (id,)).fetchone()
        conn.close()
        if row:
            return Cliente(id=row["id"], nombre=row["nombre"], telefono=row["telefono"], email=row["email"])
        return None

    def get_by_email(self, email: str) -> Optional[Cliente]:
        conn = self._get_connection()
        cursor = conn.cursor()
        row = cursor.execute("SELECT * FROM clientes WHERE email = ?", (email.strip().lower(),)).fetchone()
        conn.close()
        if row:
            return Cliente(id=row["id"], nombre=row["nombre"], telefono=row["telefono"], email=row["email"])
        return None

    def save(self, cliente: Cliente) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
            (cliente.nombre, cliente.telefono, cliente.email.lower())
        )
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def seed(self, clientes: List[Cliente]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        count = cursor.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        if count == 0:
            cursor.executemany(
                "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
                [(c.nombre, c.telefono, c.email.lower()) for c in clientes]
            )
            conn.commit()
        conn.close()


class SqliteReservaRepository(IReservaRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_active(self) -> List[Reserva]:
        conn = self._get_connection()
        cursor = conn.cursor()
        rows = cursor.execute("""
            SELECT r.*, c.nombre as cancha_nombre, cl.nombre as cliente_nombre
            FROM reservas r
            JOIN canchas c ON r.cancha_id = c.id
            JOIN clientes cl ON r.cliente_id = cl.id
            WHERE r.estado = 'Confirmada'
            ORDER BY r.fecha ASC, r.hora_inicio ASC
        """).fetchall()
        conn.close()

        reservas = []
        for r in rows:
            res = Reserva(
                id=r["id"],
                cancha_id=r["cancha_id"],
                cliente_id=r["cliente_id"],
                fecha=r["fecha"],
                hora_inicio=r["hora_inicio"],
                hora_fin=r["hora_fin"],
                total=r["total"],
                estado=r["estado"]
            )
            res.cancha_nombre = r["cancha_nombre"]
            res.cliente_nombre = r["cliente_nombre"]
            reservas.append(res)
        return reservas

    def get_by_id(self, id: int) -> Optional[Reserva]:
        conn = self._get_connection()
        cursor = conn.cursor()
        row = cursor.execute("""
            SELECT r.*, c.nombre as cancha_nombre, cl.nombre as cliente_nombre
            FROM reservas r
            JOIN canchas c ON r.cancha_id = c.id
            JOIN clientes cl ON r.cliente_id = cl.id
            WHERE r.id = ?
        """, (id,)).fetchone()
        conn.close()
        if row:
            res = Reserva(
                id=row["id"],
                cancha_id=row["cancha_id"],
                cliente_id=row["cliente_id"],
                fecha=row["fecha"],
                hora_inicio=row["hora_inicio"],
                hora_fin=row["hora_fin"],
                total=row["total"],
                estado=row["estado"]
            )
            res.cancha_nombre = row["cancha_nombre"]
            res.cliente_nombre = row["cliente_nombre"]
            return res
        return None

    def get_by_date(self, fecha: str) -> List[Reserva]:
        conn = self._get_connection()
        cursor = conn.cursor()
        rows = cursor.execute("""
            SELECT r.*, c.nombre as cancha_nombre, cl.nombre as cliente_nombre
            FROM reservas r
            JOIN canchas c ON r.cancha_id = c.id
            JOIN clientes cl ON r.cliente_id = cl.id
            WHERE r.fecha = ? AND r.estado = 'Confirmada'
        """, (fecha,)).fetchall()
        conn.close()

        reservas = []
        for r in rows:
            res = Reserva(
                id=r["id"],
                cancha_id=r["cancha_id"],
                cliente_id=r["cliente_id"],
                fecha=r["fecha"],
                hora_inicio=r["hora_inicio"],
                hora_fin=r["hora_fin"],
                total=r["total"],
                estado=r["estado"]
            )
            res.cancha_nombre = r["cancha_nombre"]
            res.cliente_nombre = r["cliente_nombre"]
            reservas.append(res)
        return reservas

    def check_overlap(self, cancha_id: int, fecha: str, hora_inicio: int, hora_fin: int) -> List[Reserva]:
        conn = self._get_connection()
        cursor = conn.cursor()
        rows = cursor.execute("""
            SELECT r.*, cl.nombre as cliente_nombre
            FROM reservas r
            JOIN clientes cl ON r.cliente_id = cl.id
            WHERE r.cancha_id = ?
              AND r.fecha = ?
              AND r.estado = 'Confirmada'
              AND r.hora_inicio < ?
              AND r.hora_fin > ?
        """, (cancha_id, fecha, hora_fin, hora_inicio)).fetchall()
        conn.close()

        conflictos = []
        for r in rows:
            res = Reserva(
                id=r["id"],
                cancha_id=r["cancha_id"],
                cliente_id=r["cliente_id"],
                fecha=r["fecha"],
                hora_inicio=r["hora_inicio"],
                hora_fin=r["hora_fin"],
                total=r["total"],
                estado=r["estado"]
            )
            res.cliente_nombre = r["cliente_nombre"]
            conflictos.append(res)
        return conflictos

    def save(self, reserva: Reserva) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reservas (cancha_id, cliente_id, fecha, hora_inicio, hora_fin, total, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (reserva.cancha_id, reserva.cliente_id, reserva.fecha,
              reserva.hora_inicio, reserva.hora_fin, reserva.total, reserva.estado))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def cancel(self, id: int) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reservas SET estado = 'Cancelada' WHERE id = ?", (id,))
        conn.commit()
        conn.close()

    def get_financial_stats(self) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()

        # 1. Ingresos Totales
        total_ingresos = cursor.execute(
            "SELECT SUM(total) FROM reservas WHERE estado = 'Confirmada'"
        ).fetchone()[0] or 0.0

        # 2. Reservas por cancha
        canchas_stats_rows = cursor.execute("""
            SELECT c.nombre, COUNT(r.id) as total_reservas, SUM(r.total) as total_recaudado
            FROM canchas c
            LEFT JOIN reservas r ON c.id = r.cancha_id AND r.estado = 'Confirmada'
            GROUP BY c.id
            ORDER BY total_reservas DESC
        """).fetchall()

        canchas_stats = [
            {
                "nombre": r["nombre"],
                "total_reservas": r["total_reservas"],
                "total_recaudado": r["total_recaudado"] or 0.0
            }
            for r in canchas_stats_rows
        ]

        # 3. Cliente con más reservas
        top_cliente_row = cursor.execute("""
            SELECT cl.nombre, COUNT(r.id) as total_reservas, SUM(r.total) as total_gastado
            FROM clientes cl
            JOIN reservas r ON cl.id = r.cliente_id
            WHERE r.estado = 'Confirmada'
            GROUP BY cl.id
            ORDER BY total_reservas DESC
            LIMIT 1
        """).fetchone()

        top_cliente = None
        if top_cliente_row:
            top_cliente = {
                "nombre": top_cliente_row["nombre"],
                "total_reservas": top_cliente_row["total_reservas"],
                "total_gastado": top_cliente_row["total_gastado"]
            }

        # 4. Conteos
        res_activas = cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'Confirmada'").fetchone()[0]
        res_canceladas = cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'Cancelada'").fetchone()[0]

        conn.close()

        return {
            "total_ingresos": total_ingresos,
            "canchas_stats": canchas_stats,
            "top_cliente": top_cliente,
            "res_activas": res_activas,
            "res_canceladas": res_canceladas
        }

    def seed(self, reservas: List[Reserva]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        count = cursor.execute("SELECT COUNT(*) FROM reservas").fetchone()[0]
        if count == 0:
            cursor.executemany("""
                INSERT INTO reservas (cancha_id, cliente_id, fecha, hora_inicio, hora_fin, total, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [(r.cancha_id, r.cliente_id, r.fecha, r.hora_inicio, r.hora_fin, r.total, r.estado) for r in reservas])
            conn.commit()
        conn.close()
