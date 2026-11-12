# Primer avance de implementación

## Situación

En el restaurante, los cocineros son los hilos. En esta primera prueba dos cocineros intentan reservar la última unidad disponible. Se prueba un ingrediente (pollo) y un plato preparado en masa (lasaña).

## Dos representaciones

- **Tipo básico:** la clase `InventarioBasico` usa el entero `pollo = 1`.
- **Tipo complejo:** la clase `InventarioComplejo` usa un diccionario con pollo, arroz, carne, papas y `lasana_lista = 1`.

En cada prueba, los dos hilos reciben el mismo objeto inventario.

## Sección crítica

La sección crítica está señalada con comentarios en los métodos `_revisar_y_descontar`. Sus tres operaciones son **consultar**, **validar** si hay disponibilidad y **actualizar** la cantidad.

Sin protección, dos cocineros pueden leer que hay una unidad y ambos confirmar una reserva. Aunque el inventario termina en cero, se confirmaron dos reservas: existe una inconsistencia.

## Mecanismo elegido

Se usa **`threading.Lock` (mutex)** porque esta secuencia debe ser exclusiva. El bloqueo se adquiere antes de consultar, validar y descontar, y se libera al salir del bloque `with`, incluso cuando se retorna del método. No se mantiene durante la preparación del plato.

Para mostrar de forma reproducible el problema, **solo en la versión sin sincronización** se utiliza `threading.Barrier(2)`, que obliga a ambos hilos a completar la lectura antes de escribir. Esta barrera es una herramienta de demostración: no protege el inventario.

## Tabla de resultados de la prueba

| Recurso | Prueba | Stock inicial | Reservas confirmadas | Stock final | Resultado |
|---|---|---:|---:|---:|---|
| Entero (pollo) | Sin Lock | 1 | 2 | 0 | Reserva duplicada |
| Entero (pollo) | Con Lock | 1 | 1 | 0 | Correcto |
| Diccionario (lasaña lista) | Sin Lock | 1 | 2 | 0 | Reserva duplicada |
| Diccionario (lasaña lista) | Con Lock | 1 | 1 | 0 | Correcto |

## Evidencia y ejecución

Se ejecutó desde consola con:

```bash
python main.py
```

La salida de referencia de las cuatro pruebas se conserva en [evidencia_ejecucion.txt](evidencia_ejecucion.txt). El orden de impresión de los cocineros puede variar porque son hilos.

Este es un **primer avance académico**, no el sistema terminado. Todavía falta integrar pedidos reales, recetas y el inventario completo de platos preparados.
