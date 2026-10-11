# Restaurante con Gestión de Pedidos

Proyecto grupal de la asignatura **Sistemas Operativos**, correspondiente a la actividad **P1_Grupal**.

## Integrantes — Grupo 6

- Roberto Alejandro Falquez Guerrero
- William Francisco Balseca Jimenez

## Situación seleccionada

Aplicación que representa el flujo de pedidos en una cocina, coordinando la preparación de platos según los recursos e ingredientes disponibles.

En un restaurante pueden recibirse varios pedidos al mismo tiempo. Cada plato requiere ingredientes, utensilios y equipos de cocina que pueden ser compartidos con otras preparaciones. Por ello, es necesario organizar las tareas y coordinar el uso de estos recursos para evitar conflictos y retrasos.

## Objetivo del proyecto

Representar el flujo de atención de pedidos de un restaurante, desde su recepción hasta la finalización de los platos, coordinando su preparación según la disponibilidad de recursos e ingredientes.

## Funcionamiento propuesto

1. Recibir y registrar los pedidos de los clientes.
2. Identificar los platos solicitados.
3. Verificar los ingredientes y recursos necesarios.
4. Coordinar la preparación de los platos y el uso de recursos compartidos.
5. Actualizar el estado de cada pedido hasta completar su preparación.

## Relación con Sistemas Operativos

El proyecto permitirá aplicar los siguientes conceptos:

- **Concurrencia:** representar la preparación de varios pedidos al mismo tiempo.
- **Sincronización:** coordinar las tareas que necesitan utilizar un mismo recurso.
- **Gestión de recursos compartidos:** organizar el uso de utensilios y equipos disponibles en la cocina.

## Fase de análisis

Se compararon los modelos de **Memoria Compartida** y **Paso de Mensajes** para coordinar a los cocineros y gestionar el inventario de ingredientes.

Se seleccionó **Memoria Compartida** para una aplicación que funciona en un solo equipo, con hilos que representan a los cocineros. La extracción de pedidos y la verificación y reserva de ingredientes se protegerán mediante bloqueos, que se liberarán antes de preparar los platos.

## Documentación

[Consultar la fase de análisis en PDF](docs/Restaurante%20con%20Gesti%C3%B3n%20de%20Pedidos.pdf)

El documento incluye la descripción de la situación, las unidades de ejecución, el recurso compartido principal, los datos y resultados esperados, la tabla comparativa, la conclusión del modelo seleccionado y la bibliografía.

## Estructura actual del repositorio

```text
restaurante/
├── README.md                              # Descripción, integrantes y estado del proyecto
└── docs/                                  # Documentación del proyecto
    └── Restaurante con Gestión de Pedidos.pdf  # Fase de análisis y comparación de modelos
```

Esta estructura se actualizará conforme se incorporen el código, las pruebas y los resultados del proyecto.

## Estado del proyecto

La fase de análisis está documentada y el modelo de comunicación seleccionado es Memoria Compartida. La implementación se desarrollará en las siguientes etapas.
