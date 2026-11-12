"""Primer avance del proyecto: concurrencia en el inventario del restaurante."""

import threading


class InventarioBasico:
    # Representa un ingrediente con una variable entera.
    def __init__(self):
        self.pollo = 1
        self.lock = threading.Lock()

    def reservar(self, cocinero, sincronizado=False, barrera=None):
        if sincronizado:
            # El bloqueo se adquiere aqui y se libera al salir del with.
            with self.lock:
                return self._revisar_y_descontar(cocinero)
        return self._revisar_y_descontar(cocinero, barrera)

    def _revisar_y_descontar(self, cocinero, barrera=None):
        # SECCION CRITICA: consulta, validacion y actualizacion.
        cantidad = self.pollo              # Consultar
        disponible = cantidad > 0          # Validar
        if barrera is not None:
            barrera.wait()  # Para que ambos hilos lean antes de cambiar el dato
        if disponible:
            self.pollo = cantidad - 1      # Actualizar
            print(f"{cocinero}: reservo una porcion de pollo")
            return True
        print(f"{cocinero}: no hay pollo")
        return False


class InventarioComplejo:
    # Representa varios ingredientes y platos en un diccionario.
    def __init__(self):
        self.inventario = {
            "pollo": 5,
            "arroz": 10,
            "carne": 8,
            "papas": 12,
            "lasana_lista": 1  # Plato preparado en masa
        }
        self.lock = threading.Lock()

    def reservar(self, cocinero, producto, sincronizado=False, barrera=None):
        if sincronizado:
            with self.lock:
                return self._revisar_y_descontar(cocinero, producto)
        return self._revisar_y_descontar(cocinero, producto, barrera)

    def _revisar_y_descontar(self, cocinero, producto, barrera=None):
        # SECCION CRITICA: consulta, validacion y actualizacion.
        cantidad = self.inventario.get(producto, 0)   # Consultar
        disponible = cantidad > 0                     # Validar
        if barrera is not None:
            barrera.wait()  # Solo para demostrar la condicion de carrera
        if disponible:
            self.inventario[producto] = cantidad - 1  # Actualizar
            print(f"{cocinero}: reservo una unidad de {producto}")
            return True
        print(f"{cocinero}: no hay {producto}")
        return False


def probar(tipo, sincronizado):
    # Ambos cocineros usaran la MISMA instancia del recurso.
    recurso = InventarioBasico() if tipo == "basico" else InventarioComplejo()
    barrera = None if sincronizado else threading.Barrier(2)
    resultados = []
    lock_resultados = threading.Lock()

    def trabajo(numero):
        cocinero = f"Cocinero {numero}"
        if tipo == "basico":
            pudo_reservar = recurso.reservar(cocinero, sincronizado, barrera)
        else:
            pudo_reservar = recurso.reservar(
                cocinero, "lasana_lista", sincronizado, barrera
            )
        # Este lock solo protege la lista donde contamos resultados.
        with lock_resultados:
            resultados.append(pudo_reservar)

    print(f"\n--- {tipo.upper()} / {'CON LOCK' if sincronizado else 'SIN LOCK'} ---")
    hilos = [threading.Thread(target=trabajo, args=(i,)) for i in (1, 2)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    cantidad_final = (
        recurso.pollo if tipo == "basico"
        else recurso.inventario["lasana_lista"]
    )
    confirmadas = sum(resultados)
    print(f"Reservas confirmadas: {confirmadas}")
    print(f"Cantidad final: {cantidad_final}")
    if confirmadas > 1:
        print("PROBLEMA: dos reservas de una sola unidad")
    else:
        print("RESULTADO: no hay reserva duplicada")


if __name__ == "__main__":
    for tipo in ("basico", "complejo"):
        probar(tipo, sincronizado=False)
        probar(tipo, sincronizado=True)
