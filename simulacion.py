import threading
from Inventario import Inventario
from Pedido import Pedido
from Gestor_Pedidos import GestorPedidos
from Cocinero import Cocinero


def ejecutar_simulacion(tipo="basico", con_mutex=False, cocineros=2, stock=1):
    """Crea una prueba independiente y devuelve los resultados para la web."""
    if tipo not in ("basico", "complejo"):
        raise ValueError("La representacion debe ser basico o complejo.")
    if type(con_mutex) is not bool:
        raise ValueError("El mutex debe ser verdadero o falso.")
    if type(cocineros) is not int or not 2 <= cocineros <= 6:
        raise ValueError("El numero de cocineros debe estar entre 2 y 6.")
    if type(stock) is not int or not 0 <= stock <= 10:
        raise ValueError("La cantidad inicial debe estar entre 0 y 10.")

    movimientos = []
    mutex_registro = threading.Lock()

    def registrar(datos):
        # Este bloqueo es solo para ordenar el registro, no protege el inventario.
        with mutex_registro:
            movimientos.append({"paso": len(movimientos) + 1, **datos})

    inventario = Inventario(tipo, registrar=registrar)
    recurso = "pollo" if tipo == "basico" else "lasana"
    if tipo == "basico":
        inventario.pollo = stock
    else:
        inventario.platos_preparados["lasana"] = stock

    pedidos = [Pedido(i, recurso) for i in range(1, cocineros + 1)]
    gestor = GestorPedidos(pedidos)
    # En la version sin mutex todos consultan el mismo dato antes de descontar.
    barrera = None if con_mutex else threading.Barrier(cocineros, timeout=5)
    hilos = [
        Cocinero(f"cocinero {i}", inventario, gestor, con_mutex, barrera)
        for i in range(1, cocineros + 1)
    ]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join(timeout=7)

    if any(hilo.is_alive() for hilo in hilos):
        raise RuntimeError("No se pudo terminar la simulacion.")

    final = inventario.consultar("pollo") if tipo == "basico" else inventario.platos_preparados["lasana"]
    confirmadas = sum(hilo.reserva_correcta for hilo in hilos)
    # Si hay mas reservas que unidades descontadas, hay perdida de actualizaciones.
    conflicto = confirmadas != stock - final
    return {
        "tipo": tipo,
        "con_mutex": con_mutex,
        "recurso": recurso,
        "cocineros": cocineros,
        "stock_inicial": stock,
        "stock_final": final,
        "reservas": confirmadas,
        "conflicto": conflicto,
        "mensaje": ("Se detecto una condicion de carrera: hay reservas que no quedaron registradas."
                    if conflicto else "Las cantidades y las reservas son consistentes."),
        "movimientos": movimientos,
        "pedidos": [{"numero": pedido.numero, "estado": pedido.estado} for pedido in pedidos],
    }
