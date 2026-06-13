# Especificaciones del Sistema de Reservas de Canchas de Fútbol

Este documento detalla los requerimientos, diseño de base de datos, reglas de negocio y la estructura del proyecto para el sistema de reservas de canchas de fútbol.

---

## 1. Estructura del Proyecto

El proyecto se dividirá en dos subproyectos independientes ubicados en la raíz del repositorio:

```text
soccer-reservation-system/
├── .docs/
│   └── specifications.md       # Este archivo
├── non_solid/                  # Versión 1: Sin aplicar SOLID
│   ├── app.py                  # Script principal monolithic
│   ├── pyproject.toml          # Configuración de uv para dependencias
│   └── reservas.db             # Base de datos SQLite local
└── solid/                      # Versión 2: Aplicando SOLID
    ├── src/                    # Módulos separados por responsabilidades
    ├── main.py                 # Punto de entrada
    ├── pyproject.toml          # Configuración de uv
    └── reservas.db             # Base de datos SQLite local
```

Ambos proyectos se gestionarán de forma independiente utilizando `uv`.

---

## 2. Requerimientos de Software y Base de Datos

El sistema utilizará **SQLite** como motor de base de datos relacional para persistir los datos de canchas, clientes y reservas.

### Esquema de Base de Datos (Tablas)

#### Tabla: `canchas`
Persiste los datos de las canchas disponibles para reservar.
*   `id`: INTEGER PRIMARY KEY AUTOINCREMENT
*   `nombre`: TEXT NOT NULL (Ej: "Maracaná", "Camp Nou")
*   `tipo`: TEXT NOT NULL (Ej: "Fútbol 5", "Fútbol 7", "Fútbol 11")
*   `precio_hora`: REAL NOT NULL (Ej: 30.0, 50.0)

#### Tabla: `clientes`
Persiste la información de contacto de los clientes.
*   `id`: INTEGER PRIMARY KEY AUTOINCREMENT
*   `nombre`: TEXT NOT NULL
*   `telefono`: TEXT NOT NULL
*   `email`: TEXT NOT NULL UNIQUE

#### Tabla: `reservas`
Registra las reservas realizadas.
*   `id`: INTEGER PRIMARY KEY AUTOINCREMENT
*   `cancha_id`: INTEGER NOT NULL (FK -> `canchas.id`)
*   `cliente_id`: INTEGER NOT NULL (FK -> `clientes.id`)
*   `fecha`: TEXT NOT NULL (Formato: `YYYY-MM-DD`)
*   `hora_inicio`: INTEGER NOT NULL (Formato de 24h, Ej: 8, 14, 21)
*   `hora_fin`: INTEGER NOT NULL (Formato de 24h, Ej: 9, 15, 22)
*   `total`: REAL NOT NULL (Cálculo: `(hora_fin - hora_inicio) * precio_hora`)
*   `estado`: TEXT NOT NULL DEFAULT 'Confirmada' ('Confirmada', 'Cancelada')

---

## 3. Reglas de Negocio

Para asegurar la consistencia del sistema, se deben cumplir estrictamente las siguientes reglas:

1.  **Horario de Operación**: Las canchas solo pueden reservarse en el rango de **08:00 a 22:00** (hora de inicio mínima: 8, hora de fin máxima: 22).
2.  **Bloques Horarios**: Las reservas se realizan en bloques de horas exactas (duración mínima de 1 hora, máxima de 4 horas por reserva).
3.  **Conflictos de Reserva (Disponibilidad)**: No se puede registrar una reserva si la cancha ya está ocupada en ese rango de fecha y hora.
    *   *Ejemplo*: Si la cancha A está reservada de 14:00 a 16:00 el día 2026-06-20, no se puede realizar otra reserva para la misma cancha de 15:00 a 16:00 o de 13:00 a 15:00 en esa fecha.
4.  **Cálculo de Tarifas**: El costo total se calcula automáticamente multiplicando la cantidad de horas por el `precio_hora` de la cancha seleccionada.
5.  **Cancelaciones**: Las reservas no se eliminan físicamente de la base de datos; su estado cambia a `'Cancelada'`. Una vez cancelada, el bloque horario de la cancha queda libre nuevamente.

---

## 4. Diseño de la Interfaz CLI

El sistema se controlará mediante una interfaz de consola enriquecida visualmente usando la librería `rich`.

### Menú Principal

```text
======================================================
     SISTEMA DE RESERVAS - CANCHAS DE FÚTBOL
======================================================
1. Ver Canchas y Disponibilidad
2. Registrar Cliente
3. Crear Reserva
4. Ver Reservas Activas
5. Cancelar Reserva
6. Reporte de Ingresos y Estadísticas
7. Salir
======================================================
Seleccione una opción:
```

### Funcionalidades del Menú

1.  **Ver Canchas y Disponibilidad**:
    *   Muestra una tabla con las canchas, su tipo y precio por hora.
    *   Permite ingresar una fecha (`YYYY-MM-DD`) para ver qué horarios están ocupados o libres.
2.  **Registrar Cliente**:
    *   Pide nombre, teléfono y correo electrónico. Valida que el email no esté duplicado.
3.  **Crear Reserva**:
    *   Muestra la lista de clientes para seleccionar uno (o buscar por ID/email).
    *   Muestra la lista de canchas para seleccionar una.
    *   Pide fecha (`YYYY-MM-DD`), hora de inicio (8 a 21) y duración en horas.
    *   Valida la disponibilidad de la cancha.
    *   Calcula el total, muestra un resumen para confirmación del usuario y guarda la reserva si es aceptada.
4.  **Ver Reservas Activas**:
    *   Muestra una tabla detallada con las reservas de estado 'Confirmada', indicando el nombre del cliente, la cancha, la fecha, el rango de horas y el total.
5.  **Cancelar Reserva**:
    *   Permite buscar una reserva activa por ID de reserva o cliente.
    *   Muestra los detalles de la reserva y pide confirmación para cancelarla.
6.  **Reporte de Ingresos y Estadísticas**:
    *   Muestra el total recaudado acumulado.
    *   Muestra estadísticas como:
        *   Cancha más popular/reservada.
        *   Ingresos generados por tipo de cancha.
        *   Cliente con más reservas.

---

## 5. Diferencias entre las Versiones

### Versión 1: NO SOLID (`non_solid/`)
*   **Diseño**: Todo en un único archivo (`app.py`) o estructura sumamente simplista.
*   **Características**:
    *   Mezcla directa de lógica de presentación (prints, inputs, tablas `rich`) con lógica de acceso a datos (consultas SQL directas `sqlite3.connect`) y lógica de negocio (validación de traslapes en el mismo método).
    *   Alto acoplamiento: si se decide cambiar SQLite por PostgreSQL o JSON, hay que reescribir todo el archivo.
    *   Fácil de leer para scripts rápidos, pero imposible de testear unitariamente sin mockear la base de datos real y la entrada del usuario.

### Versión 2: SOLID (`solid/`)
*   **Diseño**: Modular, siguiendo los principios SOLID.
*   **Principios Aplicados**:
    *   **Single Responsibility Principle (SRP)**: Clases separadas para el repositorio de datos (SQLite), la lógica de negocio (servicios de reserva) y la interfaz de usuario (CLI).
    *   **Open/Closed Principle (OCP)**: Interfaces o clases base abstractas para el almacenamiento. Si se desea cambiar SQLite por un archivo en memoria o JSON, se extiende sin modificar el servicio de reservas.
    *   **Liskov Substitution Principle (LSP)**: Cualquier implementación del repositorio (ej. `SqliteRepository`, `MemoryRepository`) puede ser sustituida sin romper la aplicación.
    *   **Interface Segregation Principle (ISP)**: Los clientes de una interfaz solo dependen de los métodos que realmente utilizan.
    *   **Dependency Inversion Principle (DIP)**: El servicio de reserva depende de abstracciones (interfaces de repositorio), no de detalles concretos (SQLite). Estas dependencias se inyectan en el constructor.
