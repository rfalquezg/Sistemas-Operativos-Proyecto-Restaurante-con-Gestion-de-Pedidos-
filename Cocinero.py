import threading
# Cada cocinero es un hilo que atiende un pedido.
class Cocinero(threading.Thread):
    def __init__(self, nombre, inventario, gestor, con_mutex, barrera=None):
        super().__init__(name=nombre)
        self.nombre = nombre
        self.inventario = inventario
        self.gestor = gestor
        self.con_mutex = con_mutex
        self.barrera = barrera
        self.reserva_correcta = False

    def run(self):
        # run es el metodo que ejecuta Python al iniciar el hilo.
        pedido = self.gestor.tomar_pedido()
        if pedido is not None:
            self.atender_pedido(pedido)

    def atender_pedido(self, pedido):
        if pedido.plato == "lasana":
            # La lasana ya esta preparada y solo hay que reservarla.
            self.reserva_correcta = self.inventario.reservar_plato(
                "lasana", self.con_mutex, self.barrera
            )
        else:
            # Para este avance se reserva una porcion de pollo.
            self.reserva_correcta = self.inventario.reservar_ingrediente(
                "pollo", 1, self.con_mutex, self.barrera
            )

        if self.reserva_correcta:
            pedido.cambiar_estado("completado")
        else:
            pedido.cambiar_estado("sin disponibilidad")
