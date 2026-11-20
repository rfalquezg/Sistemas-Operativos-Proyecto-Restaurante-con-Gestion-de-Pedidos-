
# Restaurante con Gestión de Pedidos

Proyecto grupal de la asignatura **Sistemas Operativos**, correspondiente a la actividad **P1_Grupal**.

## Integrantes — Grupo 6

- Roberto Alejandro Falquez Guerrero
- William Francisco Balseca Jimenez

## Situación seleccionada

Aplicación que representa el flujo de pedidos en una cocina, coordinando la preparación de platos según los recursos e ingredientes disponibles.

En un restaurante pueden recibirse varios pedidos al mismo tiempo. Cada plato requiere ingredientes y recursos que pueden ser compartidos con otras preparaciones. Además, el restaurante puede tener platos preparados en masa que están listos para entregar. Por ello, es necesario organizar las tareas para evitar que dos cocineros utilicen los mismos ingredientes o retiren el mismo plato.

## Objetivo del proyecto

Representar el flujo de atención de pedidos de un restaurante, desde su recepción hasta la finalización de los platos, coordinando su preparación y entrega según la disponibilidad de ingredientes y platos preparados.

## Funcionamiento propuesto

1. Recibir y registrar los pedidos de los clientes.
2. Identificar los platos solicitados.
3. Verificar los ingredientes o platos preparados disponibles.
4. Asignar cada pedido a un cocinero.
5. Reservar los ingredientes o platos necesarios sin generar conflictos.
6. Actualizar el estado de cada pedido hasta completar su preparación o entrega.

## Relación con Sistemas Operativos

El proyecto permitirá aplicar los siguientes conceptos:

- **Concurrencia:** representar a varios cocineros mediante hilos que atienden pedidos al mismo tiempo.
- **Memoria compartida:** permitir que todos los cocineros accedan al mismo inventario y a la lista de pedidos.
- **Sincronización:** coordinar el acceso a los recursos mediante bloqueos.
- **Sección crítica:** controlar las operaciones de consulta, verificación y descuento de ingredientes o platos preparados.

## Fase de análisis

Se compararon los modelos de **Memoria Compartida** y **Paso de Mensajes** para coordinar a los cocineros y gestionar los recursos del restaurante.

Se seleccionó **Memoria Compartida**, porque los cocineros serán representados mediante hilos que trabajan dentro de una misma aplicación en Python.

## Fase de planificación y diseño

Durante esta fase se identificaron los recursos compartidos y se diseñaron las clases que participarán en la futura implementación.

Se propusieron dos representaciones para el inventario:

### Tipo básico (int)

Utilizaremos variables enteras que representan las cantidades disponibles de cada ingrediente.

**Ejemplo:**

```python
pollo = 5

carne = 8

arroz = 10

papas = 12
```

Esta representación es fácil de comprender, pero requiere utilizar diferentes variables para administrar cada ingrediente.

### Tipo complejo (dict)

Utilizaremos un diccionario que almacena varios ingredientes con sus respectivas cantidades dentro de una misma estructura.

**Ejemplo:**

```python
inventario = {
    "pollo": 5,
    "arroz": 10,
    "carne": 8,
    "papas": 12
}
```

Se decidió utilizar el **diccionario (dict)** porque permite organizar mejor la información del inventario y facilitará las consultas y modificaciones de los recursos compartidos.

Los ejemplos anteriores representan el diseño inicial; en el Avance 1 se implementaron las dos representaciones del inventario para realizar pruebas de sincronización.

### Clases propuestas

Para el desarrollo del proyecto se diseñaron cuatro clases principales:

- **Inventario:** administrará las cantidades de ingredientes disponibles y las reservas.
- **Pedido:** almacenará la información de cada pedido y su estado.
- **GestorPedidos:** administrará los pedidos pendientes y evitará que dos cocineros seleccionen el mismo.
- **Cocinero:** representará a cada hilo que atenderá los pedidos utilizando los recursos compartidos.

También se consideró el control de los platos preparados en masa, para evitar que dos cocineros retiren la misma porción.

### Sección crítica y sincronización

La sección crítica se presenta cuando varios cocineros intentan consultar, verificar y modificar las cantidades de un recurso compartido al mismo tiempo.

Por ejemplo, si solamente queda una porción de lasaña preparada y dos cocineros intentan retirarla, ambos podrían pensar que todavía está disponible.

Para evitar este conflicto, se propone utilizar un **mutex mediante `threading.Lock`**, permitiendo que solamente un hilo realice la verificación y actualización del recurso compartido a la vez.

El bloqueo se adquirirá antes de verificar la disponibilidad y se liberará después de actualizar la cantidad correspondiente.

## Documentación

[Consultar documentación del proyecto en PDF](docs/Restaurante%20con%20Gesti%C3%B3n%20de%20Pedidos.pdf)

El documento contiene las fases de análisis, planificación y diseño, la comparación de modelos de cooperación, las clases propuestas y los mecanismos de sincronización.

## Presentación del proyecto

[Ver presentación de planificación y diseño](docs/Presentacion_Gestion%20de%20pedidos%20en%20Restaurantes.pptx)

La presentación explica los cocineros como hilos, los recursos compartidos, los tipos de datos básicos y complejos, las clases propuestas, la sección crítica y el uso de mutex para evitar conflictos.

## Estructura actual del repositorio

```text
restaurante/
├── .gitignore
├── README.md
├── main.py
├── Inventario.py
├── Pedido.py
├── Gestor_Pedidos.py
├── Cocinero.py
├── simulacion.py
├── app_web.py
├── web/
│   ├── index.html
│   ├── estilos.css
│   └── interfaz.js
├── tests/
│   └── test_simulacion.py
└── docs/
    ├── Restaurante con Gestión de Pedidos.pdf
    ├── Presentacion_Gestion de pedidos en Restaurantes.pptx
    ├── avance_implementacion.md
    ├── interfaz_web.md
    └── evidencia_ejecucion.txt
```

En IntelliJ/PyCharm, el archivo principal del ZIP se llama `Gestion De Pedidos.py`. En GitHub, ese mismo archivo se llama `main.py` para facilitar su ejecución. Las clases están separadas en `Inventario.py`, `Pedido.py`, `Gestor_Pedidos.py` y `Cocinero.py`, tal como en el ZIP del proyecto. Las carpetas locales `.venv/` y `.idea/` no se suben porque contienen configuraciones del entorno de desarrollo.

Esta estructura se actualizará conforme se incorporen más funcionalidades, pruebas y resultados del proyecto.

## Estado del proyecto

Actualmente se encuentran documentadas las fases de **análisis, planificación y diseño**.

El modelo seleccionado es **Memoria Compartida** y se utilizarán hilos para representar a los cocineros, junto con mecanismos de sincronización para proteger los recursos compartidos.

Se implementó un primer avance con las clases Inventario, Pedido, GestorPedidos y Cocinero para demostrar la condición de carrera y su solución con un mutex. La implementación completa continúa en desarrollo.

## Primer avance de implementación

### Situación

En el restaurante, los **cocineros son los hilos**. En esta primera prueba, dos cocineros intentan reservar la última unidad disponible. Se prueba un ingrediente (pollo) y un plato preparado en masa (lasaña).

### Dos representaciones y clases

En la versión final del **Avance 1** se mantiene la clase **`Inventario`** con dos formas de guardar los datos, como se planteó en el documento y la presentación:

- **Tipo básico (`int`):** variables enteras separadas, como `pollo = 1`, `carne = 8`, `arroz = 10` y `papas = 12`.
- **Tipo complejo (`dict`):** un diccionario de ingredientes con pollo, arroz, carne y papas, además de `platos_preparados = {"lasana": 1}`.

También se usan las clases **`Pedido`**, **`GestorPedidos`** y **`Cocinero`**. En cada prueba, los dos hilos de cocineros reciben el **mismo objeto `Inventario`** y el mismo gestor de pedidos.

### Sección crítica

La sección crítica está señalada con comentarios en los métodos **`descontar_ingrediente()`** y **`descontar_plato()`** de `Inventario.py`. Contiene las operaciones de **consultar**, **validar** la disponibilidad y **actualizar** el recurso.

Sin sincronización, los dos cocineros pueden leer que hay una unidad disponible y ambos confirmar la reserva antes de que se actualice correctamente el inventario. En la prueba, el stock termina en cero, pero aparecen dos pedidos atendidos: esa es la inconsistencia.

### Mecanismo elegido

Se utiliza **`threading.Lock()` (mutex)** porque la consulta, validación y actualización deben realizarse de forma exclusiva. El bloqueo se adquiere antes de estas operaciones y se libera al terminar el bloque `with self.mutex:`. La lista de pedidos pendientes también se protege con un bloqueo.

Para mostrar el conflicto de forma reproducible, **solo en la prueba sin mutex del inventario** se utiliza `threading.Barrier(2)`, que permite que los dos hilos lean antes de descontar. Esta barrera sirve para demostrar el error y no protege el inventario.

### Tabla de resultados

| Recurso | Prueba | Stock inicial | Reservas confirmadas | Stock final | Resultado |
|---|---|---:|---:|---:|---|
| Entero (pollo) | Sin Lock | 1 | 2 | 0 | Reserva duplicada |
| Entero (pollo) | Con Lock | 1 | 1 | 0 | Correcto |
| Diccionario (lasaña lista) | Sin Lock | 1 | 2 | 0 | Reserva duplicada |
| Diccionario (lasaña lista) | Con Lock | 1 | 1 | 0 | Correcto |

### Evidencia y ejecución

El proyecto organizado por archivos se ejecutó correctamente y terminó con **exit code 0**. La salida proporcionada por el equipo en IntelliJ/PyCharm corresponde a `Gestion De Pedidos.py`. Desde una terminal también se puede ejecutar así:

```bash
python main.py
```

La salida compartida por el equipo confirma **2 reservas sin mutex** y **1 reserva con mutex** tanto para el pollo como para la lasaña preparada, con stock final de 0 en todas las pruebas. La consola terminó con `Process finished with exit code 0`. El código organizado en archivos se verificó adicionalmente con los mismos resultados. Como son hilos, el orden de los mensajes puede variar.

- [Archivo principal de las pruebas](main.py)
- [Clase Inventario](Inventario.py)
- [Clase Pedido](Pedido.py)
- [Clase GestorPedidos](Gestor_Pedidos.py)
- [Clase Cocinero](Cocinero.py)
- [Documentación de la sección crítica y resultados](docs/avance_implementacion.md)
- [Salida de ejecución compartida por el equipo](docs/evidencia_ejecucion.txt)

Este es un **primer avance académico**, no la versión final. Aún falta integrar recetas completas, más platos y el manejo general de los pedidos.

## Avance 2: Interfaz web interactiva

Se incluyo una pagina web local para elegir las dos representaciones del recurso (entero y diccionario) y comparar su comportamiento **con y sin mutex**. Es posible configurar de **2 a 6 cocineros** y de **0 a 10 unidades** disponibles.

La pagina muestra cada hilo, la operacion de reserva, el recurso **antes**, el **resultado**, el recurso **despues**, el stock final, las reservas confirmadas y si hubo una condicion de carrera. Tambien permite comparar las cuatro versiones con un solo boton.

### Como ejecutar la interfaz

No se requieren librerias adicionales; solo Python 3.

```bash
python app_web.py
```

Despues abre **http://localhost:8000** en tu navegador. Para cerrar el servidor presiona Ctrl+C. Se conserva la version por consola con `python main.py`.

### Archivos de este avance

- [Interfaz web (servidor)](app_web.py)
- [Simulacion concurrente](simulacion.py)
- [Pagina principal](web/index.html)
- [Estilos](web/estilos.css)
- [Interaccion de la pagina](web/interfaz.js)
- [Documentacion de la interfaz](docs/interfaz_web.md)
- [Pruebas](tests/test_simulacion.py)

Para probar desde terminal: `python -m unittest discover -s tests`.

**Estado:** Avance 1 terminado y Avance 2 con interfaz web local implementada. El restaurante completo sigue en desarrollo.
