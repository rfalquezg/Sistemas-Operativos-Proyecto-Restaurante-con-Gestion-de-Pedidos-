
import threading

from Inventario import Inventario
from Pedido import Pedido
from Gestor_Pedidos import GestorPedidos
from Cocinero import Cocinero


def ejecutar_simulacion(
        tipo="basico",
        con_mutex=False,
        cocineros=2,
        stock=1
):
    # Validar la configuración.
    if tipo not in ("basico", "complejo"):
        raise ValueError(
            "Selecciona una representación válida."
        )

    if type(con_mutex) is not bool:
        raise ValueError("El valor del mutex no es válido.")

    if type(cocineros) is not int or not 2 <= cocineros <= 6:
        raise ValueError(
            "Se permiten entre 2 y 6 cocineros."
        )

    if type(stock) is not int or not 0 <= stock <= 10:
        raise ValueError(
            "El stock debe estar entre 0 y 10."
        )

    pasos = []

    # Este Lock protege únicamente el registro.
    mutex_registro = threading.Lock()

    def registrar(datos):
        with mutex_registro:
            pasos.append({
                "paso": len(pasos) + 1,
                **datos
            })

    # Crear el inventario compartido.
    inventario = Inventario(
        tipo,
        registrar=registrar,
        cocineros=cocineros
    )

    recurso = "pollo" if tipo == "basico" else "lasana"

    # Configurar stock inicial.
    if tipo == "basico":
        inventario.pollo = stock

    else:
        inventario.platos_preparados["lasana"] = stock

    # Crear los pedidos.
    pedidos = [
        Pedido(i, recurso)
        for i in range(1, cocineros + 1)
    ]

    gestor = GestorPedidos(pedidos)

    # En la versión sin mutex, permite que
    # varios hilos consulten el mismo stock
    # antes de realizar sus actualizaciones.
    barrera = None

    if not con_mutex:
        barrera = threading.Barrier(
            cocineros, timeout=8
        )

    # Crear los hilos de Python.
    hilos = [
        Cocinero(
            f"cocinero {i}",
            inventario,
            gestor,
            con_mutex,
            barrera
        )
        for i in range(1, cocineros + 1)
    ]

    # Iniciar todos los cocineros.
    for hilo in hilos:
        hilo.start()

    # Esperar a que terminen sus procesos.
    for hilo in hilos:
        hilo.join(timeout=10)

    if any(hilo.is_alive() for hilo in hilos):
        raise RuntimeError(
            "La simulación no terminó correctamente."
        )

    # Obtener el inventario final.
    if tipo == "basico":
        final = inventario.consultar("pollo")

    else:
        final = inventario.platos_preparados["lasana"]

    # Contar pedidos completados.
    reservas = sum(
        hilo.reserva_correcta for hilo in hilos
    )

    rechazados = cocineros - reservas

    # Detectar reservas duplicadas.
    conflictos = max(
        0,
        reservas - (stock - final)
    )

    conflicto = conflictos > 0

    if conflicto:
        mensaje = (
            "Condición de carrera: dos o más cocineros "
            "confirmaron una misma unidad."
        )

    else:
        mensaje = (
            "Sin reservas duplicadas: "
            "el inventario es consistente."
        )

    # Enviar resultados a la interfaz web.
    return {
        "tipo": tipo,
        "con_mutex": con_mutex,
        "recurso": recurso,
        "cocineros": cocineros,
        "stock_inicial": stock,
        "stock_final": final,
        "reservas": reservas,
        "rechazados": rechazados,
        "conflictos": conflictos,
        "conflicto": conflicto,
        "mensaje": mensaje,
        "movimientos": pasos,
        "pedidos": [
            {
                "numero": p.numero,
                "estado": p.estado
            }
            for p in pedidos
        ]
    }
