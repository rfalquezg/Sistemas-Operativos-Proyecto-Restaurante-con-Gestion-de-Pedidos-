# Avance 2 — Interfaz web interactiva

## Objetivo

Agregamos una interfaz web local para configurar y comparar las cuatro versiones de la simulacion de concurrencia del restaurante.

## Como se ejecuta

Se utiliza Python 3 y no hace falta instalar librerias externas.

1. Abrir la carpeta completa del proyecto en IntelliJ o PyCharm.
2. Ejecutar `app_web.py`, o escribir en la terminal `python app_web.py`.
3. Abrir `http://localhost:8000` en el navegador.
4. Elegir representacion (basico o complejo), mutex (con o sin), cocineros (2 a 6) y stock inicial (0 a 10).
5. Presionar **Ejecutar escenario** o **Comparar las 4 versiones**.
6. Para detener la aplicacion, presionar Ctrl+C en la consola.

## Que muestra la interfaz

- Nombre de cada hilo (cocinero 1, cocinero 2, etc.).
- Operacion que realizo (reservar una unidad de pollo o lasana).
- Cantidad que consulto antes, si pudo reservar y cantidad que escribio despues.
- Stock inicial y final del recurso compartido.
- Reservas confirmadas y mensaje de consistencia o condicion de carrera.
- Comparacion de las cuatro versiones de la simulacion.

## Como funciona

Mantenemos las clases `Inventario`, `Pedido`, `GestorPedidos` y `Cocinero`. El archivo `simulacion.py` prepara pedidos y cocineros con una unica instancia compartida de inventario. `Inventario.py` incluye un registro opcional de operaciones para que la pagina muestre lo que sucede en cada hilo.

La seccion critica sigue siendo **consultar, validar y actualizar**. Cuando se selecciona **con mutex**, `threading.Lock()` protege toda esa secuencia. Cuando se elige **sin mutex**, una barrera de prueba hace que los hilos consulten el mismo valor antes de actualizarlo, mostrando posibles reservas duplicadas o actualizaciones perdidas. La barrera NO es el mecanismo de proteccion.

El servidor `app_web.py` funciona en el propio equipo (127.0.0.1) y responde a los botones de la pagina. Cada simulacion comienza con un inventario nuevo: no conserva ni modifica los recursos de otras pruebas.

## Resultados de referencia (dos cocineros y una unidad)

| Version | Stock inicial | Reservas | Stock final | Resultado |
|---|---:|---:|---:|---|
| Basico sin mutex | 1 | 2 | 0 | Condicion de carrera |
| Basico con mutex | 1 | 1 | 0 | Correcto |
| Complejo sin mutex | 1 | 2 | 0 | Condicion de carrera |
| Complejo con mutex | 1 | 1 | 0 | Correcto |

## Archivos de la interfaz

- `app_web.py`: servidor web de Python.
- `simulacion.py`: prepara y ejecuta las pruebas concurrentes y devuelve los resultados.
- `web/index.html`: formulario y tabla de resultados.
- `web/estilos.css`: diseño visual de la pagina.
- `web/interfaz.js`: envia los parametros y muestra resultados.
- `tests/test_simulacion.py`: pruebas automaticas de los cuatro escenarios.

La interfaz corre localmente y no necesita internet.
