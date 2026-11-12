# Primer avance de implementación

## Situación

En el restaurante, los cocineros son los hilos. Dos cocineros intentan reservar la última unidad disponible: una porción de pollo o una lasaña ya preparada en masa.

## Clases y representaciones

Se mantienen las cuatro clases propuestas en el documento y la presentación:

- **Inventario:** según el atributo `tipo`, emplea las variables enteras `pollo`, `carne`, `arroz`, `papas` (tipo básico) o el diccionario `ingredientes` (tipo complejo). En el tipo complejo también maneja `platos_preparados = {"lasana": 1}`.
- **Pedido:** almacena identificador, plato, cantidad, receta y estado.
- **GestorPedidos:** almacena y asigna pedidos pendientes.
- **Cocinero:** hereda de `threading.Thread` y ejecuta el método `run()` para atender un pedido.

En cada escenario, los dos cocineros reciben **la misma instancia** de `Inventario` y `GestorPedidos`.

## Sección crítica

La sección crítica está identificada mediante comentarios en `_descontar_ingrediente()` y `_descontar_plato()`:

1. **Consultar** la cantidad disponible.
2. **Validar** que alcanza para la reserva.
3. **Actualizar** el recurso descontando la cantidad.

Sin protección, ambos cocineros pueden observar una unidad disponible y confirmar dos reservas de esa misma unidad. En la prueba queda un inventario final de 0, pero **dos pedidos figuran atendidos**: eso es la inconsistencia. `GestorPedidos.obtener_pedido()` también protege mediante un bloqueo la asignación de cada pedido.

## Mecanismo elegido

Se utiliza **mutex mediante `threading.Lock()`**. Se adquiere antes de consultar, validar y modificar el inventario, y se libera al salir de `with self.lock:`; no permanece adquirido durante la preparación del plato. También se protege la lista de pedidos.

Para reproducir el problema, **solo en las pruebas sin mutex sobre el inventario**, `threading.Barrier(2)` permite que los dos hilos lean antes de actualizar. La barrera es una ayuda para demostrar el error, no un reemplazo del mutex.

## Tabla de resultados de la ejecución

| Recurso | Prueba | Stock inicial | Reservas confirmadas | Stock final | Resultado |
|---|---|---:|---:|---:|---|
| Entero (pollo) | Sin Lock | 1 | 2 | 0 | Reserva duplicada |
| Entero (pollo) | Con Lock | 1 | 1 | 0 | Correcto |
| Diccionario (lasaña preparada) | Sin Lock | 1 | 2 | 0 | Reserva duplicada |
| Diccionario (lasaña preparada) | Con Lock | 1 | 1 | 0 | Correcto |

## Evidencia y ejecución

El equipo ejecutó el primer avance en PyCharm con `main.py`. También puede ejecutarse desde consola con `python main.py`.

Se conserva la salida proporcionada por el equipo en [evidencia_ejecucion.txt](evidencia_ejecucion.txt). El orden de los mensajes y algunas líneas de impresión pueden variar por concurrencia.

Este es un **primer avance académico**, no la aplicación terminada. Falta integrar recetas completas, cantidades variables, más platos preparados y la atención real de pedidos.
