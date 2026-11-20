import threading
# Lleva la lista de pedidos pendientes del restaurante.
class GestorPedidos:
    def __init__(self, pedidos):
        self.pedidos = pedidos
        self.mutex = threading.Lock()

    def agregar_pedido(self, pedido):
        with self.mutex:
            self.pedidos.append(pedido)

    def tomar_pedido(self):
        # El mutex evita que dos cocineros tomen el mismo pedido.
        with self.mutex:
            if self.pedidos:
                return self.pedidos.pop(0)
        return None
