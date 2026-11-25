# Proyecto_gestion_restaurantes

Proyecto de **Sistemas Operativos · Grupo 6**: restaurante con gestión concurrente de pedidos y visualización web de secciones críticas.

## Funcionalidades

- Representación básica: `pollo` como variable entera (`int`).
- Representación compleja: ingredientes y lasañas preparadas mediante diccionarios (`dict`).
- Escenarios con y sin sincronización (`threading.Lock`).
- En el escenario con mutex, los cocineros permanecen en espera hasta que el hilo anterior libera la sección crítica. La espera se representa en la interfaz.
- En el escenario sin mutex, los hilos pueden confirmar reservas duplicadas por condición de carrera.
- Interfaz rojo/granate con cuatro estaciones (pedidos, cocineros, inventario y despacho), reproducción paso a paso, bitácora, exportación CSV y comparación.

## Ejecutar

Requiere **Python 3.10 o superior**. No se necesitan dependencias externas.

```bash
python app_web.py
```

Abrir `http://127.0.0.1:8000` en el navegador.

## Pruebas

```bash
python -m unittest discover -s tests -p 'tests*.py' -v
```

## Archivos principales

- `Inventario.py`: acceso al inventario y sincronización.
- `Cocinero.py`: hilo que atiende un pedido.
- `Pedido.py`: entidad pedido.
- `Gestor_Pedidos.py`: administración de la cola de pedidos.
- `simulacion.py`: ejecución y registro de movimientos de los hilos.
- `app_web.py`: servidor HTTP y API `POST /api/simular`.
- `web/index.html`, `web/estilos.css`, `web/interfaz.js`: aplicación web.
- `tests/tests_simulacion.py`: pruebas de casos concurrentes.

## Ejemplo: dos cocineros, una unidad

| Modo | Reservas | Rechazados | Conflictos |
|---|---:|---:|---:|
| Sin mutex | 2 | 0 | 1 |
| Con mutex | 1 | 1 | 0 |

Con mutex, el segundo cocinero espera, entra cuando se libera el acceso y finalmente puede rechazar el pedido si ya no existe stock. No se repone el inventario de manera automática.

> La interfaz reproduce registros obtenidos de hilos Python; el control de pausa detiene la reproducción visual, no la ejecución real de hilos ya finalizada.

## Integrantes

- Roberto Alejandro Falquez Guerrero
- William Francisco Balseca Jimenez
