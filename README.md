# Soccer Reservation System (Sistema de Reserva de Canchas)

Este proyecto contiene dos implementaciones independientes de un sistema de reservas de canchas de fútbol por CLI, diseñado en Python, con persistencia en base de datos SQLite y estilizado visualmente con la librería `rich`.

El objetivo de este repositorio es ilustrar la diferencia práctica de arquitectura, mantenibilidad y modularidad entre un código acoplado y un código que sigue rigurosamente los principios de diseño **SOLID**.

---

## Estructura del Repositorio

*   **[.docs/specifications.md](file:///.docs/specifications.md)**: Documento detallado de especificaciones, reglas de negocio y diseño de base de datos.
*   **[non_solid/](file:///non_solid/)**: Implementación rápida, monolítica e informal (V1). Sin separar responsabilidades, mezclando UI, base de datos y validaciones de negocio en un solo archivo.
*   **[solid/](file:///solid/)**: Arquitectura desacoplada en capas (V2). Aplica SRP, OCP, LSP, ISP y DIP, utilizando Inyección de Dependencias, clases base abstractas (interfaces) y modelos de dominio.

---

## Tecnologías Utilizadas

*   **Python 3.13+**
*   **SQLite** (Motor de base de datos integrado)
*   **Rich** (Librería de terminal para formato, paneles, tablas y menú interactivo)
*   **UV** (Gestor rápido de dependencias y entornos de Python)

---

## Cómo Ejecutar los Proyectos

Ambos proyectos se ejecutan de forma independiente utilizando `uv`.

### Requisitos Previos

Asegúrate de tener instalado `uv` en tu sistema:
```bash
# Instalación de uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### Ejecución de la Versión 1: NO SOLID

Esta versión corre todo en un script principal monolítico.

1. Navega a la carpeta del subproyecto:
   ```bash
   cd non_solid
   ```
2. Ejecuta la aplicación (uv instalará automáticamente `rich` y configurará el entorno virtual localmente):
   ```bash
   uv run main.py
   ```

---

### Ejecución de la Versión 2: SOLID

Esta versión cuenta con una arquitectura en capas modular (Domain Models -> Interfaces -> Repositories -> Services -> UI View & Controller -> Entry Point).

1. Navega a la carpeta del subproyecto:
   ```bash
   cd solid
   ```
2. Ejecuta la aplicación:
   ```bash
   uv run main.py
   ```

---

## Reglas de Negocio Implementadas

1.  **Horarios permitidos**: Bloques de horas exactas de **08:00 a 22:00**.
2.  **Duración de reservas**: Rango permitido de 1 a 4 horas por reserva.
3.  **Validación de disponibilidad**: No se permiten reservas que se traslapen en fecha y hora para la misma cancha.
4.  **Cálculo de tarifas**: Calculado automáticamente según el precio por hora de la cancha.
5.  **Cancelaciones**: Modificación de estado a `'Cancelada'`, liberando el horario.
