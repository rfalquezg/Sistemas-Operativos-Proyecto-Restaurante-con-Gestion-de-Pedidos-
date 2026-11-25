import threading
# Cada cocinero representa un hilo que atiende pedidos.
class Cocinero(threading.Thread):
    def __init__(self, nombre, inventario, gestor, con_mutex, barrera=None):

        # Asignar el nombre al hilo.
        super().__init__(name=nombre)

        self.nombre = nombre
        self.inventario = inventario
        self.gestor = gestor
        self.con_mutex = con_mutex
        self.barrera = barrera
        self.reserva_correcta = False

    # Metodo que se ejecuta cuando inicia el hilo.
    def run(self):

        # El cocinero toma un pedido pendiente.
        pedido = self.gestor.tomar_pedido()

        if pedido is not None:
            self.atender_pedido(pedido)

    # Metodo para atender el pedido.
    def atender_pedido(self, pedido):

        if pedido.plato == "lasana":

            # Tipo complejo: reservar una lasana preparada.
            self.reserva_correcta = self.inventario.reservar_plato(
                "lasana",
                self.con_mutex,
                self.barrera
            )

        else:

            # Tipo basico: reservar una porcion de pollo.
            self.reserva_correcta = self.inventario.reservar_ingrediente(
                "pollo",
                1,
                self.con_mutex,
                self.barrera
            )

        # Actualizar el estado del pedido.
        if self.reserva_correcta:
            pedido.cambiar_estado("completado")

        else:
            pedido.cambiar_estado("sin disponibilidad")
