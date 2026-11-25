
import threading


class Inventario:
    # Inventario compartido del restaurante.

    def __init__(self, tipo, registrar=None, cocineros=2):
        self.tipo = tipo
        self.mutex = threading.Lock()
        self.registrar = registrar

        # Permite mostrar que otros hilos intentan entrar
        # mientras el primer hilo ocupa la sección crítica.
        self.primero_entro = threading.Event()

        self.intentos_registrados = threading.Barrier(
            cocineros, timeout=8
        )

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

            self.platos_preparados = {
                "lasana": 1
            }

    # Registrar una acción realizada por un hilo.
    def avisar(
            self, etapa, recurso,
            antes, despues, mensaje, **extra
    ):
        if self.registrar:
            self.registrar({
                "hilo": threading.current_thread().name,
                "etapa": etapa,
                "recurso": recurso,
                "antes": antes,
                "despues": despues,
                "mensaje": mensaje,
                **extra
            })

    # Consultar las unidades de un ingrediente.
    def consultar(self, ingrediente):
        if self.tipo == "basico":
            return getattr(self, ingrediente, 0)

        return self.ingredientes.get(ingrediente, 0)

    # -----------------------------------------
    # RESERVAR CON MUTEX
    # -----------------------------------------
    def reservar_con_mutex(
            self, recurso, obtener_stock, descontar
    ):
        nombre = threading.current_thread().name

        es_primero = nombre == "cocinero 1"

        if not es_primero:

            # Espera hasta que el primer cocinero
            # haya ocupado la sección crítica.
            if not self.primero_entro.wait(timeout=8):
                raise RuntimeError(
                    "El primer cocinero no entró a tiempo."
                )

            actual = obtener_stock()

            # Registrar que este hilo está esperando.
            self.avisar(
                "esperar",
                recurso,
                actual,
                actual,
                "Intentó entrar, pero el mutex está "
                "ocupado. Espera su turno."
            )

            # Coordinación para que la espera se vea
            # antes de liberar el primer acceso.
            self.intentos_registrados.wait()

        # SOLO UN HILO PUEDE ENTRAR A LA VEZ.
        with self.mutex:

            actual = obtener_stock()

            self.avisar(
                "entrar",
                recurso,
                actual,
                actual,
                "Entró a la sección crítica."
            )

            if es_primero:

                # Avisar que el primer hilo ya entró.
                self.primero_entro.set()

                # Mantener el espacio ocupado hasta
                # registrar los intentos de los demás.
                self.intentos_registrados.wait()

            # =====================================
            # SECCIÓN CRÍTICA PROTEGIDA
            # Consultar -> Validar -> Actualizar
            # =====================================

            correcto = descontar()

            actual = obtener_stock()

            self.avisar(
                "salir",
                recurso,
                actual,
                actual,
                "Terminó su proceso y liberó el mutex. "
                "El siguiente hilo puede entrar."
            )

            return correcto

    # -----------------------------------------
    # RESERVAR INGREDIENTES
    # -----------------------------------------
    def reservar_ingrediente(
            self,
            ingrediente,
            cantidad,
            con_mutex,
            barrera=None
    ):
        if con_mutex:
            return self.reservar_con_mutex(
                ingrediente,
                lambda: self.consultar(ingrediente),
                lambda: self.descontar_ingrediente(
                    ingrediente, cantidad
                )
            )

        return self.descontar_ingrediente(
            ingrediente, cantidad, barrera
        )

    def descontar_ingrediente(
            self, ingrediente, cantidad, barrera=None
    ):
        # SECCIÓN CRÍTICA:
        # consultar -> validar -> actualizar.

        disponible = self.consultar(ingrediente)

        self.avisar(
            "consultar",
            ingrediente,
            disponible,
            disponible,
            f"Consultó {disponible} unidades."
        )

        alcanza = disponible >= cantidad

        self.avisar(
            "validar",
            ingrediente,
            disponible,
            disponible,
            "Hay suficiente stock."
            if alcanza else "No alcanza el stock."
        )

        # En la versión SIN mutex,
        # esta barrera permite reproducir
        # la condición de carrera.
        if barrera is not None:
            barrera.wait()

        if alcanza:

            actual = self.consultar(ingrediente)
            nuevo = disponible - cantidad

            if self.tipo == "basico":
                setattr(self, ingrediente, nuevo)

            else:
                self.ingredientes[ingrediente] = nuevo

            duplicada = actual != disponible

            self.avisar(
                "reservar",
                ingrediente,
                actual,
                nuevo,
                "Reserva duplicada: el hilo utilizó "
                "una lectura anterior."
                if duplicada else "Ingrediente reservado.",
                exito=True,
                duplicada=duplicada
            )

            return True

        self.avisar(
            "rechazar",
            ingrediente,
            disponible,
            disponible,
            "Pedido rechazado: sin ingredientes.",
            exito=False
        )

        return False

    # -----------------------------------------
    # RESERVAR PLATOS PREPARADOS
    # -----------------------------------------
    def reservar_plato(
            self, plato, con_mutex, barrera=None
    ):
        if con_mutex:
            return self.reservar_con_mutex(
                plato,
                lambda: self.platos_preparados.get(plato, 0),
                lambda: self.descontar_plato(plato)
            )

        return self.descontar_plato(plato, barrera)

    def descontar_plato(self, plato, barrera=None):

        # SECCIÓN CRÍTICA:
        # consultar -> validar -> actualizar.

        disponible = self.platos_preparados.get(plato, 0)

        self.avisar(
            "consultar",
            plato,
            disponible,
            disponible,
            f"Consultó {disponible} platos preparados."
        )

        alcanza = disponible >= 1

        self.avisar(
            "validar",
            plato,
            disponible,
            disponible,
            "La lasaña está disponible."
            if alcanza else "No quedan lasañas."
        )

        if barrera is not None:
            barrera.wait()

        if alcanza:

            actual = self.platos_preparados.get(plato, 0)
            nuevo = disponible - 1

            self.platos_preparados[plato] = nuevo

            duplicada = actual != disponible

            self.avisar(
                "reservar",
                plato,
                actual,
                nuevo,
                "Reserva duplicada: ambos cocineros "
                "utilizaron la misma lasaña."
                if duplicada else "Lasaña preparada reservada.",
                exito=True,
                duplicada=duplicada
            )

            return True

        self.avisar(
            "rechazar",
            plato,
            disponible,
            disponible,
            "Pedido rechazado: no hay lasaña.",
            exito=False
        )

        return False
