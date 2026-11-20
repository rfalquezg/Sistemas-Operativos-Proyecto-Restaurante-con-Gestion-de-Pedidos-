import threading
# Guarda los ingredientes y los platos preparados del restaurante.
class Inventario:
    def __init__(self, tipo):
        self.tipo = tipo
        self.mutex = threading.Lock()

        if tipo == "basico":
            # Cada ingrediente se guarda en una variable entera.
            self.pollo = 1
            self.carne = 8
            self.arroz = 10
            self.papas = 12
        else:
            # Los ingredientes se guardan en un diccionario.
            self.ingredientes = {
                "pollo": 5,
                "arroz": 10,
                "carne": 8,
                "papas": 12
            }
            # Platos que ya se prepararon en masa.
            self.platos_preparados = {"lasana": 1}

    def consultar(self, ingrediente):
        if self.tipo == "basico":
            return getattr(self, ingrediente, 0)
        return self.ingredientes.get(ingrediente, 0)

    def reservar_ingrediente(self, ingrediente, cantidad, con_mutex, barrera=None):
        if con_mutex:
            # El mutex se adquiere antes de la seccion critica.
            with self.mutex:
                return self.descontar_ingrediente(ingrediente, cantidad)
            # Al salir del with se libera el mutex.

        return self.descontar_ingrediente(ingrediente, cantidad, barrera)

    def descontar_ingrediente(self, ingrediente, cantidad, barrera=None):
        # SECCION CRITICA: consultar, validar y actualizar.
        disponible = self.consultar(ingrediente)  # 1. Consultar
        alcanza = disponible >= cantidad         # 2. Validar

        if barrera is not None:
            # Solo para demostrar la condicion de carrera sin mutex.
            barrera.wait()

        if alcanza:
            if self.tipo == "basico":
                setattr(self, ingrediente, disponible - cantidad)
            else:
                self.ingredientes[ingrediente] = disponible - cantidad
            return True                          # 3. Actualizar
        return False

    def reservar_plato(self, plato, con_mutex, barrera=None):
        if con_mutex:
            with self.mutex:
                return self.descontar_plato(plato)
        return self.descontar_plato(plato, barrera)

    def descontar_plato(self, plato, barrera=None):
        # SECCION CRITICA: consultar, validar y actualizar platos listos.
        disponible = self.platos_preparados.get(plato, 0)  # 1. Consultar
        alcanza = disponible >= 1                        # 2. Validar

        if barrera is not None:
            barrera.wait()  # Solo para mostrar el problema sin mutex.

        if alcanza:
            self.platos_preparados[plato] = disponible - 1  # 3. Actualizar
            return True
        return False
