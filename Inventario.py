import threading

# Clase del avance 1: ahora tambien puede avisar a la interfaz de lo que paso.
class Inventario:
    def __init__(self, tipo, registrar=None):
        self.tipo = tipo
        self.mutex = threading.Lock()
        self.registrar = registrar

        if tipo == "basico":
            self.pollo = 1
            self.carne = 8
            self.arroz = 10
            self.papas = 12
        else:
            self.ingredientes = {
                "pollo": 5,
                "arroz": 10,
                "carne": 8,
                "papas": 12
            }
            self.platos_preparados = {"lasana": 1}

    def consultar(self, ingrediente):
        if self.tipo == "basico":
            return getattr(self, ingrediente, 0)
        return self.ingredientes.get(ingrediente, 0)

    def reservar_ingrediente(self, ingrediente, cantidad, con_mutex, barrera=None):
        if con_mutex:
            # El mutex se toma antes de consultar y se libera despues de actualizar.
            with self.mutex:
                return self.descontar_ingrediente(ingrediente, cantidad)
        return self.descontar_ingrediente(ingrediente, cantidad, barrera)

    def descontar_ingrediente(self, ingrediente, cantidad, barrera=None):
        # SECCION CRITICA: 1. consultar, 2. validar, 3. actualizar.
        antes = self.consultar(ingrediente)
        alcanza = antes >= cantidad
        if barrera is not None:
            barrera.wait()  # Solo se usa para demostrar el error sin mutex.
        if alcanza:
            despues = antes - cantidad
            if self.tipo == "basico":
                setattr(self, ingrediente, despues)
            else:
                self.ingredientes[ingrediente] = despues
        else:
            despues = antes
        self.guardar_operacion(ingrediente, antes, alcanza, despues)
        return alcanza

    def reservar_plato(self, plato, con_mutex, barrera=None):
        if con_mutex:
            with self.mutex:
                return self.descontar_plato(plato)
        return self.descontar_plato(plato, barrera)

    def descontar_plato(self, plato, barrera=None):
        # SECCION CRITICA: 1. consultar, 2. validar, 3. actualizar.
        antes = self.platos_preparados.get(plato, 0)
        alcanza = antes >= 1
        if barrera is not None:
            barrera.wait()  # Ambos hilos consultan antes de modificar.
        despues = antes - 1 if alcanza else antes
        if alcanza:
            self.platos_preparados[plato] = despues
        self.guardar_operacion(plato, antes, alcanza, despues)
        return alcanza

    def guardar_operacion(self, recurso, antes, resultado, despues):
        if self.registrar is not None:
            self.registrar({
                "hilo": threading.current_thread().name,
                "operacion": f"reservar 1 de {recurso}",
                "antes": antes,
                "resultado": "reservado" if resultado else "sin disponibilidad",
                "despues": despues,
                "confirmada": resultado
            })
