
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

Los ejemplos anteriores representan el diseño propuesto y todavía no constituyen la implementación completa del programa.

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
├── README.md
└── docs/
    ├── Restaurante con Gestión de Pedidos.pdf
    └── Presentacion_Gestion de pedidos en Restaurantes.pptx
```

Esta estructura se actualizará conforme se incorporen el código, las pruebas y los resultados del proyecto.

## Estado del proyecto

Actualmente se encuentran documentadas las fases de **análisis, planificación y diseño**.

El modelo seleccionado es **Memoria Compartida** y se utilizarán hilos para representar a los cocineros, junto con mecanismos de sincronización para proteger los recursos compartidos.

La implementación de las clases, los hilos y las pruebas del programa se desarrollará en las siguientes etapas.
