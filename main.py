import threading
from Inventario import Inventario
from Pedido import Pedido
from Gestor_Pedidos import GestorPedidos
from Cocinero import Cocinero

# Ejecuta una prueba con dos cocineros y un solo recurso disponible.
def probar_escenario(tipo, con_mutex, numero):
    print(f"\nescenario {numero}: {tipo} {'con' if con_mutex else 'sin'} sincronizacion")

    # Ambos cocineros comparten el MISMO inventario y el MISMO gestor.
    inventario = Inventario(tipo)
    plato = "pollo" if tipo == "basico" else "lasana"
    gestor = GestorPedidos([Pedido(1, plato), Pedido(2, plato)])

    # Solo sin mutex: los dos hilos consultan antes de actualizar.
    # La barrera demuestra el problema, pero no protege el inventario.
    barrera = None if con_mutex else threading.Barrier(2)

    cocineros = [
        Cocinero("cocinero 1", inventario, gestor, con_mutex, barrera),
        Cocinero("cocinero 2", inventario, gestor, con_mutex, barrera)
    ]

    for cocinero in cocineros:
        cocinero.start()
    for cocinero in cocineros:
        cocinero.join()

    reservas = sum(cocinero.reserva_correcta for cocinero in cocineros)
    if tipo == "basico":
        cantidad_final = inventario.consultar("pollo")
    else:
        cantidad_final = inventario.platos_preparados["lasana"]

    print("--- resultados ---")
    print(f"reservas confirmadas: {reservas}")
    print(f"cantidad final: {cantidad_final}")
    if reservas > 1:
        print("problema: se produjo una condicion de carrera.")
    else:
        print("correcto: no hubo reserva duplicada.")


if __name__ == "__main__":
    probar_escenario("basico", False, 1)
    probar_escenario("basico", True, 2)
    probar_escenario("complejo", False, 3)
    probar_escenario("complejo", True, 4)
