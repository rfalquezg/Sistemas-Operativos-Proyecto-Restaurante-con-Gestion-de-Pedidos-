# Representa el pedido de un cliente.
class Pedido:
    def __init__(self, numero, plato, cantidad=1, receta=None):
        self.numero = numero
        self.plato = plato
        self.cantidad = cantidad
        self.receta = receta or {}
        self.estado = "pendiente"
    def cambiar_estado(self, estado):
        self.estado = estado
